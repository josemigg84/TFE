import json
import mysql.connector
from mysql.connector.errors import IntegrityError, InterfaceError, OperationalError
from decimal import Decimal
from logger import Logger
import traceback

class CarroceriaDBWriter:
    def __init__(self, db_config, logger=None):
        self.db_config = db_config              # configuración de la conexión a la BBDD
        self.logger = logger or Logger()        # si no se crea un logger se pasa por defecto

    # metodo para guardar logs
    def log(self, msg):
        if self.logger:
            self.logger.log(msg)
        else:
            print(msg)

    # metodo para leer un JSON y guardar el resultado en la BBDD
    def insertar_desde_json(self, json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)             # leer el fichero JSON
        except Exception as e:
            self.log(f"Error al leer JSON {json_path}: {e}")
            self.log(traceback.format_exc())
            raise  # lanzamos el error para que main.py pueda tratarlo

        try:
            conexion = mysql.connector.connect(**self.db_config)        # tratar de conectar a la BBDD. ** desempaquetar diccionario config
        except (InterfaceError, OperationalError) as e:
            self.log(f"Error de conexión a la base de datos: {e}")
            raise  # eleva el error a main.py
        except Exception as e:              # cualquier otro error genérico
            self.log(f"Error inesperado al conectar con la base de datos: {e}")
            raise  # eleva el error a main.py

        conexion.autocommit = False     # se desactiva el auto commit para realizar las transacciones de forma manual
        cursor = conexion.cursor()      # cursor para realizar insert y consultar lastrowid

        try:
            # insertar o actualizar en la tabla Carroceria
            cursor.execute("""
                INSERT INTO Carroceria (id_carroceria, modelo, pin, skid, fecha_aplicacion)    
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  modelo = VALUES(modelo),
                  pin = VALUES(pin),
                  skid = VALUES(skid),
                  fecha_aplicacion = VALUES(fecha_aplicacion)
            """, (
                data["id_carroceria"],
                data.get("modelo"),
                data.get("pin"),
                data.get("skid"),
                data.get("fecha_aplicacion"),
            ))
            # insertar o actualizar en la tabla Analisis
            cursor.execute("""
                INSERT INTO Analisis (id_carroceria, fecha_hora_analisis)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                  id_analisis = LAST_INSERT_ID(id_analisis)  
            """, (
                data["id_carroceria"],
                data["analisis"].get("fecha_hora")
            ))
            id_analisis = cursor.lastrowid      # id del último análisis, se usa en el siguiente insert

            # insertar o actualizar en la tabla Resultado
            for resultado in data["analisis"]["resultados"]:
                cursor.execute("""
                    INSERT INTO Resultado (id_analisis, id_elemento, resultado)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    resultado = VALUES(resultado)
                """, (
                    id_analisis,
                    resultado["id_elemento"],
                    bool(resultado["resultado"])
                ))
                id_resultado = cursor.lastrowid    # id del último resultado, se usa en el siguiente insert

                # insertar en la tabla Segmento_Fallo
                for seg in resultado.get("segmentos", []):
                    cursor.execute("""
                        INSERT INTO Segmento_Fallo (id_resultado, porcent_inicio, porcent_fin)
                        VALUES (%s, %s, %s)
                    """, (
                        id_resultado,
                        Decimal(str(seg["inicio"])),
                        Decimal(str(seg["fin"]))
                    ))

            # si se ha llegado aquí, es que no hay error y los datos se han insertado correctamente
            conexion.commit()   # se confirma con commit manual
            self.log(f"Datos insertados correctamente desde {json_path}")

        except IntegrityError as e:
            conexion.rollback()             # si hay error de integridad se deshacen los cambios
            if "Duplicate entry" in str(e):
                self.log(f"ID de carrocería duplicado: {data['id_carroceria']} en {json_path}")
            else:
                self.log(f"Error de integridad: {e}")
                self.log(traceback.format_exc())            # se guarda en el log el traceback del error

        except Exception as e:
            conexion.rollback()          # si hay error general se deshacen los cambios
            self.log(f"Error general al insertar {json_path}: {e}")
            self.log(traceback.format_exc())
            raise       # elevar el error a main.py

        finally:
            cursor.close()          # se cierra el cursor
            conexion.close()        # se cierra la conexión

import json
import mysql.connector
from mysql.connector.errors import IntegrityError, InterfaceError, OperationalError
from decimal import Decimal
from logger import Logger
import traceback

class CarroceriaDBWriter:
    def __init__(self, db_config, logger=None):
        self.db_config = db_config
        self.logger = logger or Logger()

    def log(self, msg):
        if self.logger:
            self.logger.log(msg)
        else:
            print(msg)

    def insertar_desde_json(self, json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.log(f"Error al leer JSON {json_path}: {e}")
            self.log(traceback.format_exc())
            raise  # lanzamos el error para que main.py pueda tratarlo

        try:
            conn = mysql.connector.connect(**self.db_config)
        except (InterfaceError, OperationalError) as e:
            self.log(f"Error de conexión a la base de datos: {e}")
            raise  # propaga error a main.py
        except Exception as e:
            self.log(f"Error inesperado al conectar con la base de datos: {e}")
            raise

        conn.autocommit = False
        cursor = conn.cursor()

        try:
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

            cursor.execute("""
                INSERT INTO Analisis (id_carroceria, fecha_hora_analisis)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE
                  id_analisis = LAST_INSERT_ID(id_analisis)  
            """, (
                data["id_carroceria"],
                data["analisis"].get("fecha_hora")
            ))
            id_analisis = cursor.lastrowid

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
                id_resultado = cursor.lastrowid

                for seg in resultado.get("segmentos", []):
                    cursor.execute("""
                        INSERT INTO Segmento_Fallo (id_resultado, porcent_inicio, porcent_fin)
                        VALUES (%s, %s, %s)
                    """, (
                        id_resultado,
                        Decimal(str(seg["inicio"])),
                        Decimal(str(seg["fin"]))
                    ))

            conn.commit()
            self.log(f"Datos insertados correctamente desde {json_path}")

        except IntegrityError as e:
            conn.rollback()
            if "Duplicate entry" in str(e):
                self.log(f"ID de carrocería duplicado: {data['id_carroceria']} en {json_path}")
            else:
                self.log(f"Error de integridad: {e}")
                self.log(traceback.format_exc())

        except Exception as e:
            conn.rollback()
            self.log(f"Error general al insertar {json_path}: {e}")
            self.log(traceback.format_exc())
            raise

        finally:
            cursor.close()
            conn.close()

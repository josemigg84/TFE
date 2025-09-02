use TFG;


/* CREACION DE TABLAS */
/* Tabla de Carrocerías */

CREATE TABLE Carroceria (
    id_carroceria INT NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    pin VARCHAR(50),
    skid VARCHAR(50),
    fecha_aplicacion TIMESTAMP,
    PRIMARY KEY (id_carroceria)
);

/* Tabla de Cámaras */
CREATE TABLE Camara (
    id_camara SERIAL NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_camara)
);

/* Tabla base de Elementos inspeccionados */
CREATE TABLE Elemento (
    id_elemento SERIAL NOT NULL,
    id_camara BIGINT UNSIGNED  NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    tipo_elemento ENUM('cordon', 'tapon', 'salpicadura') NOT NULL,
    PRIMARY KEY (id_elemento)
);

/* Tabla de Análisis */
CREATE TABLE Analisis (
    id_analisis SERIAL NOT NULL,
    id_carroceria INT NOT NULL,
    fecha_hora_analisis TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_analisis)
);

/* Resultados de cada elemento inspeccionado en un análisis */
CREATE TABLE Resultado (
    id_resultado SERIAL NOT NULL,
    id_analisis BIGINT UNSIGNED  NOT NULL,
    id_elemento BIGINT UNSIGNED  NOT NULL,
    resultado BOOLEAN NOT NULL,
    PRIMARY KEY (id_resultado)
);

/* Segmentos con fallo para elementos lineales (cordones) */
CREATE TABLE Segmento_Fallo (
    id_segmento SERIAL NOT NULL,
    id_resultado BIGINT UNSIGNED  NOT NULL,
    porcent_inicio DECIMAL(7,6) NOT NULL,
    porcent_fin DECIMAL(7,6) NOT NULL,
    PRIMARY KEY (id_segmento)
);

/* CLAVES AJENAS*/

ALTER TABLE Elemento
  ADD CONSTRAINT fk_el_ca FOREIGN KEY (id_camara) REFERENCES Camara (id_camara) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT uq_el_ca UNIQUE (id_camara, nombre);   /* controlar que no se duplique el nombre de elemento, por seguridad*/

ALTER TABLE Analisis
  ADD CONSTRAINT fk_an_ca FOREIGN KEY (id_carroceria) REFERENCES Carroceria (id_carroceria) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT uq_an_ca UNIQUE (id_carroceria, fecha_hora_analisis);   /* controlar que no hay más de un analisis con la misma carrocería y la misma fecha, por si lee varias veces el mismo json*/

ALTER TABLE Resultado
  ADD CONSTRAINT fk_re_an FOREIGN KEY (id_analisis) REFERENCES Analisis (id_analisis) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_re_ce FOREIGN KEY (id_elemento) REFERENCES Elemento (id_elemento) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT uq_re_el UNIQUE (id_analisis, id_elemento);   /* controlar que no solo hay un elmento igual por análisis*/

ALTER TABLE Segmento_Fallo
  ADD CONSTRAINT fk_sf_re FOREIGN KEY (id_resultado) REFERENCES Resultado (id_resultado) ON DELETE CASCADE ON UPDATE CASCADE;

/* INDICES*/

CREATE INDEX idx_carroceria_pin ON Carroceria(pin);


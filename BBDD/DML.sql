/* DDL - inserciones de valores fijos de configuracion para camaras y cordones inspeccionados*/
insert into Camara (nombre) VALUES
('Camara1_Izq'),
('Camara2_Der');


insert into Elemento (id_camara, nombre, tipo_elemento) VALUES
(1, 'cord1_mod1_izq', 'cordon'),
(1, 'cord2_mod1_izq', 'cordon'),
(1, 'cord3_mod1_izq', 'cordon'),
(2, 'cord1_mod1_der', 'cordon'),
(2, 'cord2_mod1_der', 'cordon'),
(2, 'cord3_mod1_der', 'cordon'),
(1, 'cord1_mod2_izq', 'cordon'),
(1, 'cord2_mod2_izq', 'cordon'),
(1, 'cord3_mod2_izq', 'cordon'),
(1, 'cord4_mod2_izq', 'cordon'),
(2, 'cord1_mod2_der', 'cordon'),
(2, 'cord2_mod2_der', 'cordon'),
(2, 'cord3_mod2_der', 'cordon'),
(2, 'cord4_mod2_der', 'cordon');


begin;
-- creacion de schema 
create schema if not exists operacional;

--------------------------------------
/* Seccion: creacion de tablas*/ 
------------------------------------

-- Tabla auxuliar: cat_pais (con la fk garantiza que la ciudad pertenezca al pais indicado)
create table operacional.cat_pais (
id_pais serial primary key,
nom_pais varchar(100) not null
);

-- Tabla auxuliar: cat_ciudad
create table operacional.cat_ciudad (
id_ciudad serial primary key,
nom_ciudad varchar(100) not null,
pais_id int not null,
constraint fk_ciudad_pais foreign key (pais_id) references operacional.cat_pais(id_pais),
constraint unique_ciudad_pais unique (id_ciudad, pais_id)
);

------------------------------------------------------------
-- Tabla: pacientes
create table operacional.pac_registro (
id_pac serial primary key,
tip_doc varchar(10) not null,
num_doc_hash varchar(64) not null unique,
fec_nac date not null,
genero varchar(10) not null,
ciudad_res_id int not null,
tip_aseguradora varchar(50) not null,
id_eps int not null,
estrato_socioec int not null,
fec_primer_atencion date not null,
activo boolean not null default true,
constraint fk_pac_ciudad foreign key (ciudad_res_id) references operacional.cat_ciudad(id_ciudad)
);


-- Tabla: sedes hospitalarias (conservamos id_ciudad & id_pais como campos del origen y evitamos asociar una ciudad con otro pais)
create table operacional.red_sedes (
id_sede serial primary key,
nom_sede varchar (150) not null,
tip_sede varchar (50) not null,
ciudad_id int not null,
pais_id int not null,
cap_camas_gen int not null default 0,
cap_camas_uci int not null default 0,
cap_camas_cirugia int not null default 0,
cap_camas_urg int not null default 0,
nivel_complejidad varchar (50) not null,
constraint fk_sede_ciudad foreign key (ciudad_id, pais_id) references operacional.cat_ciudad(id_ciudad, pais_id)
);


-- Tabla: medicos (sede_id identifica la sede asociada a la asignacion al medico sin imponer que sea la misma del encuentro)
create table operacional.med_planta (
id_med serial primary key,
esp_principal varchar(100) not null,
esp_secundaria varchar(100),
sede_id int not null,
fec_ingreso date not null,
tip_contrato varchar(50) not null,
jornada varchar(50) not null,
estado_activo boolean not null default true,
constraint fk_med_sede foreign key (sede_id) references operacional.red_sedes(id_sede)

);

-- Tabla: camas (ocupacion por sede, tipo de unidad y momento)
create table operacional.gcm_camas (
id_registro_cama serial primary key,
sede_id int not null,
tip_unidad varchar (50) not null,
fec_hora_registro timestamp not null,
num_camas_ocupadas int not null default 0,
num_camas_disp int not null default 0,
num_camas_mant int not null default 0,
motivo_indisponibilidad varchar(250),
constraint fk_cama_sede foreign key (sede_id) references operacional.red_sedes(id_sede)
);




-- Tabla: encuentros (sede_id identifica la sede de la atencion y cod_procedimientos pued econtener varios separados por ; o null, esp_atentida exige una especialidad para agendar)
create table operacional.hce_encuentros (
id_encuentro varchar(50) primary key,
pac_id int not null,
med_id int not null,
sede_id int not null,
fec_registro timestamp not null,
fec_inicio_atencion timestamp not null,
fec_egreso timestamp,
tip_consulta varchar(50) not null,
esp_atendida varchar(100) not null,
diag_principal_cie10 varchar(10) not null,
diag_sec1_cie10 varchar(10),
cod_procedimientos varchar(100),
vr_facturado numeric(12,2) not null,
estado_factura varchar(20) not null,
constraint fk_encuentro_pac foreign key (pac_id) references operacional.pac_registro(id_pac),
constraint fk_encuentro_med foreign key (med_id) references operacional.med_planta(id_med),
constraint fk_encuentro_sede foreign key (sede_id) references operacional.red_sedes(id_sede),
constraint unique_encuentro_pac unique (id_encuentro, pac_id) --referenciamos un encuentro y paciente
);


-- Tabla transaccional: dispensacion
/*
Cada registro representa a un medicamente y cantidad; la fk compuesta garantiza que pac_id corresponda al encuentro
*/
create table operacional.far_dispensacion (
id_dispensacion varchar(50) primary key,
encuentro_id varchar(50) not null,
pac_id int not null,
sede_id int not null,
fec_dispensacion timestamp not null,
cod_medicamento varchar(50) not null,
nom_medicamento varchar(150) not null,
cantidad int not null,
vr_unitario numeric (12,2) not null,
tip_prescripcion varchar(50) not null,
constraint fk_disp_encuentro_pac foreign key (encuentro_id, pac_id) references operacional.hce_encuentros(id_encuentro, pac_id),
constraint fk_disp_sede foreign key (sede_id) references operacional.red_sedes(id_sede)
/*se conserva sede_id como atributo independiente porque aunque el encuentro_id ya cuenta con una sede, la dispensacion puede ocurrir en una sede distinta*/
);

-- Tabla: citas
create table operacional.age_citas(
id_cita varchar(50) primary key,
pac_id int not null,
med_id int not null,
sede_id int not null,
fec_agendamiento timestamp not null,
fec_cita_programada date not null,
hra_cita_programada time not null,
hra_llegada_paciente time,
hra_inicio_atencion time,
esp_solicitada varchar(100), -- no se obliga indicar especialidad para registrar la cita
tip_cita varchar(50) not null,
estado_cita varchar(50) not null,
constraint fk_cita_pac foreign key (pac_id) references operacional.pac_registro(id_pac),
constraint fk_cita_med foreign key (med_id) references operacional.med_planta(id_med),
constraint fk_cita_sede foreign key (sede_id) references operacional.red_sedes(id_sede)

);

commit;
--rollback;
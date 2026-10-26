begin;

create role adf_lectura login;

grant usage on schema operacional to adf_lectura;

grant select on all tables in schema operacional to adf_lectura;

commit;
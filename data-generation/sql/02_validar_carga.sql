select 'cat_pais' as tabla, count(*) as registros
from operacional.cat_pais
union all
select 'cat_ciudad', count(*)
from operacional.cat_ciudad
union all
select 'red_sedes', count(*)
from operacional.red_sedes
union all
select 'med_planta', count(*)
from operacional.med_planta
union all
select 'pac_registro', count(*)
from operacional.pac_registro
union all
select 'gcm_camas', count(*)
from operacional.gcm_camas
union all
select 'hce_encuentros', count(*)
from operacional.hce_encuentros
union all
select 'far_dispensacion', count(*)
from operacional.far_dispensacion
union all
select 'age_citas', count(*)
from operacional.age_citas
order by tabla;
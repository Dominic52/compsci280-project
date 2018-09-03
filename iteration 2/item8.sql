select *
from Operators
where (first_name, family_name) = ("blob", "chat");

select *
from Operators
order by family_name, first_name ASC;

select *
from Maps
order by name;

select *
from Drones
where Mid IS NOT NULL;

select *
from Drones
where Mid IS NULL;

select Did, name, family_name, first_name
from Drones
left join Operators on Drones.Oid = Operators.Oid;

select Operators.Oid, family_name, first_name, Maps.name
from Operators
inner join Drones as j1 on Operators.Oid = j1.Oid 
inner join Maps on j1.Mid = Maps.Mid;
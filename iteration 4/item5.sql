CREATE table Operators (
  Oid int,
  first_name varchar(250) NOT NULL,
  family_name varchar(250),
  date_of_birth date NOT NULL,
  drone_license int NOT NULL,
  rescue_endorsement boolean,
  operations int,
  Primary Key(Oid)
);
CREATE table Maps (
  Mid int,
  name varchar(250),
  map varchar(250),
  Primary Key(Mid)
 );
CREATE table Drones (
  Did int,
  Oid int UNIQUE,
  Mid int,
  name varchar(250),
  class_type int,
  rescue boolean,
  Primary Key(Did),
  Foreign Key(Oid) references Operators(Oid) on delete set NULL,
  Foreign Key(Mid) references Maps(Mid) on delete set NULL
 );
 INSERT INTO Maps(Mid, name, map) VALUES (1, 'Abel Tasman', 'map_abel_tasman_3.gif'), (2, 'Ruatiti', 'map_ruatiti.gif');

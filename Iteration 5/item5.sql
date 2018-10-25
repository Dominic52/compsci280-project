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

 INSERT INTO Operators(Oid, first_name, family_name, date_of_birth, drone_license, rescue_endorsement, operations) VALUES (1, 'Operator1', NULL, '0000-00-00', 1, 0, 0);
 INSERT INTO Maps(Mid, name, map) VALUES (1, 'Abel Tasman', 'map_abel_tasman_3.gif'), (2, 'Ruatiti', 'map_ruatiti.gif');
 INSERT INTO Drones(Did, Oid, Mid, name, class_type, rescue) VALUES (1, NULL, NULL, 'idleDrone', 1, 0), (2, NULL, 1, 'resDrone', 1, 1), (3, NULL, 1, 'resDrone2', 2, 1), (4, NULL, 2, 'resDrone3', 2, 1), (5, NULL, 1, 'Drone1', 1, 0), (6, NULL, 1, 'Drone2', 2, 0), (7, NULL, 2, 'Drone3', 1, 0), (8, NULL, 2, 'Drone4', 1, 0);

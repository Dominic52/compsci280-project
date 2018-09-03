INSERT INTO Operators 
(Oid, first_name, family_name, date_of_birth, drone_license, 
rescue_endorsement, operations) 
VALUES 
  (0, "bob", "cat", "1990-05-05", 1, False, 2),
  (1, "blob", "chat", "1990-05-05", 1, False, 2),
  (2, "gud", "boye", "1990-05-05", 2, False, 2),
  (3, "better", NULL, "1990-05-05", 1, True, 5);

INSERT INTO Maps
(Mid, name, map)
VALUES
  (0, "Abel Tasman", "map_abel_tasman_3.jpg"),
  (1, "Ruatiti", "ruatiti.jpg");
  
INSERT INTO Drones
(Did, Oid, Mid, name, class_type, rescue)
VALUES
  (0, NULL, NULL, "test_drone1", 1, False),
  (1, NULL, NULL, "test_drone2", 2, False),
  (2, NULL, NULL, "test_drone3", 2, True),
  (3, 1, 0, "test_drone4", 1, False),
  (4, 2, 1, "test_drone5", 2, True);
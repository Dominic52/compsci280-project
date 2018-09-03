SET SQL_SAFE_UPDATES = 0;

UPDATE Operators 
SET drone_license = 2, rescue_endorsement = False, operations = 6
WHERE Oid = 0;

UPDATE Operators
SET rescue_endorsement = True
WHERE operations >= 5;

UPDATE Drones
SET Oid = 3, Mid = 0
WHERE Did = 1;

DELETE FROM Operators
WHERE Oid = 3;

DELETE FROM Maps
WHERE name = "Abel Tasman";
class Drone(object):
    """ Stores details on a drone. """

    def __init__(self, name, class_type=1, rescue=False):
        self.id = 0
        self.name = name
        self.class_type = class_type
        self.rescue = rescue
        self.operator = None


class DroneAction(object):
    """ A pending action on the DroneStore. """

    def __init__(self, drone, operator, commit_action):
        self.drone = drone
        self.operator = operator
        self.messages = []
        self._commit_action = commit_action
        self._committed = False

    def add_message(self, message):
        """ Adds a message to the action. """
        self.messages.append(message)

    def is_valid(self):
        """ Returns True if the action is valid, False otherwise. """
        return len(self.messages) == 0

    def commit(self):
        """ Commits (performs) this action. """
        if self._committed:
            raise Exception("Action has already been committed")

        self._commit_action(self.drone, self.operator)
        self._committed = True


class DroneStore(object):
    """ DroneStore stores all the drones for DALSys. """

    def __init__(self, conn=None):
        self._drones = {}
        self._last_id = 0
        self._conn = conn

    def add(self, drone):
        """ Adds a new drone to the store. """
        if drone.name in self._drones:
            raise Exception('Drone already exists in store')
        else:
            self._last_id += 1
            drone.id = self._last_id
            self._drones[drone.id] = drone

    def addDrones(self, args):
        cursor = self._conn.cursor()

        # Rescue string, appended with 'rescue ' if drone being added is rescue drone, blank otherwise
        rescue = ''

        # Checks if drone is in store
        query = 'SELECT COUNT(*) FROM Drones WHERE name = %s' % (args[0])
        cursor.execute(query)
        count = cursor.fetchall()[0][0]

        # If rows are returned from name query, abort transaction
        if count != 0:
            raise Exception('Drone name already exists in store')
        else:
            # Drone is not in store
            # Get highest ID and generate next unique drone ID
            cursor.execute('SELECT MAX(Did) FROM Drones')
            maxID = cursor.fetchall()[0][0]
            newID = maxID + 1

            # Insert new drone into database
            query = 'INSERT INTO Drones (Did, Oid, Mid, name, class_type, rescue) VALUES (%d, NULL, NULL, %s, %d, %d)' % (newID, args[
                0], args[1], args[2])
            cursor.execute(query)

            # Appends 'rescue ' to confirmation print string
            if args[2] == 1:
                rescue = 'rescue '

            print("Added " + rescue + "drone with ID %.4d" % newID)
            self._conn.commit()

        cursor.close()

    def remove(self, drone):
        """ Removes a drone from the store. """
        if not drone.id in self._drones:
            raise Exception('Drone does not exist in store')
        else:
            del self._drones[drone.id]

    def removeDrones(self, arg):
        """ Removes drone with args = Did from database """
        cursor = self._conn.cursor()

        # Queries database to see if drone ID exists
        query = "SELECT COUNT(*) FROM Drones WHERE Did = %d" % arg
        cursor.execute(query)
        result = cursor.fetchall()

        # If it does, execute delete query
        if result[0][0] == 1:
            query = "DELETE FROM Drones WHERE Did = %d" % arg
            cursor.execute(query)
            self._conn.commit()
            print("Drone removed")
        else:
            # Else raise unknown drone error
            raise Exception("Unknown drone")

        cursor.close()

    def get(self, id):
        """ Retrieves a drone from the store by its ID. """
        if not id in self._drones:
            return None
        else:
            return self._drones[id]

    def list_all(self):
        """ Lists all the drones in the system. """
        for drone in self._drones:
            yield drone

    def listDrones(self, args):
        cursor = self._conn.cursor()
        query = ''

        # Creates query string based on user arguments
        if len(args) != 0:
            argQuery = 'WHERE '
            try:
                if args[0][1] == 'r':
                    argQuery += 'rescue = true'
                elif args[0][1] == 'c':
                    num = args[0].split('=')
                    if num[1] == '1':
                        argQuery += 'class_type = 1'
                    elif num[1] == '2':
                        argQuery += 'class_type = 2'
                    else:
                        e = "Unknown drone class " + str(num[1])
                        raise Exception(e)
                if len(args) == 2:
                    if args[1][1] == 'r':
                        argQuery += ' AND rescue = true'
                    elif args[1][1] == 'c':
                        num = args[1].split('=')
                        if num[1] == '1':
                            argQuery += ' AND class_type = 1'
                        elif num[1] == '2':
                            argQuery += ' AND class_type = 2'
                        else:
                            e = "Unknown drone class " + str(num[1])
                            raise Exception(e)
                query = 'SELECT Did, name, class_type, rescue, first_name FROM Drones LEFT JOIN Operators on Drones.Oid = Operators.Oid ' + \
                    argQuery + ' ORDER BY Did'
            except Exception as error:
                raise Exception(error)

        else:
            # Default list method with no arguments returns all drones
            query = 'SELECT Did, name, class_type, rescue, first_name FROM Drones LEFT JOIN Operators on Drones.Oid = Operators.Oid ORDER BY Did'

        cursor.execute(query)

        # Loops cursor row tuples and creates drone object with display format conversions
        for (did, name, class_type, rescue, operator) in cursor:
            drone = Drone(name, class_type, rescue)
            drone.id = did
            drone.operator = operator

            if drone.class_type == 1:
                drone.class_type = 'One'
            else:
                drone.class_type = 'Two'
            if drone.rescue == True:
                drone.rescue = 'Yes'
            else:
                drone.rescue = 'No'
            if drone.operator == None:
                drone.operator = '<none>'
            yield drone
        cursor.close()

    def validationError(self, string):
        # Helper function for any validation checks with generic 'Do you want to continue' user overrides
        print("Validation errors:")
        print(string)
        while True:
            print("Do you want to continue [Y/n]?")
            userRes = raw_input().lower().strip()
            if userRes == 'y' or userRes == '':
                break
            elif userRes == 'n':
                raise Exception("Allocation Cancelled")

    def allocate(self, drone, operator):
        """ Starts the allocation of a drone to an operator. """
        action = DroneAction(drone, operator, self._allocate)
        if drone.rescue == True:
            if operator.rescue_endorsement == False:
                action.add_message("Operator does not have rescue endorsement")
        if drone.class_type == 2:
            if operator.drone_license != 2:
                action.add_message(
                    "Operator does not have correct drone license")
        if operator.drone != None:
            action.add_message("Operator can only control one drone")

        return action

    def allocateDrones(self, args):
        """Allocates drone to operator and saves to database"""
        cursor = self._conn.cursor()

        # Queries database to see if drone ID is valid
        query = 'SELECT Did, name, class_type, rescue, first_name FROM Drones LEFT JOIN Operators on Drones.Oid = Operators.Oid WHERE Did = %d' % args[
            0]
        cursor.execute(query)
        result = cursor.fetchall()

        # Valid drone check from query result
        if len(result) != 1:
            raise Exception("Unknown drone")

        else:  # If query returns one and only one drone, drone is valid
            drone = result[0]

            # Validation error if drone already has an operator allocated
            # Does not show this error message if drone has no operator
            if drone[4] != None:
                errorString = "- Drone already allocated to " + drone[4]

                # Calls validationError to ask user if they want to overwrite drone's already allocated operator
                # If user replies with 'N', aborts allocation
                self.validationError(errorString)

            ### OPERATOR VALIDATION TESTS ###
            # Run validation tests on operator specified
            query = 'SELECT Oid, first_name, drone_license FROM Operators WHERE first_name = %s' % args[
                1]

            cursor.execute(query)
            result = cursor.fetchall()

            # Query should return one and only one valid operator OR no operators at all
            # If multiple operators are returned, means first_name has duplicate entries which this vague assignment did not specify for
            if len(result) == 0:    # No operators with name exists in database
                while True:
                    print(
                        "Operator does not exist, do you want to add operator [Y/n]?")
                    userRes = raw_input().lower().strip()
                    if userRes == 'y' or userRes == '':
                        break
                    elif userRes == 'n':
                        raise Exception("Allocation Cancelled")

                # Queries operator table for max Oid
                cursor.execute('SELECT MAX(Oid) FROM Operators')

                maxID = cursor.fetchall()[0][0]
                newID = maxID + 1

                # Insert new operator into database
                query = 'INSERT INTO Operators (Oid, first_name, family_name, date_of_birth, drone_license, rescue_endorsement, operations) VALUES (%d, %s, NULL, 0000-00-00, 1, 0, 0)' % (
                    newID, args[1])
                cursor.execute(query)
                self._conn.commit()
                print("Operator " + args[1] + " has been added")

                # Updates drone with new specified operator
                query = 'UPDATE Drones SET Oid = %d WHERE Did = %d' % (
                    newID, args[0])
                cursor.execute(query)
                print("Drone allocated to " + args[1])
                self._conn.commit()

            elif len(result) == 1:  # One operator with name exists in databse

                # Saves operator(Oid, first_name, drone_license) to variable
                operator = result[0]

                ### LICENSE VALIDATION CHECKS ###
                # If drone classtype and operator license type do not match, ask user for override permission
                if drone[2] != operator[2]:
                    errorString = '- Operator does not have correct drone license'
                    self.validationError(errorString)

                try:
                    # Updates drone with new specified operator
                    query = 'UPDATE Drones SET Oid = %d WHERE Did = %d' % (
                        operator[0], args[0])

                    cursor.execute(query)
                    self._conn.commit()
                    print("Drone allocated to " + args[1])
                except:
                    raise Exception(
                        "Operator is already assigne to another drone")

            else:
                print("something funky happened. too many operators returned")

        cursor.close()

    def _allocate(self, drone, operator):
        """ Performs the actual allocation of the operator to the drone. """
        if operator.drone is not None:
            # If the operator had a drone previously, we need to clean it so it does not
            # hold an incorrect reference
            operator.drone.operator = None
        operator.drone = drone
        drone.operator = operator
        self.save(drone)

    def updateDrones(self, args):
        # Initialise
        cursor = self._conn.cursor()

        changes = ''

        # name, class_type, rescue variables from database and user respectively
        databaseVars = []
        userVars = args[1:]

        # Update flag
        updateNeeded = False

        # Query arguments stored to list before joining by comma
        queryStr = []

        # Queries database to see if drone ID is valid
        query = "SELECT name, class_type, rescue FROM Drones WHERE Did = %d" % args[0]
        cursor.execute(query)
        result = cursor.fetchall()

        # If drone ID is valid, compare existing row with update command, then execute update query
        if len(result) == 1:

            baseName = result[0][0]
            baseClass = result[0][1]
            baseRescue = result[0][2]

            databaseVars = [baseName, baseClass, baseRescue]

            for i in range(3):
                # If user did not specify a change in the variable, continue to next loop
                if userVars[i] == None:
                    continue
                else:
                    if userVars[i] != databaseVars[i]:
                        updateNeeded = True
                        if i == 0:
                            queryStr.append("name = '" + userVars[0] + "'")
                            changes = changes + ' name to ' + userVars[0]
                        elif i == 1:
                            queryStr.append("class_type = " + str(userVars[1]))
                            changes = changes + ' class to ' + str(userVars[1])
                        elif i == 2:
                            queryStr.append("rescue = " + str(userVars[2]))
                            changes = changes + \
                                ' rescue to ' + str(userVars[2])

            s = ','
            queryJoin = s.join(queryStr)
            if updateNeeded:
                query = "UPDATE Drones SET " + queryJoin + \
                    " WHERE Did = " + str(args[0])
                cursor.execute(query)
                self._conn.commit()

                print("- set" + changes)
            else:
                raise Exception("No changes detected")
        else:
            # Else raise unknown drone error
            raise Exception("Unknown drone")

        cursor.close()

    def save(self, drone):
        """ Saves the drone to the database. """
        pass    # TODO: we don't have a database yet

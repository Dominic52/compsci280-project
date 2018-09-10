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
        print(args)
        cursor = self._conn.cursor()

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

    def remove(self, drone):
        """ Removes a drone from the store. """
        if not drone.id in self._drones:
            raise Exception('Drone does not exist in store')
        else:
            del self._drones[drone.id]

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
            query = 'SELECT Did, name, class_type, rescue, first_name FROM Drones LEFT JOIN Operators on Drones.Oid = Operators.Oid ORDER BY Did'

        cursor.execute(query)
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

    def _allocate(self, drone, operator):
        """ Performs the actual allocation of the operator to the drone. """
        if operator.drone is not None:
            # If the operator had a drone previously, we need to clean it so it does not
            # hold an incorrect reference
            operator.drone.operator = None
        operator.drone = drone
        drone.operator = operator
        self.save(drone)

    def save(self, drone):
        """ Saves the drone to the database. """
        pass    # TODO: we don't have a database yet

from datetime import date


class Operator(object):
    """ Stores details on an operator. """

    def __init__(self, Oid, first, family, drone_license, res_end, oper, Did):
        self.id = Oid
        self.first_name = first
        self.family_name = family
        self.date_of_birth = None
        self.drone_license = drone_license
        self.rescue_endorsement = res_end
        self.operations = oper
        self.drone = Did
        self.drone_name = None


class OperatorAction(object):
    """ A pending action on the OperatorStore. """

    def __init__(self, operator, commit_action):
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

        self._commit_action(self.operator)
        self._committed = True


class OperatorStore(object):
    """ Stores the operators. """

    def __init__(self, conn=None):
        self._operators = {}
        self._last_id = 0
        self._conn = conn

    def add(self, operator):
        """ Starts adding a new operator to the store. """
        action = OperatorAction(operator, self._add)
        check_age = True
        if operator.first_name is None:
            action.add_message("First name is required")
        if operator.date_of_birth is None:
            action.add_message("Date of birth is required")
            check_age = False
        if operator.drone_license is None:
            action.add_message("Drone license is required")
        else:
            if check_age and operator.drone_license == 2:
                today = date.today()
                age = today.year - operator.date_of_birth.year - \
                    ((today.month, today.day) < (
                        operator.date_of_birth.month, operator.date_of_birth.day))
                if age < 20:
                    action.add_message(
                        "Operator should be at least twenty to hold a class 2 license")
        if operator.rescue_endorsement == True:
            if operator.operations < 5:
                action.add_message(
                    "Operator should have been involved in five prior rescue operations to hold a rescue drone endorsement")
        return action

    def _add(self, operator):
        """ Adds a new operator to the store. """
        if operator.id in self._operators:
            raise Exception('Operator already exists in store')
        else:
            self._last_id += 1
            operator.id = self._last_id
            self._operators[operator.id] = operator

    def remove(self, operator):
        """ Removes a operator from the store. """
        if not operator.id in self._operators:
            raise Exception('Operator does not exist in store')
        else:
            del self._operators[operator.id]

    def get(self, id):
        """ Retrieves a operator from the store by its ID or name. """
        if isinstance(id, basestring):
            for op in self._operators:
                if (op.first_name + ' ' + op.family_name) == id:
                    return op
            return None
        else:
            if not id in self._operators:
                return None
            else:
                return self._operators[id]

    def list_all(self):
        """ Lists all the _operators in the system. """
        for _operator in self._operators:
            yield _operator

    def listOperators(self, args):
        cursor = self._conn.cursor()

        # Creates query string based on user arguments
        # Default list method with no arguments returns all operators
        query = 'SELECT O.Oid, O.first_name, O.family_name, O.drone_license, O.rescue_endorsement, O.operations, Did, name FROM Operators O LEFT JOIN Drones D on O.Oid = D.Oid ORDER BY Oid'

        cursor.execute(query)

        # Loops cursor row tuples and creates drone object with display format conversions
        for (Oid, first_name, family_name, drone_license, rescue_endorsement, operations, Did, name) in cursor:
            operator = Operator(Oid, first_name, family_name,
                                drone_license, rescue_endorsement, operations, Did)
            operator.drone_name = name

            yield operator
        cursor.close()

    def save(self):
        """ Saves the store to the database. """
        pass    # TODO: we don't have a database yet

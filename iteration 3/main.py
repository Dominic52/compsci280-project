import mysql.connector
from drones import Drone, DroneStore


class Application(object):
    """ Main application wrapper for processing input. """

    def __init__(self, conn):
        self._drones = DroneStore(conn)
        self._commands = {
            'list': self.list,
            'add': self.add,
            'update': self.update,
            'remove': self.remove,
            'allocate': self.allocate,
            'help': self.help,
        }

    def main_loop(self):
        print 'Welcome to DALSys'
        cont = True
        while cont:
            val = raw_input('> ').strip().lower()
            cmd = None
            args = {}
            if len(val) == 0:
                continue

            try:
                parts = val.split(' ')
                if parts[0] == 'quit':
                    cont = False
                    print 'Exiting DALSys'
                else:
                    cmd = self._commands[parts[0]]
            except KeyError:
                print '!! Unknown command "%s" !!' % (val)

            if cmd is not None:
                args = parts[1:]
                try:
                    cmd(args)
                except Exception as ex:
                    print '!! %s !!' % (str(ex))

    def add(self, args):
        """ Adds a new drone. """
        raise Exception("Add method has not been implemented yet")

    def allocate(self, args):
        """ Allocates a drone to an operator. """
        raise Exception("Allocate method has not been implemented yet")

    def help(self, args):
        """ Displays help information. """
        print "Valid commands are:"
        print "* list [- class =(1|2)] [- rescue ]"
        print "* add 'name ' -class =(1|2) [- rescue ]"
        print "* update id [- name ='name '] [- class =(1|2)] [- rescue ]"
        print "* remove id"
        print "* allocate id 'operator'"

    def list(self, args):
        """ Lists all the drones in the system. """
        raise Exception("List method has not been implemented yet")

    def remove(self, args):
        """ Removes a drone. """
        raise Exception("Remove method has not been implemented yet")

    def update(self, args):
        """ Updates the details for a drone. """
        raise Exception("Update method has not been implemented yet")


if __name__ == '__main__':
    conn = mysql.connector.connect(user='user',
                                   password='password',
                                   host='server',
                                   database='database')
    app = Application(conn)
    app.main_loop()
    conn.close()

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
        # Initialise variables
        name = ''
        dclass = ''
        res = False  # Rescue is False by default

        argsStart = 0

        # Strips for name of drone
        for i in range(len(args)):
            if args[0][0] == "'" or args[0][0] == '"':
                name = name + ' ' + args[i]
                if not (len(args[i]) == 0) and args[i][-1] == "'":
                    argsStart = i + 1
                    break
        try:
            name = name[1:]
        except:
            pass

        # Checks for -rescue argument
        if len(args) == 3:
            if args[2] == '-rescue':
                res = 1
            else:
                res = 0

        # Recombines to form proper argument list in format [name, class, rescue]
        args = [name] + args[argsStart:]

        # Checks for name and class input errors
        if len(name) == 0:
            raise Exception("name is required")
        else:
            try:
                dclass = args[1]
                if dclass[-1] == '1':
                    dclass = 1
                elif dclass[-1] == '2':
                    dclass = 2
            except:
                raise Exception("class is required")

        # Reformatted arguments list for query
        args = [name, dclass, res]
        self._drones.addDrones(args)

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
        try:
            print 'ID\tName\t\t\tClass\tRescue\tOperator'
            for drone in self._drones.listDrones(args):
                print '%.4d\t%s\t\t%s\t%s\t%s' % (
                    drone.id, drone.name, drone.class_type, drone.rescue, drone.operator)
            if len(list(self._drones.listDrones(args))) != 0:
                print '%d drones listed' % len(
                    list(self._drones.listDrones(args)))
            else:
                raise Exception("There are no drones for this criteria")
        except Exception as error:
            raise Exception(error)

    def remove(self, args):
        """ Removes a drone. """
        raise Exception("Remove method has not been implemented yet")

    def update(self, args):
        """ Updates the details for a drone. """
        raise Exception("Update method has not been implemented yet")


if __name__ == '__main__':
    try:
        print("Connecting to UOA database...")
        conn = mysql.connector.connect(user='dyan263',
                                       password='dy002200',
                                       host='studdb-mysql.fos.auckland.ac.nz',
                                       database='stu_dyan263_COMPSCI_280_C_S2_2018',
                                       charset='utf8')
    except:
        print("Connection to UOA has failed...")
        print("Connecting to local database...")
        conn = mysql.connector.connect(user='root',
                                       password='dy002200',
                                       host='localhost',
                                       database='compsci280',
                                       charset='utf8')

    app = Application(conn)
    app.main_loop()
    conn.close()

import mysql.connector
import Tkinter as tk
import ttk

from drones import Drone, DroneStore
from operators import Operator, OperatorStore


class Application(object):
    """ Main application view - displays the menu. """

    def __init__(self, conn):
        # Initialise the stores
        self.drones = DroneStore(conn)
        self.operators = OperatorStore(conn)

        # Initialise the GUI window
        self.root = tk.Tk()
        self.root.title('Drone Allocation and Localisation')
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Add in the buttons
        drone_button = tk.Button(
            frame, text="View Drones", command=self.view_drones, width=40, padx=5, pady=5)
        drone_button.pack(side=tk.TOP)
        operator_button = tk.Button(
            frame, text="View Operators", command=self.view_operators, width=40, padx=5, pady=5)
        operator_button.pack(side=tk.TOP)
        exit_button = tk.Button(frame, text="Exit System",
                                command=quit, width=40, padx=5, pady=5)
        exit_button.pack(side=tk.TOP)

    def main_loop(self):
        """ Main execution loop - start Tkinter. """
        self.root.mainloop()

    def view_operators(self):
        """ Display the operators. """
        # Instantiate the operators window
        # Display the window and wait
        wnd = OperatorListWindow(self)
        self.root.wait_window(wnd.root)

    def view_drones(self):
        """ Display the drones. """
        wnd = DroneListWindow(self)
        self.root.wait_window(wnd.root)


class ListWindow(object):
    """ Base list window. """

    def __init__(self, parent, title):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.operators = parent.operators

        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

    def add_list(self, columns, edit_action):
        # Add the list
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.title())
        ysb = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
                            command=self.tree.yview)
        xsb = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL,
                            command=self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set
        self.tree.bind("<Double-1>", edit_action)

        # Add tree and scrollbars to frame
        self.tree.grid(in_=self.frame, row=0, column=0, sticky=tk.NSEW)
        ysb.grid(in_=self.frame, row=0, column=1, sticky=tk.NS)
        xsb.grid(in_=self.frame, row=1, column=0, sticky=tk.EW)

        # Set frame resize priorities
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

    def close(self):
        """ Closes the list window. """
        self.root.destroy()


class DroneListWindow(ListWindow):
    """ Window to display a list of drones. """

    def __init__(self, parent):
        super(DroneListWindow, self).__init__(parent, 'Drones')

        # Add the list and fill it with data
        columns = ('id', 'name', 'class', 'rescue', 'operator')
        self.add_list(columns, self.edit_drone)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Drone",
                               command=self.add_drone, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        for i in self.tree.get_children():
            self.tree.delete(i)

        listOfDrones = self.drones.listDrones('')
        for i in listOfDrones:
            self.tree.insert('', 'end', values=(
                i.id, i.name, i.class_type, i.rescue, i.operator))

    def add_drone(self):
        """ Starts a new drone and displays it in the list. """
        # Start a new drone instance
        drone = None

        # Display the drone
        self.view_drone(drone, self._save_new_drone)

    def _save_new_drone(self, drone):
        """ Saves the drone in the store and updates the list. """
        self.drones.addDrones(drone)

        self.populate_data()

    def edit_drone(self, event):
        """ Retrieves the drone and shows it in the editor. """
        # Retrieve the identifer of the drone
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the drone from the store
        allDrones = list(self.drones.listDrones(''))
        for d in allDrones:
            if d.id == item_id:
                drone = d

        # Display the drone
        self.view_drone(drone, self._update_drone)

    def _update_drone(self, drone):
        """ Saves the new details of the drone. """
        self.drones.updateDrones(drone)
        self.populate_data()

    def view_drone(self, drone, save_action):
        """ Displays the drone editor. """
        wnd = DroneEditorWindow(self, drone, save_action)
        self.root.wait_window(wnd.root)


class OperatorListWindow(ListWindow):
    """ Window to display a list of drones. """

    def __init__(self, parent):
        super(OperatorListWindow, self).__init__(parent, 'Drones')

        # Add the list and fill it with data
        columns = ('Name', 'Class', 'Rescue', 'Operations', 'Drone')
        self.add_list(columns, self.edit_operator)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Operator",
                               command=self.add_operator, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        for i in self.tree.get_children():
            self.tree.delete(i)

        listOfOperators = self.operators.listOperators('')
        for i in listOfOperators:
            if i.family_name == None:
                name = i.first_name
            else:
                name = i.first_name + ' ' + i.family_name
            if i.Did == None:
                drone = '<none>'
            else:
                drone = str(i.Did) + ' ' + i.drone_name
            self.tree.insert('', 'end', values=(
                name, i.drone_license, i.rescue_endorsement, i.operations, drone))

    def add_operator(self):
        """ Starts a new drone and displays it in the list. """
        # Start a new drone instance
        operator = None

        # Display the drone
        self.view_operator(operator, self._save_new_operator)

    def _save_new_operator(self, operator):
        """ Saves the drone in the store and updates the list. """
        self.operators.addOperators(operator)

        self.populate_data()

    def edit_operator(self, event):
        """ Retrieves the drone and shows it in the editor. """
        # Retrieve the identifer of the drone
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the drone from the store
        allOperators = list(self.operators.listOpeartors(''))
        for o in allOperators:
            if o.id == item_id:
                operator = o

        # Display the drone
        self.view_operator(operator, self._update_operator)

    def _update_operator(self, operator):
        """ Saves the new details of the drone. """
        self.operators.updateOperators(operator)
        self.populate_data()

    def view_operator(self, operator, save_action):
        """ Displays the drone editor. """
        wnd = OperatorEditorWindow(self, operator, save_action)
        self.root.wait_window(wnd.root)

####
####
####
# Editor Windows
####
####
####


class EditorWindow(object):
    """ Base editor window. """

    def __init__(self, parent, title, save_action):
        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        # Add the editor widgets
        last_row = self.add_editor_widgets()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Save",
                               command=save_action, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=last_row +
                        1, column=1, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=last_row +
                         2, column=1, sticky=tk.E)

    def add_editor_widgets(self):
        """ Adds the editor widgets to the frame - this needs to be overriden in inherited classes. 
        This function should return the row number of the last row added - EditorWindow uses this
        to correctly display the buttons. """
        return -1

    def close(self):
        """ Closes the editor window. """
        self.root.destroy()


class DroneEditorWindow(EditorWindow):
    """ Editor window for drones. """

    def __init__(self, parent, drone, save_action):
        self._drone = drone
        self._save_action = save_action
        if self._drone == None:
            title = 'Drone: <new>'
        else:
            title = 'Drone: ID' + str(self._drone.id)
        super(DroneEditorWindow, self).__init__(
            parent, title, self.save_drone)

        # If new drone, set default values
        if self._drone == None:
            # Default name
            n = ''
            # Default class
            c = 'One'

            # Default rescue
            r = 'No'
        else:
            # Drone name is displayed
            n = self._drone.name

            # Drone class is displayed
            if self._drone.class_type == 1:
                c = 'One'
            else:
                c = 'Two'

            # Rescue is displayed
            if self._drone.rescue == 0:
                r = 'No'
            else:
                r = 'Yes'

        # Name entry line init
        namevar = tk.StringVar(self.frame, value=n)
        self.nameEntry = tk.Entry(self.frame, width=40, textvariable=namevar)

        tk.Label(self.frame, text='Name:', justify=tk.LEFT).grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.nameEntry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Name drone class line init
        self.droneLicense = ttk.Combobox(
            self.frame)
        self.droneLicense['values'] = ('One', 'Two')
        self.droneLicense.set(c)
        self.droneLicense.config(width=4)
        tk.Label(self.frame, text='Drone Class:',
                 justify=tk.LEFT).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.droneLicense.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Name rescue line init
        self.rescue = ttk.Combobox(
            self.frame)
        self.rescue['values'] = ('Yes', 'No')
        self.rescue.set(r)
        self.rescue.config(width=4)
        tk.Label(self.frame, text='Rescue Drone:',
                 justify=tk.LEFT).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.rescue.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

    def add_editor_widgets(self):
        """ Adds the widgets dor editing a drone. """
        return 2

    def save_drone(self):
        """ Updates the drone details and calls the save action. """
        name = "'" + self.nameEntry.get() + "'"
        dclass = self.droneLicense.get()
        res = self.rescue.get()

        if dclass == 'One':
            dclass = 1
        else:
            dclass = 2

        if res == 'Yes':
            res = 1
        else:
            res = 0

        # Prepares to add new drone
        if self._drone == None:
            self._drone = [name, dclass, res]
            self._save_action(self._drone)
            self._drone = None
        else:  # Prepares to update drone
            tempDrone = self._drone
            Did = self._drone.id
            name = name.strip("'")
            self._drone = [Did, name, dclass, res]
            self._save_action(self._drone)
            self._drone = tempDrone


class OperatorEditorWindow(EditorWindow):
    """ Editor window for operator. """

    def __init__(self, parent, operator, save_action):
        self._operator = operator
        self._save_action = save_action
        if self._operator == None:
            title = 'Operator: <new>'
        else:
            title = 'Operator: ID' + str(self._operator.Oid)
        super(OperatorEditorWindow, self).__init__(
            parent, title, self.save_operator)

        # If new operator, set default values
        if self._operator == None:
            # Default first name
            n = ''

            # Default family name
            fn = ''

            # Default class
            c = 'One'

            # Default rescue
            # r = 'No'

            # Default operations
            o = 0
        else:
            # operator name is displayed
            n = self._operator.first_name
            fn = self._operator.family_name

            # operator class is displayed
            if self._operator.drone_license == 1:
                c = 'One'
            else:
                c = 'Two'

            # Rescue is displayed
            # if self._operator.rescue_endorsement == 0:
            #     r = 'No'
            # else:
            #     r = 'Yes'

            # Operations is displayed
            o = self._operator.operations

        # Name entry line
        namevar = tk.StringVar(self.frame, value=n)
        self.nameEntry = tk.Entry(self.frame, width=40, textvariable=namevar)

        tk.Label(self.frame, text='First Name:', justify=tk.LEFT).grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.nameEntry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Family name entry line
        famnamevar = tk.StringVar(self.frame, value=fn)
        self.famnameEntry = tk.Entry(
            self.frame, width=40, textvariable=famnamevar)

        tk.Label(self.frame, text='Family Name:', justify=tk.LEFT).grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.famnameEntry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Name drone license line
        self.droneLicense = ttk.Combobox(
            self.frame)
        self.droneLicense['values'] = ('One', 'Two')
        self.droneLicense.set(c)
        self.droneLicense.config(width=4)
        tk.Label(self.frame, text='Drone License:',
                 justify=tk.LEFT).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.droneLicense.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Endorsement disabled text field
        if o < 5:
            end = 'No'
        elif o >= 5:
            end = 'Yes'
        endorsed = tk.StringVar(self.frame, value=end)
        self.endorsement = tk.Entry(
            self.frame, state='disabled', width=7, textvariable=endorsed)

        tk.Label(self.frame, text='Rescue Endorsement:', justify=tk.LEFT).grid(
            row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.endorsement.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        # Operations
        self.ops = tk.Spinbox(self.frame, from_=0, to=999, width=8,
                              command=self.updateEndorsement)
        tk.Label(self.frame, text='Number of Operations:', justify=tk.LEFT).grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.ops.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

    def updateEndorsement(self):
        if int(self.ops.get()) >= 5:
            val = 'Yes'
        elif int(self.ops.get()) < 5:
            val = 'No'

        endorsed = tk.StringVar(self.frame, value=val)
        self.endorsement = tk.Entry(
            self.frame, state='disabled', width=7, textvariable=endorsed)

        self.endorsement.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

    def add_editor_widgets(self):
        """ Adds the widgets dor editing a drone. """
        return 3

    def save_operator(self):
        """ Updates the drone details and calls the save action. """
        # name = "'" + self.nameEntry.get() + "'"
        # dclass = self.droneLicense.get()
        # res = self.rescue.get()

        # if dclass == 'One':
        #     dclass = 1
        # else:
        #     dclass = 2

        # if res == 'Yes':
        #     res = 1
        # else:
        #     res = 0

        # # Prepares to add new drone
        # if self._drone == None:
        #     self._drone = [name, dclass, res]
        #     self._save_action(self._drone)
        #     self._drone = None
        # else:  # Prepares to update drone
        #     tempDrone = self._drone
        #     Did = self._drone.id
        #     name = name.strip("'")
        #     self._drone = [Did, name, dclass, res]
        #     self._save_action(self._drone)
        #     self._drone = tempDrone


if __name__ == '__main__':

    print("Connection to UOA has failed...")
    print("Connecting to local database...")
    conn = mysql.connector.connect(user='root',
                                   password='dy002200',
                                   host='localhost',
                                   database='compsci280',
                                   charset='utf8')

    # print("Connecting to UOA database...")
    # conn = mysql.connector.connect(user='dyan263',
    #                                password='dy002200',
    #                                host='studdb-mysql.fos.auckland.ac.nz',
    #                                database='stu_dyan263_COMPSCI_280_C_S2_2018',
    #                                charset='utf8')

    app = Application(conn)
    app.main_loop()
    conn.close()

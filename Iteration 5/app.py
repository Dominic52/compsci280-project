import mysql.connector
import Tkinter as tk
import ttk
from PIL import Image

from drones import Drone, DroneStore
from operators import Operator, OperatorStore
from maps import Map, MapStore
from trackingsystem import TrackingSystem, DroneLocation


class Application(object):
    """ Main application view - displays the menu. """

    def __init__(self, conn):
        # Initialise the stores
        self.drones = DroneStore(conn)
        self.operators = OperatorStore(conn)
        self.maps = MapStore(conn)
        self.track = TrackingSystem()

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
        view_map_button = tk.Button(
            frame, text="View Maps", command=self.view_maps, width=40, padx=5, pady=5)
        view_map_button.pack(side=tk.TOP)
        allocate_drone_button = tk.Button(
            frame, text="Allocate Drone", command=self.view_allocation, width=40, padx=5, pady=5)
        allocate_drone_button.pack(side=tk.TOP)
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

    def view_maps(self):
        """ Display the maps. """
        wnd = MapWindow(self, 'Map Viewer')
        self.root.wait_window(wnd.root)

    def view_allocation(self):
        """ Displays allocation window. """
        wnd = AllocateWindow(self, 'Allocate Drone')
        self.root.wait_window(wnd.root)


class ListWindow(object):
    """ Base list window. """

    def __init__(self, parent, title):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.operators = parent.operators
        self.maps = parent.maps
        self.track = parent.track
        

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
        self.view_drone(drone, None, self._save_new_drone)

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

        # Load all maps from store and passes the assigned map along with drone
        # (Monkey implementation because the assignment brief sucks ass)
        allMaps = list(self.maps.listMaps())
        for m in allMaps:
            if drone.map == m.mid:
                assignedMap = m
                break
            else:
                assignedMap = None

        # Display the drone
        self.view_drone(drone, assignedMap, self._update_drone)

    def _update_drone(self, drone):
        """ Saves the new details of the drone. """
        self.drones.updateDrones(drone)
        self.populate_data()

    def view_drone(self, drone, assignedMap, save_action):
        """ Displays the drone editor. """
        wnd = DroneEditorWindow(self, drone, assignedMap, save_action)
        self.root.wait_window(wnd.root)


class OperatorListWindow(ListWindow):
    """ Window to display a list of operators. """

    def __init__(self, parent):
        super(OperatorListWindow, self).__init__(parent, 'Oprators')

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
        operator = None
        # Load the drone from the store
        allOperators = list(self.operators.listOperators(''))
        for o in allOperators:
            fn = o.first_name
            famn = o.family_name
            if fn == None:
                fn = ''
            if famn == None:
                famn = ''
            name = fn + ' ' + famn
            name = name.strip(' ')
            if name == item_id:
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
############################################################################################################
################################################# Editor Windows ###########################################
############################################################################################################
####
####


class EditorWindow(object):
    """ Base editor window. """

    def __init__(self, parent, title, save_action):
        # Initialise the new top-level window (modal dialog)
        
        self._parent = parent.root
        self.track = parent.track
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

    def __init__(self, parent, drone, assignedMap, save_action):
        self.track = parent.track
        self._drone = drone
        self._map = assignedMap
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

            # Unassigned map
            point = 'n/a'
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

            # Get map and generate Coordinates
            if self._map == None:
                point = 'n/a'
            else:
                ts = self.track.retrieve(self._map, self._drone)
                if ts.is_valid():
                    point = ts.position()
                    self._drone.loc = point
                    point = '(' + str(point[0]) + ', ' + str(point[1]) + ')'
                else:
                    point = 'n/a'

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

        # Map coordinates
        coords = tk.StringVar(self.frame, value=point)
        self.map = tk.Entry(self.frame, width=40,
                            textvariable=coords, state='disabled')

        tk.Label(self.frame, text='Location: ', justify=tk.LEFT).grid(
            row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.map.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

    def add_editor_widgets(self):
        """ Adds the widgets dor editing a drone. """
        return 3

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

        try:
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
        except:
            self._drone = None
            raise(Exception("Drone already in list"))


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
        numOps = tk.StringVar(self.frame, value=o)
        self.ops = tk.Spinbox(self.frame, from_=0, to=999, width=8, textvariable=numOps,
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
        first_name = "'" + self.nameEntry.get() + "'"
        family_name = "'" + self.famnameEntry.get() + "'"
        if self.droneLicense.get() == 'Two':
            drone_license = 2
        else:
            drone_license = 1

        if self.endorsement.get() == 'Yes':
            rescue_endorsement = 1
        else:
            rescue_endorsement = 0
        operations = int(self.ops.get())

        try:
            if self._operator == None:
                print("Adding new Op")
                self._operator = [first_name, family_name,
                                  drone_license, rescue_endorsement, operations]
                self._save_action(self._operator)
                self._operator = None
            else:
                print("Updating Op")
                tempOp = self._operator
                Oid = self._operator.Oid
                self._operator = [Oid, first_name, family_name,
                                  drone_license, rescue_endorsement, operations]
                self._save_action(self._operator)
                self._operator = tempOp
        except:
            self._operator == None
            raise(Exception("App go Boom"))


class MapWindow(object):
    def __init__(self, parent, title):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.operators = parent.operators
        self.maps = parent.maps
        self.track = parent.track

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

        # Map dropdown
        self.mapdropdown = ttk.Combobox(self.frame)

        # Generates map list and populates combobox
        maplist = list(self.maps.listMaps())
        values = []
        for i in range(len(maplist)):
            values.append(maplist[i].name)
        self.mapdropdown['values'] = tuple(values)
        self.mapdropdown.set(values[0])
        self.currentmap = maplist[0].filepath
        self.cmObj = maplist[0]
        self.mapdropdown.config(width=60)

        # Creates the map dropdown label and combobox
        tk.Label(self.frame, text='Map: ',
                 justify=tk.LEFT).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.mapdropdown.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Create frame and canvas
        self.imgFrame = tk.Frame(
            self.frame, width=800, height=500)
        self.imgFrame.grid(row=1, column=0, columnspan=2)
        self.imgFrame.rowconfigure(0, weight=1)
        self.imgFrame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.imgFrame, width=800, height=500)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        canvasFrame = tk.Frame(self.canvas)
        self.canvas.create_window(0, 0, window=canvasFrame, anchor='nw')

        # Assign Image here
        self.img = tk.PhotoImage(file=self.currentmap)
        self.frame.im2 = self.img
        self.canvas.config(scrollregion=(0,0,self.img.width(),self.img.height()))
        self.canvas.create_image(0,0,anchor='nw',image=self.img)
        #####

        yScroll = tk.Scrollbar(self.imgFrame, orient=tk.VERTICAL)
        yScroll.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=yScroll.set)
        yScroll.grid(row=0, column=2, sticky="ns")

        xScroll = tk.Scrollbar(self.imgFrame, orient=tk.HORIZONTAL)
        xScroll.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=xScroll.set)
        xScroll.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Add the command buttons
        refresh_button = tk.Button(self.frame, text="Refresh",
                                   command=self.refresh, width=20, padx=5, pady=5)
        refresh_button.grid(in_=self.frame, row=2, column=1, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=1, sticky=tk.E)

        # Renders mock drone locations

        # First time rescue and nonrescue drone count
        self.res = 0
        self.nonres = 0

        self.resDrones = []
        self.nonresDrones = []

        allDrones = list(self.drones.listDrones(''))
        for i in allDrones:
            if i.map == self.cmObj.mid:
                if i.rescue == 1:
                    self.res += 1
                    self.resDrones.append(i)
                else:
                    self.nonres += 1
                    self.nonresDrones.append(i)

        # Update on combobox change
        def populateImage(event):
            self.canvas.delete(all)
            mapname = self.mapdropdown.get()
            for i in range(len(maplist)):
                if mapname == maplist[i].name:
                    self.currentmap = maplist[i].filepath
                    self.cmObj = maplist[i]
                    break
            self.img = tk.PhotoImage(file=self.currentmap)
            self.frame.im2 = self.img
            self.canvas.config(scrollregion=(0,0,self.img.width(),self.img.height()))
            self.canvas.create_image(0,0,anchor='nw',image=self.img)
            
            self.res = 0
            self.nonres = 0

            for i in allDrones:
                if i.map == self.cmObj.mid:
                    if i.rescue == 1:
                        self.res += 1
                    else:
                        self.nonres += 1

            self.refresh()
            

        # Binds populate image on new selection
        self.mapdropdown.bind('<<ComboboxSelected>>', populateImage)

        self.circles = []

        for i in range(self.res):
            loc = self.track.retrieve(self.cmObj, self.resDrones[i])
            if loc.is_valid():
                coords = loc.position()
                self.circles.append(self.canvas.create_oval(self.img.width()*(coords[0]/100.0)-20, self.img.height()*(coords[1]/100.0)-20, self.img.width()*(coords[0]/100.0)+20, self.img.height()*(coords[1]/100.0)+20, fill="blue"))
                
        for i in range(self.nonres):
            loc = self.track.retrieve(self.cmObj, self.nonresDrones[i])
            if loc.is_valid():
                coords = loc.position()
                self.circles.append(self.canvas.create_oval(self.img.width()*(coords[0]/100.0)-20, self.img.height()*(coords[1]/100.0)-20, self.img.width()*(coords[0]/100.0)+20, self.img.height()*(coords[1]/100.0)+20, fill="red"))
        
    def refresh(self):
        for i in range(len(self.circles)):
            self.canvas.delete(self.circles[i])

        for i in range(self.res):
            loc = self.track.retrieve(self.cmObj, self.resDrones[i])
            if loc.is_valid():
                coords = loc.position()
                self.circles.append(self.canvas.create_oval(self.img.width()*(coords[0]/100.0)-20, self.img.height()*(coords[1]/100.0)-20, self.img.width()*(coords[0]/100.0)+20, self.img.height()*(coords[1]/100.0)+20, fill="blue"))
                
        for i in range(self.nonres):
            loc = self.track.retrieve(self.cmObj, self.nonresDrones[i])
            if loc.is_valid():
                coords = loc.position()
                self.circles.append(self.canvas.create_oval(self.img.width()*(coords[0]/100.0)-20, self.img.height()*(coords[1]/100.0)-20, self.img.width()*(coords[0]/100.0)+20, self.img.height()*(coords[1]/100.0)+20, fill="red"))

    def close(self):
        """ Closes the list window. """
        self.root.destroy()


class AllocateWindow(object):
    def __init__(self, parent, title):
        # Initialise the new top-level window (modal dialog)
        
        self._parent = parent.root
        self.track = parent.track
        self._drone = parent.drones
        self._operator = parent.operators
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        self.allDrones = list(self._drone.listDrones(''))
        self.allOps = list(self._operator.listOperators(''))

        droneListStr = []
        opListStr = []

        for i in range(len(self.allDrones)):
            string = str(self.allDrones[i].id) + ": " + self.allDrones[i].name
            droneListStr.append(string)

        for i in range(len(self.allOps)):
            opListStr.append(self.allOps[i].first_name)

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        # Drone list drop down
        self.droneListDropDown = ttk.Combobox(
            self.frame)
        self.droneListDropDown['values'] = droneListStr # ID: Name of all the drones
        self.droneListDropDown.config(width=40)
        tk.Label(self.frame, text='Drone: ',
                 justify=tk.LEFT).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.droneListDropDown.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # Operator list drop down
        self.operatorListDropDown = ttk.Combobox(
            self.frame)
        self.operatorListDropDown['values'] = opListStr # Name of all the operators
        self.operatorListDropDown.config(width=40)
        tk.Label(self.frame, text='Operator: ',
                 justify=tk.LEFT).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.operatorListDropDown.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # Entry box displaying error messages
        self.errorDisplay = tk.Text(self.frame, width=30, height=8, wrap=tk.WORD)
        self.errorDisplay.insert(tk.INSERT, "Error Messages")

        self.errorDisplay.grid(row=2, column=0, rowspan=3, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Check",
                               command=self.check, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=2, sticky=tk.E)
        add_button = tk.Button(self.frame, text="Allocate",
                               command=self.allocate, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=3, column=2, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Cancel",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=4, column=2, sticky=tk.E)

    def check(self):
        # Empty error string
        
        errString = ""

        # Get currently selected operator and drone
        currentOp = self.operatorListDropDown.get()
        currentDrone = self.droneListDropDown.get()

        # If operator or drone is not selected, do nothing
        if currentOp == "" or currentDrone == "":
            return

        # Else empty display and begin checking errors
        self.errorDisplay.delete(1.0, tk.END)

        for i in range(len(self.allDrones)):
            if str(self.allDrones[i].id) == currentDrone.split(' ')[0][:-1]:
                self.cdObj = self.allDrones[i]
                break
        for i in range(len(self.allOps)):
            if self.allOps[i].first_name == currentOp:
                self.coObj = self.allOps[i]
                break
        
        # Check if drone is already allocated
        if self.cdObj.operator != None:
            errString += "Drone is already allocated\n"

        # Check if operator already has a drone
        for i in range(len(self.allDrones)):
            if self.allDrones[i].operator == self.coObj.first_name:
                if self.allDrones[i].id != self.cdObj.id:
                    errString += "Operator already assigned to a different drone\n"
                    break
        
        # Check if operator drone license is sufficient to operator drone
        if self.cdObj.class_type == 2:
            if self.coObj.drone_license != 2:
                errString += "Operator does not have drone license to operate class 2 drone\n"

        # Check if operator has rescue endorsement for rescue drone
        if self.cdObj.rescue == 1:
            if self.coObj.rescue_endorsement != 1:
                errString += "Operator does not have rescue endorsement to operate rescue drone\n"

        self.errorDisplay.insert(tk.INSERT, errString)
        

    def allocate(self):
        #allocate Oid to specified Did
        args = [None, None]
        args[0] = self.coObj.Oid
        args[1] = self.cdObj.id
        self._drone.allocateIgnoreErr(args)

        self.errorDisplay.delete(1.0, tk.END)
        self.errorDisplay.insert(tk.INSERT, "Drone - Operator pair has been allocated")

    def close(self):
        """ Closes the editor window. """
        self.root.destroy()


if __name__ == '__main__':

    # print("Connection to UOA has failed...")
    # print("Connecting to local database...")
    # conn = mysql.connector.connect(user='root',
    #                                password='dy002200',
    #                                host='localhost',
    #                                database='compsci280',
    #                                charset='utf8')

    print("Connecting to UOA database...")
    conn = mysql.connector.connect(user='dyan263',
                                   password='dy002200',
                                   host='studdb-mysql.fos.auckland.ac.nz',
                                   database='stu_dyan263_COMPSCI_280_C_S2_2018',
                                   charset='utf8')

    app = Application(conn)
    app.main_loop()
    conn.close()

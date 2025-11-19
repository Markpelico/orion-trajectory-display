#!/usr/bin/python
# author: Raphael Clark

from Tkinter import *
import ttk
import sys
import socket
import os 
import glob
from time import sleep
from time import time
import datetime
from CircularQueue import *
#from VerticalScrolledFrame import *

# this thing holds the trick terms to pass to the trick variable server
trick_terms = {
    "UTC Seconds (s)"                : "Sim.Orion_1.NEnv.itsSTimeModel.itsSTimeOutput.TimeData.UTC_Seconds_From_Epoch",
    "ActiveConf "                 : "Sim.Orion_1.Dyn.DVehModel.State.VcMgr.ActiveConfig",
    "Geodetic Alt (m)"               : "Sim.Orion_1.Dyn.DVehModel.Output.SensorData[0].GeodAltitude",
    "CurrSegment"                : "Sim.Orion_1.Cail.VlMonitor.State.CurrentSegment",
    "Mass (kg)"                       : "Sim.Orion_1.Dyn.DVehModel.State.VState[0].Mass",
    "R_CG ECI X[Y,Z] (m)"            : "Sim.Orion_1.Dyn.DVehModel.State.VState[0].R_CG_from_ECI_in_ECI,[0], [1], [2]",
    "V_CG ECI X[Y,Z] (m)"            : "Sim.Orion_1.Dyn.DVehModel.State.VState[0].V_CG_rel_ECI_in_ECI,[0], [1], [2]",
    "A_CG ECI X[Y,Z] (m)"            : "Sim.Orion_1.Dyn.DVehModel.State.VState[0].A_CG_rel_ECI_in_ECI,[0], [1], [2]",
    "S R_CG ECI X[Y,Z] (m)"          : "Sim.Orion_1.Dyn.DVehModel.Output.SensorData[0].R_CG_from_ECI_in_ECI,[0], [1], [2]",
    "S V_CG ECI X[Y,Z] (m)"          : "Sim.Orion_1.Dyn.DVehModel.Output.SensorData[0].V_CG_rel_ECI_in_ECI,[0], [1], [2]",
    "Effector Force X[Y,Z] (N)"      : "Sim.Orion_1.Dyn.DVehModel.State.Vehicles[0].JBody.Body.collect.effector_forc,[0], [1], [2]",
    "Env Force X[Y,Z] (N)"           : "Sim.Orion_1.Dyn.DVehModel.State.Vehicles[0].JBody.Body.collect.environ_forc,[0], [1], [2]",
    "NoXmit Force X[Y,Z] (N)"        : "Sim.Orion_1.Dyn.DVehModel.State.Vehicles[0].JBody.Body.collect.no_xmit_forc,[0], [1], [2]",
    "Gravity Force ECI X[Y,Z] (m/s2)"   : "Sim.Orion_1.Dyn.DVehModel.Output.SensorData[0].Grav_CG_rel_ECI_in_ECI,[0], [1], [2]",
    "Ammonia 1 X[Y,Z] (N)"           : "Sim.Orion_1.CEV.itsCmModel.itsCmOutput.DVehEffectorData.ForceInEffFrame,[0][0], [0][1], [0][2]",
    "Ammonia 2 X[Y,Z] (N)"           : "Sim.Orion_1.CEV.itsCmModel.itsCmOutput.DVehEffectorData.ForceInEffFrame,[1][0], [1][1], [1][2]",
    "Air 1 X[Y,Z] (N)"               : "Sim.Orion_1.CEV.itsCmModel.itsCmOutput.DVehEffectorData.ForceInEffFrame,[2][0], [2][1], [2][2]",
    "Air 2 X[Y,Z] (N)"               : "Sim.Orion_1.CEV.itsCmModel.itsCmOutput.DVehEffectorData.ForceInEffFrame,[3][0], [3][1], [3][2]",
    "Urine 1 X[Y,Z] (N)"             : "Sim.Orion_1.CEV.itsCmModel.itsCmOutput.DVehEffectorData.ForceInEffFrame,[4][0], [4][1], [4][2]",
    "Urine 2 X[Y,Z] (N)"             : "Sim.Orion_1.CEV.itsCmModel.itsCmOutput.DVehEffectorData.ForceInEffFrame,[5][0], [5][1], [5][2]",
    "NonGravity Inertial X[Y,Z] (m/s2)" : "Sim.Orion_1.Dyn.DVehModel.State.A_nonGrav_CG_WRT_Inertial,[0], [1], [2]"
}

# this holds the current data from trick
trick_data = {
    "UTC Seconds (s)"                   : None,
    "ActiveConf "                       : None,
    "Geodetic Alt (m)"                  : None,
    "CurrSegment"                       : None,
    "Mass (kg)"                         : None,
    "R_CG ECI X[Y,Z] (m)"               : None,
    "V_CG ECI X[Y,Z] (m)"               : None,
    "A_CG ECI X[Y,Z] (m)"               : None,
    "S R_CG ECI X[Y,Z] (m)"             : None,
    "S V_CG ECI X[Y,Z] (m)"             : None,
    "Effector Force X[Y,Z] (N)"         : None,
    "Env Force X[Y,Z] (N)"              : None,
    "NoXmit Force X[Y,Z] (N)"           : None,
    "Gravity Force ECI X[Y,Z] (m/s2)"   : None,
    "Ammonia 1 X[Y,Z] (N)"              : None,
    "Ammonia 2 X[Y,Z] (N)"              : None,
    "Air 1 X[Y,Z] (N)"                  : None,
    "Air 2 X[Y,Z] (N)"                  : None,
    "Urine 1 X[Y,Z] (N)"                : None,
    "Urine 2 X[Y,Z] (N)"                : None,
    "NonGravity Inertial X[Y,Z] (m/s2)" : None
}

# This holds the data for the dynamic graphs, which is I believe populated once the user clicks the graph button
# Dont make too many of these, the display wont like it
trick_data_buffers = {
    "UTC Seconds (s)"                   : CircularQueue(50),
    "ActiveConf "                       : CircularQueue(50),
    "Geodetic Alt (m)"                  : CircularQueue(50),
    "CurrSegment"                       : CircularQueue(50),
    "Mass (kg)"                         : CircularQueue(50),
    "R_CG ECI X[Y,Z] (m)"               : CircularQueue(50),
    "V_CG ECI X[Y,Z] (m)"               : CircularQueue(50),
    "A_CG ECI X[Y,Z] (m)"               : CircularQueue(50),
    "S R_CG ECI X[Y,Z] (m)"             : CircularQueue(50),
    "S V_CG ECI X[Y,Z] (m)"             : CircularQueue(50),
    "Effector Force X[Y,Z] (N)"         : CircularQueue(50),
    "Env Force X[Y,Z] (N)"              : CircularQueue(50),
    "NoXmit Force X[Y,Z] (N)"           : CircularQueue(50),
    "Gravity Force ECI X[Y,Z] (m/s2)"   : CircularQueue(50),
    "Ammonia 1 X[Y,Z] (N)"              : CircularQueue(50),
    "Ammonia 2 X[Y,Z] (N)"              : CircularQueue(50),
    "Air 1 X[Y,Z] (N)"                  : CircularQueue(50),
    "Air 2 X[Y,Z] (N)"                  : CircularQueue(50),
    "Urine 1 X[Y,Z] (N)"                : CircularQueue(50),
    "Urine 2 X[Y,Z] (N)"                : CircularQueue(50),
    "NonGravity Inertial X[Y,Z] (m/s2)" : CircularQueue(50)   
}

WRITEABLE_FILES = []
TOLERANCES = {}
KILL_FLAG = False

#global trick_init_state_variables


def capture_init_state():
    client_socket_test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket_test.connect( ("localhost", 7104) )  
    src_test = client_socket_test.makefile("r")
    client_socket_test.send(b"trick.var_pause()\n")
    client_socket_test.send( b"trick.var_clear()\n" )

    terms_to_grab = ["orion_init.pos[0]", "orion_init.pos[1]", "orion_init.pos[2]" , "orion_init.vel[0]" , "orion_init.vel[1]" , "orion_init.vel[2]" , "orion_init.year", "orion_init.month", "orion_init.day", "orion_init.hour", "orion_init.minute", "orion_init.second"]
    for term in terms_to_grab:
        trick_var_test = "trick.var_add(\"" + term + "\")\n"
        client_socket_test.send(bytes(trick_var_test))
    client_socket_test.send(b"trick.var_unpause()\n")
    trick_server_data_test = src_test.readline() # all of the trick terms
    trick_init_state_variables = trick_server_data_test.split("\t") # a list of the trick data
    return trick_init_state_variables
    
#trick_init_state_variables = capture_init_state()


def show_popup_message(message, duration_ms):
    """Displays a temporary pop-up window with a message."""
    popup = Toplevel()
    popup.wm_overrideredirect(True) # Remove window decorations (optional)
    popup.geometry("+%d+%d" % (root.winfo_x() + 500, root.winfo_y() + 500)) # Position near main window
    Label(popup, text=message, padx=20, pady=10).pack()
    popup.after(duration_ms, popup.destroy)


class Trick():
    '''
    this class holds the entirety of the trick variable server setup and management, it adds things, clears things, and
    hopefully will not blow up like the holy hand grenade of antioch if you put the wrong term in it
    '''
    def __init__(self, host, port):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect( (host, port) )  
            self.src = self.client_socket.makefile("r")
            self.client_socket.send(b"trick.var_pause()\n")
            self.client_socket.send( b"trick.var_clear()\n" )

            for term in trick_terms:
                # need to handle vectors with commas
                # print(trick_terms[term])

                if trick_terms[term].find(",") != -1:
                    vector_trick_term = trick_terms[term].split(',')
                    term_x = vector_trick_term[0].strip() + vector_trick_term[1].strip()
                    term_y = vector_trick_term[0].strip() + vector_trick_term[2].strip()
                    term_z = vector_trick_term[0].strip() + vector_trick_term[3].strip()

                    trick_var_x = "trick.var_add(\""+str(term_x)+"\")\n"
                    self.client_socket.send(bytes(trick_var_x))
                    trick_var_y = "trick.var_add(\""+str(term_y)+"\")\n"
                    self.client_socket.send(bytes(trick_var_y))
                    trick_var_z = "trick.var_add(\""+str(term_z)+"\")\n"
                    self.client_socket.send(bytes(trick_var_z))   

                    # print(term_x)
                    # print(term_y)
                    # print(term_z)
                else:
                    # print(trick_terms[term])

                    # I think these just push it to the trick variable server
                    # exist = "trick.var_exists(\""+str(trick_terms[term])+"\")"
                    # a = self.client_socket.send(bytes(exist, encoding = 'utf-8'))

                    # print(exist)
                    trick_var = "trick.var_add(\""+str(trick_terms[term])+"\")\n"
                    self.client_socket.send(bytes(trick_var))
            self.client_socket.send(b"trick.var_unpause()\n")
            
            for term in trick_terms:
                if term in WRITEABLE_FILES:
                    name = term.replace(" ", "_")
                    file_name = "./graphing_data/"+name+".txt"
                    with open(file_name, 'a') as file:
                        pass # this is literally just an open then leave
        except:
            print "Trick Variable server not responding, trying again in 1 second"
            self.client_socket.close()
            sleep(1)
            self.__init__(host, port)

    # clears the variable server
    def clear(self):
        self.client_socket.send( b"trick.var_pause()\n" )
        self.client_socket.send( b"trick.var_clear()\n" )
        self.client_socket.close()

    # updates the trick terms
    def update_trick_terms(self):
        trick_server_data = self.src.readline() # all of the trick terms
       
        if trick_server_data == '':
            self.no_data = True
        else:
            self.no_data = False
    
        trick_variables = trick_server_data.split("\t") # a list of the trick data

        # print(trick_data.keys())

        trick_data_keys = list(trick_data.keys())
        #print("******************")
        #print(trick_data_keys[5])
        data_index = 0
        index = 1
        while index < len(trick_variables):
            if data_index == len(trick_data_keys):
                break
            # print(trick_data_keys[data_index])
            if trick_data_keys[data_index].find("X[Y,Z]") != -1:
                trick_data[trick_data_keys[data_index]] = str(trick_variables[index])+","+str(trick_variables[index+1])+","+str(trick_variables[index+2])

                #update the buffers
                trick_data_buffers[trick_data_keys[data_index]].enqueue(str(trick_variables[index])+","+str(trick_variables[index+1])+","+str(trick_variables[index+2]))
               
                index +=2
            else:
                trick_data[trick_data_keys[data_index]] = str(trick_variables[index])

                # update buffer
                trick_data_buffers[trick_data_keys[data_index]].enqueue(str(trick_variables[index]))
            index+=1

            data_index += 1

        # print(trick_data.keys())
        # write to the data_files
        for key, value in trick_data.items(): # assumedly var is the key and the value would be trick_data[index]
            if key in WRITEABLE_FILES:
                file_name = "./graphing_data/"+str(key.replace(" ", "_")) + ".txt"
                with open(file_name, 'a') as file:
                    file.write(str(value)+ "\n" )
                    # print("wrote to file")
        
        # print("Updated trick terms")  # Debugging print

class Tolerance_widget(Frame, object):
    '''
    This holds the tolerance class that allows you to set a tolerance on a trick term that you have set up, 
    when tripped it will turn red and display the time when tripped as well as the value when tripped
    entering a time to start checking at is also available should the user want
    '''
    def __init__(self, parent, thing, data, start_time, *args, **kwargs):
        super(Tolerance_widget,self).__init__(parent, *args, **kwargs)
    
        self.name = thing
        self.data = data
        self.tripped = "NO"
        self.start_time = start_time
        self.color = "green"
        self.trip_time = ""

        self.container = Frame(self, highlightbackground=self.color, highlightthickness=2, width = 100)
        self.container.pack(anchor=N)

        # Static label
        p2_strng = "" + self.name + " Tolerance Tripped:: "
        self.static_label = Label(self.container, text=p2_strng)
        self.static_label.grid(row = 0, column = 0, padx=1)

        # Dynamic label with fixed width
        self.dynamic_label = Label(self.container, text=self.tripped, fg=self.color, width=60, anchor=W)
        self.dynamic_label.grid(row = 0, column = 1, pady = 2)

        # Value check
        p2_strng = "" + self.name + " Tolerance Values:: "
        self.value_label = Label(self.container, text=p2_strng)
        self.value_label.grid(row = 1, column = 0, padx=1)

        # Value Check
        self.value_check = Label(self.container, text=self.data, width=60, anchor=W)
        self.value_check.grid(row = 1, column = 1, pady = 2)

        # time 
        self.time_label = Label(self.container, text="Start Time:: ")
        self.time_label.grid(row = 2, column = 0, padx=1)

        # time 
        self.time_check = Label(self.container, text=self.start_time, width=60, anchor=W)
        self.time_check.grid(row = 2, column = 1, pady = 2)

        p2_strng = "Time Tripped:: " + self.trip_time
        self.time_tripped = Label(self.container, text = p2_strng)
        self.time_tripped.grid(row = 3, column=0, padx=1)

        self.value_when_tripped = Label(self.container, text = "Value When Tripped:: NA")
        self.value_when_tripped.grid(row = 3, column=1, padx=1)

        # Red X button to remove the widget
        self.remove_button = Button(self.container, text="X", fg="red", command=self.destroy)
        self.remove_button.grid(row = 0, column = 6, padx=1)

    # updates the data to tripped for the tolerance thing
    def update_data(self, new_data):
        self.tripped = new_data
        self.dynamic_label.config(text=self.tripped, fg = "red")
        self.container.config(highlightbackground = "red")
        self.trip_time = trick_data["UTC Seconds (s)"]
        p2_strng = "Time Tripped:: " + self.trip_time
        self.time_tripped.config(fg = "green", text = p2_strng)
        p2_strng = "Value When Tripped:: " + trick_data[self.name]
        self.value_when_tripped.config(text = p2_strng)
        
class DataWidget(Frame, object):
    '''
    This is a simplistic class to hold a data_instance for a widget that holds the trick data
    '''
    def __init__(self, parent, thing, data, *args, **kwargs):
        super(DataWidget, self).__init__(parent, *args, **kwargs)
        
        self.container = Frame(self, highlightbackground="red", highlightthickness=2)
        self.container.pack(anchor=N)

        self.name = thing
        self.data = data

        # Static label
        p2_strng = "" + self.name + "::"
        self.static_label = Label(self.container, text=p2_strng)
        self.static_label.grid(row = 0, column = 0, padx=1)

        # Dynamic label with fixed width
        self.dynamic_label = Label(self.container, text=self.data, width=60, anchor=W)
        self.dynamic_label.grid(row = 0, column = 1, pady = 2)

        # Red X button to remove the widget
        self.remove_button = Button(self.container, text="X", fg="red", command=self.destroy)
        self.remove_button.grid(row = 0, column = 3, padx=1)

    # updates the data to the latest from the trick variable server
    def update_data(self, new_data):
        self.data = new_data
        self.dynamic_label.config(text=self.data)

class MAIN_DISPLAY:
    '''
    This is a method that just sets up terms for the display and creates most of the widgets 
    and sets up list objects of other classes so that when run time comes this can hold instances
    '''
    def __init__(self, options):
        root.title("ART2 Orion Vehicle Forces Display")

        self.dropdown_id = None
        self.options = options
        self.widget_list = []
        #self.graph_list = []
        self.tolerance_widget_list = []
        self.left_frame = Frame(root)
        self.left_frame.grid(row=0,column=0,sticky="NW")
        self.middle_frame = Frame(root)
        self.middle_frame.grid(row=0,column=1,sticky="NW")
        middle_frame_title = Label(self.middle_frame, text="TOLERANCES").pack()

        self.right_frame = Frame(root)
        self.right_frame.grid(row=0,column=2,sticky="NW")
        self.tolerance_expected = None
        self.tolerance_min = None
        self.tolerance_max = None
        self.tolerance_set = False
        self.tolerance_term = ""

        # Create a frame for the dropdown and data sections

        self.dropdown_frame = Frame(self.left_frame)
        self.dropdown_frame.grid(row=0, column=0, sticky="nw")

        self.data_frame = Frame(self.left_frame)
        self.data_frame.grid(row=4, column=0, sticky="n", padx = 10)
        data_frame_title = Label(self.data_frame, text="DATA").pack()

        #self.graph_frame = VerticalScrolledFrame(self.right_frame)
        #self.graph_frame.grid(row=0, column=0,sticky=NE, padx = 10)
       # graph_frame_title = Label(self.graph_frame, text="GRAPHS").pack()
        

        self.entry = Entry(self.dropdown_frame, width=24)
        self.entry.bind("<KeyRelease>", self.on_entry_key)
        self.entry.bind("<FocusIn>", self.show_dropdown)
        self.entry.grid(row=0, column=0, padx=5)

        # Create a Listbox widget for the dropdown menu
        self.listbox = Listbox(root, height=20, width=30)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        for option in self.options:
            self.listbox.insert(END, option)

        # Dropdown icon/button
        Button(self.dropdown_frame, text="DROP", command=self.show_dropdown).grid(row=0, column=1, padx=5)
        Button(self.dropdown_frame, text="SELECT_DATA", command=self.select_term).grid(row=0, column=2, padx=5)
        #Button(self.dropdown_frame, text="SELECT_GRAPH", command=self.select_graph).grid(row=0, column=3, padx=5)
        # Button(self.dropdown_frame, text="GRAPH_STATIC", command=self.add_static_graph).grid(row=1, column=1, pady=5)
        # Button(self.dropdown_frame, text = "LOG DATA TO FILE", command = self.log_data).grid(row = 1, column = 2, padx = 5,pady=10)

        #self.file_frame = Frame(self.left_frame)
        #self.file_frame.grid(row=1,column=0,sticky="NW", pady = 5)
        #Label(self.file_frame, text = "ADD_TERMS_FROM_FILE (Enter Path):: ").grid(row=0,column=0,sticky="NW")
        #self.file_entry = Entry(self.file_frame)
        #self.file_entry.grid(row=0,column=1,sticky="NW", padx= 4)
        #self.file_confirm = Button(self.file_frame, text = "FILE SELECT", command = lambda : select_file(self.file_entry.get()))
        #self.file_confirm.grid(row=0,column=2,sticky="NW")

        self.tolerance_container = Frame(self.left_frame, highlightbackground="black", highlightthickness = 2)
        self.tolerance_container.grid(row=3, column=0)
        
        self.min_frame = Frame(self.tolerance_container)
        self.min_frame.grid(row = 1, column = 0, pady = 5, sticky=W)
        Label(self.min_frame, text = "Minimum Deviance:: ").pack(side = LEFT)
        self.min_field = Entry(self.min_frame, width = 10)
        self.min_field.pack(side = LEFT)

        self.expected_frame = Frame(self.tolerance_container)
        self.expected_frame.grid(row = 1, column = 1, pady = 5)
        Label(self.expected_frame, text = "Expected Value:: ").pack(side = LEFT)
        self.expected_field = Entry(self.expected_frame)
        self.expected_field.pack(side = LEFT)
        self.expected_field.insert(0, "CURRENT")

        self.max_frame = Frame(self.tolerance_container)
        self.max_frame.grid(row = 2, column = 0, pady = 5, sticky=W)
        Label(self.max_frame, text = "Maximum Deviance:: ").pack(side = LEFT)
        self.max_field = Entry(self.max_frame, width = 10)
        self.max_field.pack(side = LEFT)

        self.selector = Button(self.tolerance_container, text = "SELECT TERM", command = self.select_term_tolerance).grid(row=2, column = 1, sticky = E)
        self.set_tolerance_b = Button(self.tolerance_container, text = "SET TOLERANCE", command = self.set_tolerance)
        self.set_tolerance_b.grid(row=2,column=2, sticky=W)

        self.selected_term = Label(self.tolerance_container, text = "SELECTED TERM:: "+self.tolerance_term).grid(row=0,column=0, sticky=W)
        self.selected_dimension = Label(self.tolerance_container, text = "SELECTED DIMENSION:: ").grid(row=0,column=1, sticky = E)
        self.dimension_selector = ttk.Combobox(self.tolerance_container, width = 3, values = ["X", "Y", "Z", "N"])
        self.dimension_selector.grid(row=0,column=2, sticky=W)

        self.time_after = Frame(self.tolerance_container)
        self.time_after.grid(row = 3, column = 0, pady = 5, sticky=E)
        Label(self.time_after, text = "Set Start Time:: ").pack(side = LEFT)
        self.time_field = Entry(self.time_after, width = 10, textvariable = "NOW")
        self.time_field.pack(side = LEFT)
        self.time_field.insert(0, "NOW")

        #self.init_state_container = Frame(self.left_frame, highlightbackground="blue", highlightthickness = 2)
        #self.init_state_container.pack(side = LEFT)
        #self.init_state_container.grid(row=2, column=0, sticky=SW)
        
        # Static label
        #self.init_state_title = Label(self.init_state_container, text="Initial State of Vehicle for Tracking (ECI)")
        #self.init_state_title.grid(row = 0, column = 0, columnspan = 3, padx=1, pady=5)

        #p2_strng = "Position Vector (X,Y,Z)(m): (" + trick_init_state_variables[1] + "," + trick_init_state_variables[2] + "," + trick_init_state_variables[3] + ")"
        #self.static_label = Label(self.init_state_container, text=p2_strng)
        #self.static_label.grid(row = 1, column = 0, columnspan = 3, padx=1, pady=5)

        # Dynamic label with fixed width
        #p2_strng = "Velocity Vx (X,Y,Z)(m/s): (" + trick_init_state_variables[4] + "," + trick_init_state_variables[5] + "," + trick_init_state_variables[6] + ")"
        #self.static_label = Label(self.init_state_container, text=(p2_strng))
        #self.static_label.grid(row = 2, column = 0, columnspan = 3, padx=1, pady=5)

        # Dynamic label with fixed width
        #p2_strng = "SGMT (Year/Month/Day Hour:Min:Sec):      " + trick_init_state_variables[7] + "/" + trick_init_state_variables[8] + "/" + trick_init_state_variables[9] + "" + trick_init_state_variables[10] + ":" + trick_init_state_variables[11] + ":" + trick_init_state_variables[12]
        #self.static_label = Label(self.init_state_container, text=p2_strng)
        #self.static_label.grid(row = 3, column = 0, columnspan=3, padx=5, pady=5)

        # Run the Tkinter event loop
        root.geometry('2000x1000')

    # adds widgets for the DataWidget
    def add_widget(self, thing, data):
        
        widget = DataWidget(self.data_frame, thing, data)
        widget.pack(pady=5)
        self.widget_list.append(widget)

    # sets a tolerance value and populates a ToleranceWidget
    def set_tolerance(self):
        a = self.expected_field.get()
        if self.expected_field.get() == "" or self.max_field.get() == "" or self.min_field.get() == "" or self.dimension_selector.get() == "":
            show_popup_message("PLEASE FILL ALL TERMS BEFORE SETING A TOLERANCE", 5000)
        else:
            try:
                if self.expected_field.get() == "CURRENT":
                    dim = self.dimension_selector.get()
                    if dim == "N":
                        self.tolerance_expected = float(trick_data[self.tolerance_term])
                    elif dim == "X":
                        self.tolerance_expected = float(trick_data[self.tolerance_term].split(",")[0])
                    elif dim == "Y":
                        self.tolerance_expected = float(trick_data[self.tolerance_term].split(",")[1])
                    elif dim == "Z":
                        self.tolerance_expected = float(trick_data[self.tolerance_term].split(",")[2])
                else:
                    self.tolerance_expected = float(self.expected_field.get())
                self.tolerance_max = float(self.max_field.get())
                self.tolerance_min = float(self.min_field.get())
                lowbound = self.tolerance_expected - self.tolerance_min
                hibound = self.tolerance_expected + self.tolerance_max
               
                TOLERANCES[data] = [self.tolerance_expected, self.tolerance_max, self.tolerance_min, self.dimension_selector.get(), self.time_field.get(), self.tolerance_term]
                #term_and_dim_name = self.tolerance_term + "(Dim: " + self.dimension_selector.get() + ")"
                new_widget = Tolerance_widget(self.middle_frame, self.tolerance_term, data, self.time_field.get())
                new_widget.pack()
                self.tolerance_widget_list.append(new_widget)
                self.time_field.delete(0, END)
                self.time_field.insert(0, "NOW")

            except Exception as e:
                print(e)
                show_popup_message("PLEASE USE FLOATING POINTS FOR TOLERANCES, or scientific notation in the form \"1.23e-4\" or \"1.23E-4\" or \"CURRENT\" for the expected value", 4000)

    # sets the Trick term you are using for tolerance
    def select_term_tolerance(self):
        self.tolerance_term = self.entry.get()
        p2_strng = "SELECTED TERM:: " + self.tolerance_term
        self.selected_term = Label(self.tolerance_container, text = p2_strng).grid(row=0,column=0, sticky=W)
        self.hide_dropdown()

    # updates the tolerances for when the value trips
    def update_tolerance(self):
        dead_tol = []
        for key, value in TOLERANCES.items():
            if value[4] == "NOW" or value[4] >= trick_data["UTC Seconds (s)"]:
                if value[3] == "N":
                    data = float(trick_data.get(value[5]))
                    if data > value[0] + value[1]:
                        valsAdd = value[0]+value[1]
                        p2_strng = "DATA VALUE " + str(value[5]) + " breached MAX set tolerance of " + str(valsAdd) + " and reached " + str(data)
                        show_popup_message(p2_strng, 3000)
                        dead_tol.append(key)
                        for w in self.tolerance_widget_list:
                            if w.data == key:
                                w.update_data("YES")                 
                    if data < value[0] - value[2]:
                        valsAdd = value[0]+value[2]
                        p2_strng = "DATA VALUE " + value[5] + " breached MAX set tolerance of " + str(valsAdd) + " and reached " + str(data)
                        show_popup_message(p2_strng, 3000)
                        dead_tol.append(key) 
                        for w in self.tolerance_widget_list:
                            if w.data == key:
                                w.update_data("YES")                 
                elif value[3] == "X":
                    data = float(trick_data.get(value[5]).split(',')[0])
                    if data > value[0] + value[1]:
                        valsAdd = value[0]+value[1]
                        p2_strng = "DATA VALUE " + value[5] + " breached MAX set tolerance of " + str(valsAdd) + " and reached " + str(data)
                        show_popup_message(p2_strng, 3000)
                        dead_tol.append(key)
                        for w in self.tolerance_widget_list:
                            if w.data == key:
                                w.update_data("YES")                                         
                    if data < value[0] - value[2]:
                        valsAdd = value[0]+value[2]
                        p2_strng = "DATA VALUE " + value[5] + " breached MAX set tolerance of " + str(valsAdd) + " and reached " + str(data)
                        show_popup_message(p2_strng, 3000)
                        dead_tol.append(key) 
                        for w in self.tolerance_widget_list:
                            if w.data == key:
                                w.update_data("YES")                                                       
                elif value[3] == "Y":
                    data = float(trick_data.get(value[5]).split(',')[1])
                    if data > value[0] + value[1]:
                        valsAdd = value[0]+value[1]
                        p2_strng = "DATA VALUE " + value[5] + " breached MAX set tolerance of " + str(valsAdd) + " and reached " + str(data)
                        show_popup_message(p2_strng, 3000)
                        dead_tol.append(key)
                        for w in self.tolerance_widget_list:
                            if w.data == key:
                                w.update_data("YES")                                         
                    if data < value[0] - value[2]:
                        valsAdd = value[0]+value[2]
                        p2_strng = "DATA VALUE " + value[5] + " breached MAX set tolerance of " + str(valsAdd) + " and reached " + str(data)
                        show_popup_message(p2_strng, 3000)
                        dead_tol.append(key)
                        for w in self.tolerance_widget_list:
                            if w.data == key:
                                w.update_data("YES")                                               
                elif value[3] == "Z":
                    data = float(trick_data.get(value[5]).split(',')[2])
                    if data > value[0] + value[1]:
                        valsAdd = value[0]+value[1]
                        p2_strng = "DATA VALUE " + value[5] + " breached MAX set tolerance of " + str(valsAdd) + " and reached " + str(data)
                        show_popup_message(p2_strng, 3000)
                        dead_tol.append(key)
                        for w in self.tolerance_widget_list:
                            if w.data == key:
                                w.update_data("YES")                                         
                    if data < value[0] - value[2]:
                        valsAdd = value[0]+value[2]
                        p2_strng = "DATA VALUE " + value[5] + " breached MAX set tolerance of " + str(valsAdd) + " and reached " + str(data)
                        show_popup_message(p2_strng, 3000)
                        dead_tol.append(key) 
                        for w in self.tolerance_widget_list:
                            if w.data == key:
                                w.update_data("YES")                                                        
                else:
                    continue
        for d in dead_tol:
            try: 
                TOLERANCES.pop(key)
            except:
                p2_strng = "Popping key: " + str(key) + "resulted in error! Likely not in dictionary of dead toleracnes anymore. Func: update_tolerance"
                print p2_strng

    # updates the Data Widgets with new Data from the Trick Variable Server
    def update_widgets(self):
        for widget in self.widget_list:
            if widget.winfo_exists():
                data = trick_data[widget.name]
                if data.find(",") != -1:
                    t_data = trick_data[widget.name].split(",")
                    for i, d in enumerate(t_data):
                        t_data[i] = str(round(float(d), 4))
                    data = str(t_data[0])+","+str(t_data[1])+","+str(t_data[2])
                else:
                    data = str(data)              

                widget.update_data(data)

    # A callback function for when a term is selected in the custom entry box
    def select_term(self):
        key = self.entry.get()
        if key in trick_data:
            new_data = trick_data[key]
            self.add_widget(key, new_data)
        else:
            print("Key "+key+" not found in trick_data")
        self.hide_dropdown()
        

    # select callback for entry widget
    def on_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_option = self.listbox.get(selected_index)
            self.entry.delete(0, END)
            self.entry.insert(0, selected_option)

    # on a key entry, it is searchable, just typ
    def on_entry_key(self, event):
        typed_value = event.widget.get().strip().lower()
        if not typed_value:
            # If the entry is empty, display all options
            self.listbox.delete(0, END)
            for option in self.options:
                self.listbox.insert(END, option)
        else:
            # Filter options based on the typed value
            self.listbox.delete(0, END)
            filtered_options = [option for option in self.options if option.lower().startswith(typed_value)]
            for option in filtered_options:
                self.listbox.insert(END, option)
        self.show_dropdown()

    # shows the Entry Dropdown
    def show_dropdown(self, event=None):
        self.listbox.place(in_=self.entry, x=0, rely=1, relwidth=1.0, anchor="nw")
        self.listbox.lift()

        # Show dropdown for 2 seconds
        if self.dropdown_id:  # Cancel any old events
            self.listbox.after_cancel(self.dropdown_id)
        self.dropdown_id = self.listbox.after(4000, self.hide_dropdown)

    # hides the Dropdown
    def hide_dropdown(self):
        self.listbox.place_forget()
    
    # a function to log the data to a file
    def log_data(self):
        log_name = self.entry.get()
        WRITEABLE_FILES.append(log_name)
        if "UTC Seconds (s)" not in WRITEABLE_FILES:
            WRITEABLE_FILES.append("UTC Seconds (s)")

def on_closing():
    end = time()

    #print('Destroyed after % d seconds' % (end-start))

    #for f in files:
    #    os.remove(f)

    root.destroy()

# selects a file for more trick terms, a little iffy right now
def select_file(file_name):
    new_terms = []
    # try:

    KILL_FLAG = True

    with open(file_name, 'r') as file:
        for line in file:
            new_trick_terms = line.split(":")
            for term in new_trick_terms:
                term = term.strip()
            new_terms.append([new_trick_terms[0], new_trick_terms[1]])
    # except Exception as e:
    # print(f"error parsing file {e}")
    #print("destroying and restarting display")
    trick_var_server.clear()

    sleep(1)
    root.destroy()

    for term in new_terms:
        trick_terms[term[0]] = term[1]
        trick_data[term[0]] = None
        trick_data_buffers[term[0]] = CircularQueue(50)
    
    KILL_FLAG = False


    main()




# the main thing
def main():
    global start 
    start = time()

    # Create the main window
    global root
    root = Tk()

    global options 
    options = trick_data.keys()
    global display 
    display = MAIN_DISPLAY(options)

    global trick_var_server 
    trick_var_server = Trick("192.168.121.35", 7108)

    #global trick_init_state_variables

    
    #trick_var_server = Trick("192.168.121.35", 7108)


    root.protocol("WM_DELETE_WINDOW", on_closing)

    # lastTime = datetime.datetime.now()
    while True:
        if KILL_FLAG:
            break
        root.update()
        display.update_widgets()
        period = datetime.datetime.now() 
        # if (period - lastTime).total_seconds() >= 5:
        #     print(period)
        #     display.update_dynamic_graphs()
        #     lastTime = period
        display.update_tolerance()
        trick_var_server.update_trick_terms()

    root.mainloop()

if __name__ == "__main__":
    main() # Call the main function
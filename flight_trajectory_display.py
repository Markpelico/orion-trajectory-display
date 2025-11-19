#!/usr/bin/env python
"""
Flight Trajectory Display for NASA Trick Simulation
Connects to Trick Variable Server and plots Orion vehicle trajectory in real-time
Author: Generated for NASA Trick Project
"""

import socket
import sys
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for better integration
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import deque
import time

# Python 2/3 compatibility
try:
    import Tkinter as tk
    from Tkinter import *
    import ttk
except ImportError:
    import tkinter as tk
    from tkinter import *
    from tkinter import ttk


class TrickVariableClient:
    """
    Client to connect to Trick Variable Server and retrieve simulation data.
    """
    def __init__(self, host="localhost", port=7108):
        """
        Initialize connection to Trick Variable Server.
        
        Args:
            host (str): Hostname or IP address of the Trick simulation
            port (int): Port number for the variable server (default: 7108)
        """
        self.host = host
        self.port = port
        self.client_socket = None
        self.src = None
        self.connected = False
        self.no_data = False
        
        # Data storage
        self.position = [0.0, 0.0, 0.0]  # [X, Y, Z] in meters (ECI frame)
        self.velocity = [0.0, 0.0, 0.0]  # [X, Y, Z] in m/s (ECI frame)
        self.acceleration = [0.0, 0.0, 0.0]  # [X, Y, Z] in m/s^2 (ECI frame)
        self.utc_seconds = 0.0  # Seconds from epoch
        
        # Trick variable names
        self.trick_vars = [
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].R_CG_from_ECI_in_ECI[0]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].R_CG_from_ECI_in_ECI[1]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].R_CG_from_ECI_in_ECI[2]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].V_CG_rel_ECI_in_ECI[0]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].V_CG_rel_ECI_in_ECI[1]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].V_CG_rel_ECI_in_ECI[2]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].A_CG_rel_ECI_in_ECI[0]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].A_CG_rel_ECI_in_ECI[1]",
            "Sim.Orion_1.Dyn.DVehModel.State.VState[0].A_CG_rel_ECI_in_ECI[2]",
            "Sim.Orion_1.NEnv.itsSTimeModel.itsSTimeOutput.TimeData.UTC_Seconds_From_Epoch"
        ]
        
    def connect(self):
        """Establish connection to Trick Variable Server."""
        try:
            print("Connecting to Trick Variable Server at {}:{}...".format(self.host, self.port))
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.src = self.client_socket.makefile("r")
            
            # Pause variable server and clear any existing variables
            self.client_socket.send(b"trick.var_pause()\n")
            self.client_socket.send(b"trick.var_clear()\n")
            
            # Add all variables to the server
            for var in self.trick_vars:
                cmd = "trick.var_add(\"{}\")\n".format(var)
                self.client_socket.send(cmd.encode())
            
            # Unpause to start receiving data
            self.client_socket.send(b"trick.var_unpause()\n")
            
            self.connected = True
            print("Successfully connected to Trick Variable Server!")
            return True
            
        except Exception as e:
            print("Error connecting to Trick Variable Server: {}".format(e))
            print("Retrying in 1 second...")
            time.sleep(1)
            return False
    
    def update(self):
        """
        Update data from Trick Variable Server.
        
        Returns:
            bool: True if data was successfully updated, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            # Read line from variable server
            trick_server_data = self.src.readline()
            
            if trick_server_data == '':
                self.no_data = True
                return False
            else:
                self.no_data = False
            
            # Parse data (tab-separated values)
            values = trick_server_data.strip().split("\t")
            
            if len(values) >= 10:
                # Extract position (indices 1-3, index 0 is timestamp)
                self.position[0] = float(values[1])
                self.position[1] = float(values[2])
                self.position[2] = float(values[3])
                
                # Extract velocity (indices 4-6)
                self.velocity[0] = float(values[4])
                self.velocity[1] = float(values[5])
                self.velocity[2] = float(values[6])
                
                # Extract acceleration (indices 7-9)
                self.acceleration[0] = float(values[7])
                self.acceleration[1] = float(values[8])
                self.acceleration[2] = float(values[9])
                
                # Extract UTC seconds (index 10)
                self.utc_seconds = float(values[10])
                
                return True
            else:
                return False
                
        except Exception as e:
            print("Error reading from Trick Variable Server: {}".format(e))
            return False
    
    def disconnect(self):
        """Close connection to Trick Variable Server."""
        if self.client_socket:
            try:
                self.client_socket.send(b"trick.var_pause()\n")
                self.client_socket.send(b"trick.var_clear()\n")
                self.client_socket.close()
                print("Disconnected from Trick Variable Server")
            except:
                pass
        self.connected = False
    
    def get_position(self):
        """Get current position vector [X, Y, Z] in meters."""
        return self.position.copy()
    
    def get_velocity(self):
        """Get current velocity vector [X, Y, Z] in m/s."""
        return self.velocity.copy()
    
    def get_acceleration(self):
        """Get current acceleration vector [X, Y, Z] in m/s^2."""
        return self.acceleration.copy()
    
    def get_time(self):
        """Get current UTC seconds from epoch."""
        return self.utc_seconds


class FlightTrajectoryDisplay:
    """
    GUI application for displaying flight trajectory in real-time.
    """
    def __init__(self, root, host="localhost", port=7108, max_points=1000):
        """
        Initialize the flight trajectory display.
        
        Args:
            root: Tkinter root window
            host (str): Trick Variable Server host
            port (int): Trick Variable Server port
            max_points (int): Maximum number of trajectory points to display
        """
        self.root = root
        self.root.title("Orion Flight Trajectory Display")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Trick client
        self.trick_client = TrickVariableClient(host, port)
        self.max_points = max_points
        
        # Data buffers for trajectory history
        self.pos_x_history = deque(maxlen=max_points)
        self.pos_y_history = deque(maxlen=max_points)
        self.pos_z_history = deque(maxlen=max_points)
        self.time_history = deque(maxlen=max_points)
        
        # Current axis pair for plotting
        self.axis_mode = "X-Y"  # Can be "X-Y", "Y-Z", or "X-Z"
        
        # Zoom state
        self.zoom_level = 1.0
        self.x_limits = None
        self.y_limits = None
        
        # Setup UI
        self.setup_ui()
        
        # Try to connect
        self.is_running = False
        self.update_id = None
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Control panel (top)
        control_frame = Frame(main_frame, relief=RIDGE, borderwidth=2)
        control_frame.pack(side=TOP, fill=X, pady=(0, 10))
        
        # Connection controls
        conn_frame = Frame(control_frame)
        conn_frame.pack(side=LEFT, padx=10, pady=10)
        
        Label(conn_frame, text="Host:").grid(row=0, column=0, sticky=W)
        self.host_entry = Entry(conn_frame, width=15)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, padx=5)
        
        Label(conn_frame, text="Port:").grid(row=0, column=2, sticky=W, padx=(10, 0))
        self.port_entry = Entry(conn_frame, width=8)
        self.port_entry.insert(0, "7108")
        self.port_entry.grid(row=0, column=3, padx=5)
        
        self.connect_btn = Button(conn_frame, text="Connect", command=self.connect_to_trick, 
                                   bg="green", fg="white", width=10)
        self.connect_btn.grid(row=0, column=4, padx=10)
        
        self.status_label = Label(conn_frame, text="Not Connected", fg="red", font=("Arial", 10, "bold"))
        self.status_label.grid(row=0, column=5, padx=10)
        
        # View controls
        view_frame = Frame(control_frame)
        view_frame.pack(side=LEFT, padx=10, pady=10)
        
        Label(view_frame, text="View:").pack(side=LEFT, padx=5)
        self.axis_var = tk.StringVar(value="X-Y")
        axis_options = ["X-Y", "Y-Z", "X-Z"]
        axis_menu = ttk.Combobox(view_frame, textvariable=self.axis_var, 
                                  values=axis_options, state="readonly", width=8)
        axis_menu.pack(side=LEFT, padx=5)
        axis_menu.bind("<<ComboboxSelected>>", self.change_axis_mode)
        
        Button(view_frame, text="Clear Trajectory", command=self.clear_trajectory).pack(side=LEFT, padx=10)
        
        # Zoom and quit controls
        control_btns_frame = Frame(control_frame)
        control_btns_frame.pack(side=LEFT, padx=10, pady=10)
        
        Label(control_btns_frame, text="Zoom:").pack(side=LEFT, padx=5)
        Button(control_btns_frame, text="➕", command=self.zoom_in, width=3).pack(side=LEFT, padx=2)
        Button(control_btns_frame, text="➖", command=self.zoom_out, width=3).pack(side=LEFT, padx=2)
        Button(control_btns_frame, text="Reset", command=self.reset_zoom, width=5).pack(side=LEFT, padx=5)
        Button(control_btns_frame, text="Quit", command=self.quit_application, 
               bg="darkred", fg="white", width=8).pack(side=LEFT, padx=10)
        
        # Data display panel (left side)
        data_frame = Frame(main_frame, relief=RIDGE, borderwidth=2, width=300)
        data_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        data_frame.pack_propagate(False)
        
        Label(data_frame, text="Vehicle State Data", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Position display
        pos_frame = LabelFrame(data_frame, text="Position (ECI, meters)", font=("Arial", 10, "bold"))
        pos_frame.pack(fill=X, padx=10, pady=5)
        
        self.pos_x_label = Label(pos_frame, text="X: 0.0000", font=("Courier", 9))
        self.pos_x_label.pack(anchor=W, padx=5)
        self.pos_y_label = Label(pos_frame, text="Y: 0.0000", font=("Courier", 9))
        self.pos_y_label.pack(anchor=W, padx=5)
        self.pos_z_label = Label(pos_frame, text="Z: 0.0000", font=("Courier", 9))
        self.pos_z_label.pack(anchor=W, padx=5)
        
        # Velocity display
        vel_frame = LabelFrame(data_frame, text="Velocity (ECI, m/s)", font=("Arial", 10, "bold"))
        vel_frame.pack(fill=X, padx=10, pady=5)
        
        self.vel_x_label = Label(vel_frame, text="X: 0.0000", font=("Courier", 9))
        self.vel_x_label.pack(anchor=W, padx=5)
        self.vel_y_label = Label(vel_frame, text="Y: 0.0000", font=("Courier", 9))
        self.vel_y_label.pack(anchor=W, padx=5)
        self.vel_z_label = Label(vel_frame, text="Z: 0.0000", font=("Courier", 9))
        self.vel_z_label.pack(anchor=W, padx=5)
        
        # Acceleration display
        acc_frame = LabelFrame(data_frame, text="Acceleration (ECI, m/s²)", font=("Arial", 10, "bold"))
        acc_frame.pack(fill=X, padx=10, pady=5)
        
        self.acc_x_label = Label(acc_frame, text="X: 0.0000", font=("Courier", 9))
        self.acc_x_label.pack(anchor=W, padx=5)
        self.acc_y_label = Label(acc_frame, text="Y: 0.0000", font=("Courier", 9))
        self.acc_y_label.pack(anchor=W, padx=5)
        self.acc_z_label = Label(acc_frame, text="Z: 0.0000", font=("Courier", 9))
        self.acc_z_label.pack(anchor=W, padx=5)
        
        # Time display
        time_frame = LabelFrame(data_frame, text="Simulation Time", font=("Arial", 10, "bold"))
        time_frame.pack(fill=X, padx=10, pady=5)
        
        self.time_label = Label(time_frame, text="UTC Sec: 0.0000", font=("Courier", 9))
        self.time_label.pack(anchor=W, padx=5)
        
        # Statistics
        stats_frame = LabelFrame(data_frame, text="Statistics", font=("Arial", 10, "bold"))
        stats_frame.pack(fill=X, padx=10, pady=5)
        
        self.points_label = Label(stats_frame, text="Points: 0", font=("Courier", 9))
        self.points_label.pack(anchor=W, padx=5)
        self.speed_label = Label(stats_frame, text="Speed: 0.0000 m/s", font=("Courier", 9))
        self.speed_label.pack(anchor=W, padx=5)
        
        # Plot panel (right side)
        plot_frame = Frame(main_frame)
        plot_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.line, = self.ax.plot([], [], 'b-', linewidth=1, label='Trajectory')
        self.current_pos, = self.ax.plot([], [], 'ro', markersize=8, label='Current Position')
        
        self.ax.set_xlabel('X (m)', fontsize=12)
        self.ax.set_ylabel('Y (m)', fontsize=12)
        self.ax.set_title('Orion Flight Trajectory (X-Y Plane)', fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        self.ax.set_aspect('equal', adjustable='datalim')
        
        # Embed matplotlib figure in Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        
    def connect_to_trick(self):
        """Connect to Trick Variable Server."""
        if not self.trick_client.connected:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            
            self.trick_client.host = host
            self.trick_client.port = port
            
            if self.trick_client.connect():
                self.status_label.config(text="Connected", fg="green")
                self.connect_btn.config(text="Disconnect", bg="red")
                self.is_running = True
                self.update_display()
            else:
                self.status_label.config(text="Connection Failed", fg="red")
        else:
            self.disconnect_from_trick()
    
    def disconnect_from_trick(self):
        """Disconnect from Trick Variable Server."""
        self.is_running = False
        if self.update_id:
            self.root.after_cancel(self.update_id)
        self.trick_client.disconnect()
        self.status_label.config(text="Disconnected", fg="red")
        self.connect_btn.config(text="Connect", bg="green")
    
    def change_axis_mode(self, event=None):
        """Change the axis pair being displayed."""
        self.axis_mode = self.axis_var.get()
        self.update_plot_labels()
        self.update_plot()
    
    def update_plot_labels(self):
        """Update plot labels based on current axis mode."""
        if self.axis_mode == "X-Y":
            self.ax.set_xlabel('X (m)', fontsize=12)
            self.ax.set_ylabel('Y (m)', fontsize=12)
            self.ax.set_title('Orion Flight Trajectory (X-Y Plane)', fontsize=14, fontweight='bold')
        elif self.axis_mode == "Y-Z":
            self.ax.set_xlabel('Y (m)', fontsize=12)
            self.ax.set_ylabel('Z (m)', fontsize=12)
            self.ax.set_title('Orion Flight Trajectory (Y-Z Plane)', fontsize=14, fontweight='bold')
        elif self.axis_mode == "X-Z":
            self.ax.set_xlabel('X (m)', fontsize=12)
            self.ax.set_ylabel('Z (m)', fontsize=12)
            self.ax.set_title('Orion Flight Trajectory (X-Z Plane)', fontsize=14, fontweight='bold')
    
    def clear_trajectory(self):
        """Clear trajectory history."""
        self.pos_x_history.clear()
        self.pos_y_history.clear()
        self.pos_z_history.clear()
        self.time_history.clear()
        self.update_plot()
    
    def zoom_in(self):
        """Zoom in on the plot by 50%."""
        self.zoom_level *= 1.5
        self.apply_zoom()
    
    def zoom_out(self):
        """Zoom out on the plot by 50%."""
        self.zoom_level /= 1.5
        self.apply_zoom()
    
    def reset_zoom(self):
        """Reset zoom to fit all data."""
        self.zoom_level = 1.0
        self.x_limits = None
        self.y_limits = None
        self.update_plot()
    
    def apply_zoom(self):
        """Apply current zoom level to the plot."""
        if len(self.pos_x_history) == 0:
            return
        
        # Get data based on current axis mode
        if self.axis_mode == "X-Y":
            x_data = list(self.pos_x_history)
            y_data = list(self.pos_y_history)
        elif self.axis_mode == "Y-Z":
            x_data = list(self.pos_y_history)
            y_data = list(self.pos_z_history)
        elif self.axis_mode == "X-Z":
            x_data = list(self.pos_x_history)
            y_data = list(self.pos_z_history)
        else:
            return
        
        # Calculate center and range
        x_center = (max(x_data) + min(x_data)) / 2
        y_center = (max(y_data) + min(y_data)) / 2
        
        x_range = (max(x_data) - min(x_data)) / self.zoom_level
        y_range = (max(y_data) - min(y_data)) / self.zoom_level
        
        # Set new limits
        self.x_limits = [x_center - x_range/2, x_center + x_range/2]
        self.y_limits = [y_center - y_range/2, y_center + y_range/2]
        
        # Apply limits
        self.ax.set_xlim(self.x_limits)
        self.ax.set_ylim(self.y_limits)
        self.canvas.draw_idle()
    
    def quit_application(self):
        """Quit the application cleanly."""
        self.on_closing()
    
    def update_display(self):
        """Main update loop for display."""
        if not self.is_running:
            return
        
        # Get data from Trick
        if self.trick_client.update():
            # Get current state
            pos = self.trick_client.get_position()
            vel = self.trick_client.get_velocity()
            acc = self.trick_client.get_acceleration()
            t = self.trick_client.get_time()
            
            # Store history
            self.pos_x_history.append(pos[0])
            self.pos_y_history.append(pos[1])
            self.pos_z_history.append(pos[2])
            self.time_history.append(t)
            
            # Update text displays
            self.pos_x_label.config(text="X: {:.4e}".format(pos[0]))
            self.pos_y_label.config(text="Y: {:.4e}".format(pos[1]))
            self.pos_z_label.config(text="Z: {:.4e}".format(pos[2]))
            
            self.vel_x_label.config(text="X: {:.4e}".format(vel[0]))
            self.vel_y_label.config(text="Y: {:.4e}".format(vel[1]))
            self.vel_z_label.config(text="Z: {:.4e}".format(vel[2]))
            
            self.acc_x_label.config(text="X: {:.4e}".format(acc[0]))
            self.acc_y_label.config(text="Y: {:.4e}".format(acc[1]))
            self.acc_z_label.config(text="Z: {:.4e}".format(acc[2]))
            
            self.time_label.config(text="UTC Sec: {:.4f}".format(t))
            
            # Calculate speed
            speed = np.sqrt(vel[0]**2 + vel[1]**2 + vel[2]**2)
            self.speed_label.config(text="Speed: {:.4e} m/s".format(speed))
            
            # Update statistics
            self.points_label.config(text="Points: {}".format(len(self.pos_x_history)))
            
            # Update plot
            self.update_plot()
        
        # Schedule next update (50 Hz update rate)
        self.update_id = self.root.after(20, self.update_display)
    
    def update_plot(self):
        """Update the trajectory plot."""
        if len(self.pos_x_history) == 0:
            return
        
        # Get data based on current axis mode
        if self.axis_mode == "X-Y":
            x_data = list(self.pos_x_history)
            y_data = list(self.pos_y_history)
        elif self.axis_mode == "Y-Z":
            x_data = list(self.pos_y_history)
            y_data = list(self.pos_z_history)
        elif self.axis_mode == "X-Z":
            x_data = list(self.pos_x_history)
            y_data = list(self.pos_z_history)
        else:
            return
        
        # Update line data
        self.line.set_data(x_data, y_data)
        
        # Update current position marker
        if len(x_data) > 0:
            self.current_pos.set_data([x_data[-1]], [y_data[-1]])
        
        # Apply zoom limits if set, otherwise auto-scale
        if self.x_limits is not None and self.y_limits is not None:
            self.ax.set_xlim(self.x_limits)
            self.ax.set_ylim(self.y_limits)
        else:
            # Auto-scale axes
            self.ax.relim()
            self.ax.autoscale_view()
        
        # Redraw
        self.canvas.draw_idle()
    
    def on_closing(self):
        """Handle window closing event."""
        self.disconnect_from_trick()
        self.root.destroy()


def main():
    """Main entry point."""
    # Parse command line arguments
    host = "localhost"
    port = 7108
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    print("="*60)
    print("Orion Flight Trajectory Display")
    print("="*60)
    print("Default connection: {}:{}".format(host, port))
    print("You can change the host/port in the GUI before connecting.")
    print("="*60)
    
    # Create main window
    root = tk.Tk()
    root.geometry("1400x800")
    
    # Create application
    app = FlightTrajectoryDisplay(root, host=host, port=port, max_points=1000)
    
    # Start Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    main()


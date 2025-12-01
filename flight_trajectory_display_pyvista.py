#!/usr/bin/env python
"""
Flight Trajectory Display for NASA Trick Simulation - PyVista Edition
GPU-accelerated 3D visualization using PyVista/VTK
Connects to Trick Variable Server and plots Orion vehicle trajectory in real-time
Author: Generated for NASA Trick Project
"""

import socket
import sys
import numpy as np
from collections import deque
import time
import csv
from datetime import datetime
import os

# Python 2/3 compatibility
try:
    import Tkinter as tk
    from Tkinter import *
    import ttk
except ImportError:
    import tkinter as tk
    from tkinter import *
    from tkinter import ttk

try:
    import pyvista as pv
    from pyvistaqt import BackgroundPlotter
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    print("ERROR: PyVista not installed!")
    print("Please install with: pip install pyvista pyvistaqt")
    sys.exit(1)


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
    GUI application for displaying flight trajectory in real-time using PyVista.
    """
    def __init__(self, host="localhost", port=7108, max_points=10000):
        """
        Initialize the flight trajectory display.
        
        Args:
            host (str): Trick Variable Server host
            port (int): Trick Variable Server port
            max_points (int): Maximum number of trajectory points to display
        """
        # Trick client
        self.trick_client = TrickVariableClient(host, port)
        self.max_points = max_points
        
        # Data buffers for trajectory history
        self.pos_x_history = deque(maxlen=max_points)
        self.pos_y_history = deque(maxlen=max_points)
        self.pos_z_history = deque(maxlen=max_points)
        self.vel_x_history = deque(maxlen=max_points)
        self.vel_y_history = deque(maxlen=max_points)
        self.vel_z_history = deque(maxlen=max_points)
        self.acc_x_history = deque(maxlen=max_points)
        self.acc_y_history = deque(maxlen=max_points)
        self.acc_z_history = deque(maxlen=max_points)
        self.time_history = deque(maxlen=max_points)
        
        # View mode (2D or 3D)
        self.view_mode = "3D"  # Start with 3D for PyVista
        
        # Setup PyVista plotter
        self.plotter = BackgroundPlotter(title="Orion Flight Trajectory (PyVista 3D)")
        self.plotter.set_background('black')
        
        # Add coordinate axes
        self.plotter.add_axes()
        
        # Initialize empty trajectory line
        self.trajectory_actor = None
        self.current_pos_actor = None
        
        # State
        self.is_running = False
        
        # Setup control window (Tkinter)
        self.setup_control_window()
        
        # Start update timer
        self.update_timer = None
        
    def setup_control_window(self):
        """Setup the Tkinter control panel."""
        self.control_window = tk.Tk()
        self.control_window.title("Orion Trajectory Control Panel")
        self.control_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Main frame
        main_frame = Frame(self.control_window, padx=20, pady=20)
        main_frame.pack()
        
        # Connection controls
        conn_frame = LabelFrame(main_frame, text="Connection", font=("Arial", 11, "bold"), padx=10, pady=10)
        conn_frame.pack(fill=X, pady=10)
        
        Label(conn_frame, text="Host:").grid(row=0, column=0, sticky=W)
        self.host_entry = Entry(conn_frame, width=20)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, padx=5)
        
        Label(conn_frame, text="Port:").grid(row=1, column=0, sticky=W)
        self.port_entry = Entry(conn_frame, width=20)
        self.port_entry.insert(0, "7108")
        self.port_entry.grid(row=1, column=1, padx=5)
        
        self.connect_btn = Button(conn_frame, text="Connect", command=self.connect_to_trick,
                                   bg="green", fg="white", width=15, font=("Arial", 10, "bold"))
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.status_label = Label(conn_frame, text="Not Connected", fg="red", font=("Arial", 10, "bold"))
        self.status_label.grid(row=3, column=0, columnspan=2)
        
        # Data display
        data_frame = LabelFrame(main_frame, text="Vehicle State", font=("Arial", 11, "bold"), padx=10, pady=10)
        data_frame.pack(fill=X, pady=10)
        
        # Position
        Label(data_frame, text="Position (ECI, m):", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, sticky=W)
        self.pos_x_label = Label(data_frame, text="X: 0.0000", font=("Courier", 9))
        self.pos_x_label.grid(row=1, column=0, sticky=W)
        self.pos_y_label = Label(data_frame, text="Y: 0.0000", font=("Courier", 9))
        self.pos_y_label.grid(row=1, column=1, sticky=W)
        self.pos_z_label = Label(data_frame, text="Z: 0.0000", font=("Courier", 9))
        self.pos_z_label.grid(row=2, column=0, sticky=W)
        
        # Velocity
        Label(data_frame, text="Velocity (ECI, m/s):", font=("Arial", 10, "bold")).grid(row=3, column=0, columnspan=2, sticky=W, pady=(10,0))
        self.vel_x_label = Label(data_frame, text="X: 0.0000", font=("Courier", 9))
        self.vel_x_label.grid(row=4, column=0, sticky=W)
        self.vel_y_label = Label(data_frame, text="Y: 0.0000", font=("Courier", 9))
        self.vel_y_label.grid(row=4, column=1, sticky=W)
        self.vel_z_label = Label(data_frame, text="Z: 0.0000", font=("Courier", 9))
        self.vel_z_label.grid(row=5, column=0, sticky=W)
        
        # Speed and stats
        self.speed_label = Label(data_frame, text="Speed: 0.0000 m/s", font=("Courier", 9, "bold"))
        self.speed_label.grid(row=6, column=0, columnspan=2, sticky=W, pady=(10,0))
        
        self.points_label = Label(data_frame, text="Points: 0", font=("Courier", 9))
        self.points_label.grid(row=7, column=0, columnspan=2, sticky=W)
        
        # Control buttons
        btn_frame = Frame(main_frame)
        btn_frame.pack(fill=X, pady=10)
        
        Button(btn_frame, text="Clear Trajectory", command=self.clear_trajectory,
               bg="orange", fg="white", width=15).pack(side=LEFT, padx=5)
        Button(btn_frame, text="💾 Save Data", command=self.save_to_csv,
               bg="dodgerblue", fg="white", width=15).pack(side=LEFT, padx=5)
        Button(btn_frame, text="Quit", command=self.on_closing,
               bg="darkred", fg="white", width=15).pack(side=LEFT, padx=5)
        
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
                self.start_update_loop()
            else:
                self.status_label.config(text="Connection Failed", fg="red")
        else:
            self.disconnect_from_trick()
    
    def disconnect_from_trick(self):
        """Disconnect from Trick Variable Server."""
        self.is_running = False
        if self.update_timer:
            self.control_window.after_cancel(self.update_timer)
        
        # Auto-save data before disconnecting
        if len(self.time_history) > 0:
            filename = self.save_to_csv(auto_save=True)
            if filename:
                print("Simulation data automatically saved to: {}".format(filename))
        
        self.trick_client.disconnect()
        self.status_label.config(text="Disconnected", fg="red")
        self.connect_btn.config(text="Connect", bg="green")
    
    def clear_trajectory(self):
        """Clear trajectory history."""
        self.pos_x_history.clear()
        self.pos_y_history.clear()
        self.pos_z_history.clear()
        self.vel_x_history.clear()
        self.vel_y_history.clear()
        self.vel_z_history.clear()
        self.acc_x_history.clear()
        self.acc_y_history.clear()
        self.acc_z_history.clear()
        self.time_history.clear()
        
        # Clear PyVista actors
        if self.trajectory_actor:
            self.plotter.remove_actor(self.trajectory_actor)
            self.trajectory_actor = None
        if self.current_pos_actor:
            self.plotter.remove_actor(self.current_pos_actor)
            self.current_pos_actor = None
    
    def save_to_csv(self, auto_save=False):
        """
        Save trajectory data to a CSV file.
        
        Args:
            auto_save (bool): If True, automatically saves without user notification
        """
        if len(self.time_history) == 0:
            if not auto_save:
                print("No data to save!")
            return None
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = "orion_trajectory_{}.csv".format(timestamp)
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Time (UTC sec)',
                    'Position X (m)',
                    'Position Y (m)',
                    'Position Z (m)',
                    'Velocity X (m/s)',
                    'Velocity Y (m/s)',
                    'Velocity Z (m/s)',
                    'Acceleration X (m/s²)',
                    'Acceleration Y (m/s²)',
                    'Acceleration Z (m/s²)'
                ])
                
                # Write data rows
                for i in range(len(self.time_history)):
                    writer.writerow([
                        self.time_history[i],
                        self.pos_x_history[i],
                        self.pos_y_history[i],
                        self.pos_z_history[i],
                        self.vel_x_history[i],
                        self.vel_y_history[i],
                        self.vel_z_history[i],
                        self.acc_x_history[i],
                        self.acc_y_history[i],
                        self.acc_z_history[i]
                    ])
            
            if not auto_save:
                print("Data saved to: {}".format(filename))
                print("Total data points: {}".format(len(self.time_history)))
            
            return filename
            
        except Exception as e:
            print("Error saving CSV file: {}".format(e))
            return None
    
    def start_update_loop(self):
        """Start the update loop."""
        self.update_display()
    
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
            self.vel_x_history.append(vel[0])
            self.vel_y_history.append(vel[1])
            self.vel_z_history.append(vel[2])
            self.acc_x_history.append(acc[0])
            self.acc_y_history.append(acc[1])
            self.acc_z_history.append(acc[2])
            self.time_history.append(t)
            
            # Update text displays
            self.pos_x_label.config(text="X: {:.4e}".format(pos[0]))
            self.pos_y_label.config(text="Y: {:.4e}".format(pos[1]))
            self.pos_z_label.config(text="Z: {:.4e}".format(pos[2]))
            
            self.vel_x_label.config(text="X: {:.4e}".format(vel[0]))
            self.vel_y_label.config(text="Y: {:.4e}".format(vel[1]))
            self.vel_z_label.config(text="Z: {:.4e}".format(vel[2]))
            
            # Calculate speed
            speed = np.sqrt(vel[0]**2 + vel[1]**2 + vel[2]**2)
            self.speed_label.config(text="Speed: {:.4e} m/s".format(speed))
            
            # Update statistics
            self.points_label.config(text="Points: {}".format(len(self.pos_x_history)))
            
            # Update 3D plot
            self.update_plot()
        
        # Schedule next update (50 Hz update rate)
        self.update_timer = self.control_window.after(20, self.update_display)
    
    def update_plot(self):
        """Update the 3D trajectory plot."""
        if len(self.pos_x_history) < 2:
            return
        
        # Create points array for trajectory
        points = np.column_stack([
            list(self.pos_x_history),
            list(self.pos_y_history),
            list(self.pos_z_history)
        ])
        
        # Remove old trajectory actor
        if self.trajectory_actor:
            self.plotter.remove_actor(self.trajectory_actor)
        
        # Create polyline for trajectory
        trajectory = pv.Spline(points, len(points))
        self.trajectory_actor = self.plotter.add_mesh(trajectory, color='cyan', 
                                                      line_width=3, label='Trajectory')
        
        # Remove old current position actor
        if self.current_pos_actor:
            self.plotter.remove_actor(self.current_pos_actor)
        
        # Add current position as a sphere
        current_point = pv.Sphere(radius=abs(points[-1]).max() * 0.02, center=points[-1])
        self.current_pos_actor = self.plotter.add_mesh(current_point, color='red', 
                                                        label='Current Position')
        
    def on_closing(self):
        """Handle window closing event."""
        self.disconnect_from_trick()
        self.plotter.close()
        self.control_window.destroy()
    
    def run(self):
        """Start the application."""
        self.control_window.mainloop()


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
    print("Orion Flight Trajectory Display (PyVista Edition)")
    print("="*60)
    print("GPU-Accelerated 3D Visualization")
    print("Default connection: {}:{}".format(host, port))
    print("You can change the host/port in the GUI before connecting.")
    print("="*60)
    
    # Create and run application
    app = FlightTrajectoryDisplay(host=host, port=port, max_points=10000)
    app.run()


if __name__ == "__main__":
    main()


# Orion Flight Trajectory Display

This is a real-time flight trajectory visualization tool that connects to NASA's Trick Simulation Environment to display the Orion spacecraft's position, velocity, and acceleration data.

## Two Versions Available

### 1. **Matplotlib Version** (`flight_trajectory_display.py`) - Standard
- 2D and 3D visualization with toggle button
- Good for most users
- No additional dependencies beyond matplotlib

### 2. **PyVista Version** (`flight_trajectory_display_pyvista.py`) - High Performance
- GPU-accelerated 3D visualization
- Smoother rendering for real-time data
- Better for large datasets (10,000+ points)
- Requires PyVista installation

## Features

- **Real-time data connection** to Trick Variable Server
- **2D and 3D trajectory plotting** with switchable views
  - 2D: X-Y, Y-Z, X-Z plane views
  - 3D: Full 3D interactive visualization
- **Live state data display** for position, velocity, and acceleration vectors
- **Historical trajectory tracking** (up to 1000-10000 points depending on version)
- **Speed and statistics** calculations
- **Auto-save data** to CSV when simulation disconnects
- **Manual save** button to export data anytime
- **Zoom controls** for both 2D and 3D views

## Installation

### Prerequisites

1. Python 2.7 or Python 3.x
2. Required Python packages:

**For Matplotlib Version (Standard):**
```bash
pip install matplotlib numpy
```

**For PyVista Version (High Performance):**
```bash
pip install matplotlib numpy pyvista pyvistaqt PyQt5
```

Or use the requirements file:

```bash
pip install -r requirements.txt
# For PyVista version, uncomment the PyVista lines in requirements.txt first
```

## Usage

### Step 1: Start Your Trick Simulation

Follow the procedure in the PDF document to start the SOC VM simulation:

1. Open Dashboard and load the Luna 2.1 VM load
2. Select the appropriate host (e.g., jstsdxmpcv01)
3. Init session and start the simulation
4. Load the VM and wait for it to boot (about 3 minutes)
5. Select your init point (e.g., "orbit")
6. Wait for the simulation to be ready to mode to run

### Step 2: Run the Trajectory Display

Once your Trick simulation is running, start the display:

**Matplotlib Version (Standard):**
```bash
python flight_trajectory_display.py
```

**PyVista Version (High Performance 3D):**
```bash
python flight_trajectory_display_pyvista.py
```

Or specify a custom host and port for either version:

```bash
python flight_trajectory_display.py 192.168.121.35 7108
python flight_trajectory_display_pyvista.py 192.168.121.35 7108
```

### Step 3: Connect to Trick

1. Enter the host IP (e.g., `192.168.121.35` for SOC VM or `localhost` for local sims)
2. Enter the port (default is `7108`)
3. Click **Connect**
4. The display will start showing real-time trajectory data

### Step 4: Use the Display

**Matplotlib Version:**
- **Toggle 2D/3D**: Click "Switch to 3D" button to toggle between 2D and 3D views
- **Change 2D View**: Use the dropdown to switch between X-Y, Y-Z, and X-Z plane views (in 2D mode)
- **Zoom**: Use the +/- buttons to zoom in/out, or click "Reset" to fit all data
- **Clear Trajectory**: Click to clear the historical trajectory path
- **Save Data**: Click "💾 Save Data" to export current trajectory to CSV file
- **Monitor Data**: Watch the left panel for real-time position, velocity, and acceleration values
- **Auto-save**: When you disconnect, data is automatically saved to a timestamped CSV file

**PyVista Version:**
- **3D View Only**: Always displays full 3D trajectory
- **Rotate**: Click and drag in the 3D window to rotate the view
- **Zoom**: Scroll to zoom in/out in the 3D window
- **Save Data**: Click "💾 Save Data" to export current trajectory to CSV file
- **Control Panel**: Separate Tkinter window for connection and data display
- **Auto-save**: When you disconnect, data is automatically saved to a timestamped CSV file

## CSV Data Export

Both versions automatically save all trajectory data when you disconnect from the simulation:

**File Format:** `orion_trajectory_YYYY-MM-DD_HH-MM-SS.csv`

**Data Columns:**
- Time (UTC sec)
- Position X, Y, Z (m)
- Velocity X, Y, Z (m/s)
- Acceleration X, Y, Z (m/s²)

**Usage:**
- Files are saved in the same directory where you run the script
- Can be opened in Excel, Google Sheets, MATLAB, or Python for analysis
- Manual save available anytime via "💾 Save Data" button

## Which Version Should You Use?

**Use Matplotlib Version if:**
- ✅ You want 2D and 3D views with easy toggling
- ✅ You don't want to install extra dependencies
- ✅ You're tracking < 1000 points
- ✅ You want everything in one window

**Use PyVista Version if:**
- ✅ You need smoother 3D rendering
- ✅ You're tracking lots of data (1000-10000 points)
- ✅ You want GPU acceleration
- ✅ Your Matplotlib 3D view is choppy/slow
- ✅ You want professional-grade 3D visualization

## Trick Variables Being Monitored

The display retrieves the following variables from the Trick simulation:

- **Position**: `Sim.Orion_1.Dyn.DVehModel.State.VState[0].R_CG_from_ECI_in_ECI[0-2]`
- **Velocity**: `Sim.Orion_1.Dyn.DVehModel.State.VState[0].V_CG_rel_ECI_in_ECI[0-2]`
- **Acceleration**: `Sim.Orion_1.Dyn.DVehModel.State.VState[0].A_CG_rel_ECI_in_ECI[0-2]`
- **Time**: `Sim.Orion_1.NEnv.itsSTimeModel.itsSTimeOutput.TimeData.UTC_Seconds_From_Epoch`

All data is in the ECI (Earth-Centered Inertial) reference frame.

## Coordinate System

- **ECI Frame**: Earth-Centered Inertial coordinate system
- **X-Y Plane**: Equatorial plane view
- **Y-Z Plane**: Side view (perpendicular to X-axis)
- **X-Z Plane**: Front view (perpendicular to Y-axis)

## Troubleshooting

### "Connection Failed" Error

- Make sure your Trick simulation is running and in RUN mode
- Verify the host IP address is correct
- Check that the port number is correct (default: 7108)
- Ensure the simulation has fully initialized and loaded

### "No Data" or Frozen Display

- Check that the Trick Variable Server is active
- Verify that the simulation is not paused or in FREEZE mode
- Make sure you've selected the correct init point and the VM has completed setup

### Display Not Updating

- The update rate is 50 Hz (20ms between updates)
- If data is updating slowly, check your network connection to the simulation host
- Try clearing the trajectory if too many points are displayed

## Extending the Code

### Access Position, Velocity, Acceleration

The `TrickVariableClient` class provides methods to access all vehicle state data:

```python
# In the code, you can access:
position = self.trick_client.get_position()  # Returns [X, Y, Z] in meters
velocity = self.trick_client.get_velocity()  # Returns [X, Y, Z] in m/s
acceleration = self.trick_client.get_acceleration()  # Returns [X, Y, Z] in m/s^2
time = self.trick_client.get_time()  # Returns UTC seconds from epoch
```

### Adding More Variables

To add more Trick variables, modify the `trick_vars` list in the `TrickVariableClient.__init__()` method:

```python
self.trick_vars = [
    # ... existing variables ...
    "Your.New.Trick.Variable.Here"
]
```

### Changing Plot Style

Modify the plot setup in the `setup_ui()` method:

```python
# Change line color, style, width
self.line, = self.ax.plot([], [], 'g--', linewidth=2, label='Trajectory')

# Change marker style, size, color
self.current_pos, = self.ax.plot([], [], 'rs', markersize=10, label='Current Position')
```

### Adjusting History Buffer Size

Change the `max_points` parameter when creating the display:

```python
app = FlightTrajectoryDisplay(root, host=host, port=port, max_points=5000)
```

## Additional Notes

- The display uses scientific notation for large values (common for orbital mechanics)
- Position values are typically on the order of 10^6 to 10^7 meters for Earth orbit
- Velocity values are typically on the order of 10^3 to 10^4 m/s for orbital speeds
- The trajectory plot auto-scales to fit all data points

## Contact

For questions about this display, contact your NASA JSC team lead or refer to the Trick documentation at:
https://github.com/nasa/trick


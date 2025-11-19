# Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     NASA Trick Simulation                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │          Orion Vehicle Simulation Model            │     │
│  │                                                     │     │
│  │  • Position (R_CG_from_ECI_in_ECI)                 │     │
│  │  • Velocity (V_CG_rel_ECI_in_ECI)                  │     │
│  │  • Acceleration (A_CG_rel_ECI_in_ECI)              │     │
│  │  • Time (UTC_Seconds_From_Epoch)                   │     │
│  └────────────────────────────────────────────────────┘     │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │         Trick Variable Server (Port 7108)          │     │
│  │                                                     │     │
│  │  • Manages variable subscriptions                  │     │
│  │  • Streams data via TCP                            │     │
│  │  • Commands: var_add, var_clear, var_pause         │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               │ TCP Connection
                               │ (Host:7108)
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│              Flight Trajectory Display (Python)              │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │         TrickVariableClient Class                │       │
│  │                                                   │       │
│  │  • Establishes socket connection                 │       │
│  │  • Subscribes to variables                       │       │
│  │  • Parses incoming data stream                   │       │
│  │  • Updates position/velocity/acceleration        │       │
│  │                                                   │       │
│  │  Methods:                                         │       │
│  │    - connect()                                    │       │
│  │    - update()                                     │       │
│  │    - get_position()                               │       │
│  │    - get_velocity()                               │       │
│  │    - get_acceleration()                           │       │
│  │    - get_time()                                   │       │
│  └───────────────────┬───────────────────────────────┘       │
│                      │                                        │
│                      ▼                                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │      FlightTrajectoryDisplay Class               │       │
│  │                                                   │       │
│  │  ┌─────────────────────────────────────────┐    │       │
│  │  │      GUI Components (Tkinter)           │    │       │
│  │  │                                          │    │       │
│  │  │  • Connection controls                   │    │       │
│  │  │  • View mode selector (X-Y, Y-Z, X-Z)   │    │       │
│  │  │  • Real-time data display                │    │       │
│  │  │  • Statistics panel                      │    │       │
│  │  └─────────────────────────────────────────┘    │       │
│  │                                                   │       │
│  │  ┌─────────────────────────────────────────┐    │       │
│  │  │    Plotting (Matplotlib)                 │    │       │
│  │  │                                          │    │       │
│  │  │  • 2D trajectory visualization           │    │       │
│  │  │  • Historical path (up to 1000 points)  │    │       │
│  │  │  • Current position marker               │    │       │
│  │  │  • Auto-scaling axes                     │    │       │
│  │  └─────────────────────────────────────────┘    │       │
│  │                                                   │       │
│  │  ┌─────────────────────────────────────────┐    │       │
│  │  │    Data Buffers (Collections.deque)      │    │       │
│  │  │                                          │    │       │
│  │  │  • pos_x_history (1000 points max)      │    │       │
│  │  │  • pos_y_history (1000 points max)      │    │       │
│  │  │  • pos_z_history (1000 points max)      │    │       │
│  │  │  • time_history (1000 points max)       │    │       │
│  │  └─────────────────────────────────────────┘    │       │
│  │                                                   │       │
│  │  Update Loop (50 Hz):                            │       │
│  │    1. Read data from Trick                       │       │
│  │    2. Update GUI text displays                   │       │
│  │    3. Append to history buffers                  │       │
│  │    4. Redraw plot                                │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Connection Phase

```
User Action                  Python Code                    Trick Server
───────────                  ──────────────                 ────────────
[Click Connect] ───────────> connect()
                             │
                             ├─ Create socket
                             ├─ Connect to host:port ─────> [Accept connection]
                             │
                             ├─ Send "var_pause()" ───────> [Pause updates]
                             ├─ Send "var_clear()" ───────> [Clear variables]
                             │
                             ├─ Send "var_add(...)" ──────> [Subscribe to vars]
                             │  (repeated for each var)
                             │
                             └─ Send "var_unpause()" ─────> [Start streaming]
                                                              │
                                                              ▼
                                                      [Begin sending data]
```

### 2. Runtime Data Loop

```
Trick Server              Python Code                   Display
────────────              ───────────                   ───────
[Stream data] ─────────> update()
                         │
                         ├─ Read line from socket
                         ├─ Parse tab-separated values
                         ├─ Extract X,Y,Z for each vector
                         │
                         └─ Update internal variables:
                            • position[0,1,2]
                            • velocity[0,1,2]
                            • acceleration[0,1,2]
                            • utc_seconds
                                 │
                                 ▼
                         update_display()
                         │
                         ├─ Get data from client
                         ├─ Append to history buffers
                         ├─ Update text labels ─────────> [User sees values]
                         ├─ Calculate statistics
                         └─ Update plot ───────────────> [User sees trajectory]
                                 │
                                 ▼
                         [Schedule next update in 20ms]
```

### 3. View Mode Changes

```
User Action                  Code Action                    Display Result
───────────                  ───────────                    ──────────────
[Select "X-Y"] ──────────> axis_mode = "X-Y"
                           │
                           ├─ Update plot labels
                           └─ Replot with X,Y data ─────> [Shows X-Y plane]

[Select "Y-Z"] ──────────> axis_mode = "Y-Z"
                           │
                           ├─ Update plot labels
                           └─ Replot with Y,Z data ─────> [Shows Y-Z plane]

[Select "X-Z"] ──────────> axis_mode = "X-Z"
                           │
                           ├─ Update plot labels
                           └─ Replot with X,Z data ─────> [Shows X-Z plane]
```

## Key Classes

### TrickVariableClient

**Purpose**: Manages communication with Trick Variable Server

**Key Attributes**:
- `position`: [X, Y, Z] position vector in meters
- `velocity`: [X, Y, Z] velocity vector in m/s
- `acceleration`: [X, Y, Z] acceleration vector in m/s²
- `utc_seconds`: Time in seconds from epoch

**Key Methods**:
- `connect()`: Establishes connection and subscribes to variables
- `update()`: Reads and parses latest data from server
- `get_position()`, `get_velocity()`, `get_acceleration()`, `get_time()`: Data accessors
- `disconnect()`: Cleanly closes connection

### FlightTrajectoryDisplay

**Purpose**: Main GUI application and visualization

**Key Attributes**:
- `trick_client`: Instance of TrickVariableClient
- `pos_x/y/z_history`: Circular buffers for trajectory points
- `axis_mode`: Current view mode ("X-Y", "Y-Z", "X-Z")
- `fig`, `ax`: Matplotlib figure and axes
- `line`, `current_pos`: Plot elements

**Key Methods**:
- `setup_ui()`: Creates all GUI widgets and plot
- `connect_to_trick()`: Initiates connection to Trick
- `update_display()`: Main update loop (called every 20ms)
- `update_plot()`: Redraws trajectory plot
- `change_axis_mode()`: Switches between view planes

## Coordinate Systems

### ECI (Earth-Centered Inertial) Frame

All data from Trick is in the ECI reference frame:

```
        Z (North)
        │
        │
        │
        └────────── X (Vernal Equinox)
       ╱
      ╱
     ╱
    Y (Completes right-hand system)
```

### View Modes

- **X-Y Plane**: Equatorial plane (looking down from North pole)
- **Y-Z Plane**: Side view (looking from Vernal Equinox direction)
- **X-Z Plane**: Front view (looking perpendicular to Y-axis)

## Performance Characteristics

- **Update Rate**: 50 Hz (20ms intervals)
- **History Buffer**: 1000 points (auto-removes oldest)
- **Data Volume**: ~10 floats per update (~80 bytes)
- **Network**: TCP, typically local or LAN speeds
- **GUI Responsiveness**: Non-blocking updates via `after()` scheduling

## Extension Points

### Adding New Variables

In `TrickVariableClient.__init__()`:
```python
self.trick_vars.append("Your.New.Variable.Path")
```

### Changing Update Rate

In `FlightTrajectoryDisplay.update_display()`:
```python
# Change 20ms to desired interval (e.g., 100ms for 10Hz)
self.update_id = self.root.after(100, self.update_display)
```

### Increasing History Size

When creating display:
```python
app = FlightTrajectoryDisplay(root, max_points=5000)
```

### Adding 3D Visualization

Would require:
- `from mpl_toolkits.mplot3d import Axes3D`
- Replace 2D axes with 3D axes
- Plot all three dimensions simultaneously
- Add rotation/zoom controls

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection timeout | Trick not running | Start simulation first |
| No data | Sim in FREEZE | Mode to RUN |
| Variables not found | Wrong variable names | Verify in Trick variable server |
| Slow updates | Network latency | Use local host if possible |
| Plot not updating | Too many points | Reduce history buffer size |

## File Structure

```
NASA Trick It/
├── flight_trajectory_display.py    # Main application
├── test_trick_connection.py        # Connection test utility
├── example.py                       # Raphael's original (reference)
├── requirements.txt                 # Python dependencies
├── README_TRAJECTORY.md             # Detailed documentation
├── QUICK_START.md                   # Quick setup guide
└── ARCHITECTURE.md                  # This file
```

## References

- **Trick Documentation**: https://github.com/nasa/trick
- **Matplotlib Documentation**: https://matplotlib.org/
- **Python Socket Programming**: https://docs.python.org/3/library/socket.html
- **Tkinter Documentation**: https://docs.python.org/3/library/tkinter.html

---

This architecture is designed to be:
- ✅ **Simple**: Clear separation of concerns
- ✅ **Extensible**: Easy to add new features
- ✅ **Robust**: Handles connection errors gracefully
- ✅ **Performant**: Efficient data handling and plotting


# Quick Start Guide

## What You Have

Three Python scripts for working with NASA Trick simulations:

1. **`flight_trajectory_display.py`** - Main GUI application for visualizing Orion trajectory
2. **`test_trick_connection.py`** - Simple test script to verify Trick connection
3. **`example.py`** - Raphael's original display (for reference)

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install matplotlib numpy
```

### 2. Start Your Trick Simulation

Follow your PDF procedure:
- Load Luna 2.1 in Dashboard
- Select host (e.g., `jstsdxmpcv01` or use IP like `192.168.121.35`)
- Init session → Start simulation
- Wait for VM to boot (~3 minutes)
- Select init point (e.g., "orbit")
- Wait for sim to be ready to RUN

### 3. Test the Connection

Before running the full display, test your connection:

```bash
# For local simulation
python test_trick_connection.py localhost 7108

# For SOC VM (example IP)
python test_trick_connection.py 192.168.121.35 7108
```

This will run for 10 seconds and print out position/velocity/acceleration data.

**Expected output:**
```
✓ TEST PASSED - Connection and data retrieval working!
```

### 4. Run the Trajectory Display

Once the test passes:

```bash
# For local simulation
python flight_trajectory_display.py localhost 7108

# For SOC VM
python flight_trajectory_display.py 192.168.121.35 7108
```

Or just run it and enter the host/port in the GUI:

```bash
python flight_trajectory_display.py
```

## Using the Display

### Connection Panel (Top)
- **Host**: Enter simulation host (IP or hostname)
- **Port**: Usually 7108 for Trick Variable Server
- **Connect Button**: Click to connect/disconnect
- **Status**: Shows connection state

### View Controls
- **View Dropdown**: Switch between X-Y, Y-Z, X-Z planes
- **Clear Trajectory**: Reset the trajectory path

### Data Panel (Left)
Shows real-time values for:
- Position (X, Y, Z) in meters (ECI frame)
- Velocity (X, Y, Z) in m/s
- Acceleration (X, Y, Z) in m/s²
- UTC time in seconds
- Current speed and point count

### Plot Panel (Right)
- Blue line: Historical trajectory path
- Red dot: Current vehicle position
- Auto-scales to fit all data

## Troubleshooting

### "Connection Failed"
1. Check that Trick simulation is running
2. Verify the host IP is correct
3. Make sure port is 7108 (or whatever your sim uses)
4. Ensure sim is in RUN mode (not FREEZE)

### "No Data" Warning
- Simulation might be paused
- Try moding to RUN in Trick
- Check that variables exist in your simulation

### Script Won't Run
```bash
# Make sure scripts are executable
chmod +x flight_trajectory_display.py test_trick_connection.py

# Check Python version
python --version  # Should be 2.7 or 3.x

# Check dependencies
pip list | grep matplotlib
pip list | grep numpy
```

## Common Host/Port Combinations

Based on your workflow:

| Simulation Type | Host Example | Port |
|----------------|--------------|------|
| Local Trick | `localhost` | 7108 |
| SOC VM (Luna) | `192.168.121.35` | 7108 |
| Remote Host | `jstsdxmpcv01` | 7108 |

**Note**: The IP/hostname will depend on which host you selected in Dashboard when starting your session.

## What the Code Does

The trajectory display:

1. **Connects** to Trick Variable Server via TCP socket
2. **Subscribes** to these variables:
   - `Sim.Orion_1.Dyn.DVehModel.State.VState[0].R_CG_from_ECI_in_ECI[0-2]` (Position)
   - `Sim.Orion_1.Dyn.DVehModel.State.VState[0].V_CG_rel_ECI_in_ECI[0-2]` (Velocity)
   - `Sim.Orion_1.Dyn.DVehModel.State.VState[0].A_CG_rel_ECI_in_ECI[0-2]` (Acceleration)
   - `Sim.Orion_1.NEnv.itsSTimeModel.itsSTimeOutput.TimeData.UTC_Seconds_From_Epoch` (Time)

3. **Updates** at 50 Hz (20ms intervals)
4. **Stores** up to 1000 historical points
5. **Plots** trajectory in 2D (switchable between axis pairs)

## Next Steps

After you verify this works:

1. You can modify the code to add more variables
2. Add 3D plotting if needed (would require additional libraries)
3. Add data logging/export features
4. Customize the plot appearance

## Questions?

- Check `README_TRAJECTORY.md` for detailed documentation
- Look at `example.py` to see Raphael's approach
- Contact Sara or Colby Lewis for SOC-specific questions
- Refer to Trick documentation: https://github.com/nasa/trick

---

**Pro Tip**: Always run the test script first before the full display. It's faster and will tell you immediately if there's a connection issue!


# Orion Flight Trajectory Display

Real-time visualization tool for NASA Trick Simulation Environment - Orion spacecraft trajectory display.

## 🚀 Quick Start

```bash
# Install dependencies
pip install matplotlib numpy

# Test connection
python test_trick_connection.py YOUR_HOST 7108

# Run display
python flight_trajectory_display.py YOUR_HOST 7108
```

## 📋 Features

- ✅ Real-time connection to Trick Variable Server
- ✅ 2D trajectory plotting with switchable views (X-Y, Y-Z, X-Z)
- ✅ Live position, velocity, and acceleration data display
- ✅ Zoom controls (zoom in/out, reset)
- ✅ Historical trajectory tracking (1000 points)
- ✅ Auto-scaling or manual zoom
- ✅ Connection test utility

## 📁 Files

| File | Description |
|------|-------------|
| `flight_trajectory_display.py` | Main GUI application |
| `test_trick_connection.py` | Connection test utility |
| `example.py` | Reference implementation |
| `START_HERE.md` | Getting started guide |
| `QUICK_START.md` | Quick setup instructions |
| `README_TRAJECTORY.md` | Detailed documentation |

## 🎮 Controls

- **Connect/Disconnect**: Connect to Trick simulation
- **View Dropdown**: Switch between X-Y, Y-Z, X-Z planes
- **➕ Zoom In**: Zoom into trajectory (1.5x)
- **➖ Zoom Out**: Zoom out from trajectory (1.5x)
- **Reset**: Reset zoom to fit all data
- **Clear Trajectory**: Clear trajectory history
- **Quit**: Exit application

## 📊 Data Monitored

All data is retrieved from the Trick simulation in the ECI (Earth-Centered Inertial) reference frame:

- Position: `Sim.Orion_1.Dyn.DVehModel.State.VState[0].R_CG_from_ECI_in_ECI[0-2]`
- Velocity: `Sim.Orion_1.Dyn.DVehModel.State.VState[0].V_CG_rel_ECI_in_ECI[0-2]`
- Acceleration: `Sim.Orion_1.Dyn.DVehModel.State.VState[0].A_CG_rel_ECI_in_ECI[0-2]`
- Time: `Sim.Orion_1.NEnv.itsSTimeModel.itsSTimeOutput.TimeData.UTC_Seconds_From_Epoch`

## 🔧 Requirements

- Python 2.7 or 3.x
- matplotlib
- numpy
- NASA Trick Simulation Environment
- Active Trick Variable Server (port 7108)

## 📖 Documentation

See `START_HERE.md` for complete documentation and setup instructions.

## 🏛️ NASA JSC Project

Developed for NASA Johnson Space Center - Orion spacecraft simulation visualization.

## 📝 License

For internal NASA use.


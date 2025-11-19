# 🚀 START HERE - Flight Trajectory Display for NASA Trick

Welcome! This project provides a real-time visualization tool for the Orion spacecraft trajectory using NASA's Trick Simulation Environment.

## 📁 What's Included

| File | Purpose |
|------|---------|
| **`flight_trajectory_display.py`** | 🎯 **MAIN APPLICATION** - GUI for trajectory visualization |
| **`test_trick_connection.py`** | 🔧 **TEST UTILITY** - Verify connection before running main app |
| `example.py` | 📚 Reference - Raphael's original display code |
| `requirements.txt` | 📦 Python package dependencies |
| `QUICK_START.md` | ⚡ Quick setup and usage instructions |
| `README_TRAJECTORY.md` | 📖 Detailed documentation |
| `ARCHITECTURE.md` | 🏗️ System design and internals |

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies (30 seconds)

```bash
pip install matplotlib numpy
```

### Step 2: Test Connection (30 seconds)

Start your Trick simulation first (follow your PDF procedure), then test:

```bash
python test_trick_connection.py YOUR_HOST_IP 7108
```

**Example for SOC VM:**
```bash
python test_trick_connection.py 192.168.121.35 7108
```

**Example for local:**
```bash
python test_trick_connection.py localhost 7108
```

✅ If you see `TEST PASSED`, you're ready!

### Step 3: Run the Display

```bash
python flight_trajectory_display.py YOUR_HOST_IP 7108
```

Or just run it and enter the connection details in the GUI:

```bash
python flight_trajectory_display.py
```

## 🎮 Using the Display

Once connected, you'll see:

- **📊 Left Panel**: Real-time position, velocity, acceleration data
- **📈 Right Panel**: 2D trajectory plot
- **🎛️ Controls**: Switch between X-Y, Y-Z, X-Z views

## 📋 What This Code Does

The display connects to your Trick simulation and retrieves:

1. **Position** (`R_CG_from_ECI_in_ECI`) - Where the vehicle is
2. **Velocity** (`V_CG_rel_ECI_in_ECI`) - How fast it's moving
3. **Acceleration** (`A_CG_rel_ECI_in_ECI`) - How it's accelerating
4. **Time** (`UTC_Seconds_From_Epoch`) - Simulation time

All data is in the **ECI (Earth-Centered Inertial)** reference frame.

## 🔍 What Makes This Different from Raphael's Code

| Feature | Raphael's Display | This Display |
|---------|------------------|--------------|
| Purpose | Monitor forces and states | **Visualize trajectory path** |
| Data Type | Multiple force vectors | **Position, velocity, acceleration** |
| Visualization | Text display only | **2D trajectory plot** |
| View Modes | N/A | **Toggle X-Y, Y-Z, X-Z planes** |
| History | 50 points buffer | **1000 points trajectory** |
| Focus | Tolerance checking | **Flight path visualization** |

Both use the same underlying Trick Variable Server connection method!

## 📚 Documentation Roadmap

Read in this order:

1. **START_HERE.md** (this file) - Overview
2. **QUICK_START.md** - Detailed setup instructions
3. **README_TRAJECTORY.md** - Full documentation and features
4. **ARCHITECTURE.md** - How the code works internally

## 🚨 Troubleshooting

### Connection Issues

**Problem**: "Connection Failed"

**Solutions**:
- ✅ Make sure Trick simulation is running
- ✅ Verify you're using the correct host IP
- ✅ Check port is 7108 (Variable Server default)
- ✅ Ensure simulation is in RUN mode (not FREEZE)

**Run the test script first** - it will tell you exactly what's wrong!

### No Data or Frozen Display

**Problem**: Display shows but data doesn't update

**Solutions**:
- ✅ Check that simulation is moded to RUN
- ✅ Verify the variable names match your simulation
- ✅ Try clearing the trajectory and reconnecting

### Import Errors

**Problem**: "ModuleNotFoundError: No module named 'matplotlib'"

**Solution**:
```bash
pip install matplotlib numpy
```

## 🎯 Your Task Requirements - Status

Based on your coworker's instructions:

| Requirement | Status | Notes |
|-------------|--------|-------|
| Connect to Trick Variable Server | ✅ Complete | Via TCP socket to port 7108 |
| Get Position data | ✅ Complete | `R_CG_from_ECI_in_ECI[0-2]` |
| Get Velocity data | ✅ Complete | `V_CG_rel_ECI_in_ECI[0-2]` |
| Get Acceleration data | ✅ Complete | `A_CG_rel_ECI_in_ECI[0-2]` |
| Get Time data | ✅ Complete | `UTC_Seconds_From_Epoch` |
| Plot position | ✅ Complete | 2D real-time plotting |
| Make vel/acc accessible | ✅ Complete | Available via `get_velocity()`, `get_acceleration()` |
| 2D plotting | ✅ Complete | Using matplotlib |
| Toggle axis pairs | ✅ Complete | X-Y, Y-Z, X-Z views |
| Python implementation | ✅ Complete | Python 2/3 compatible |

## 🔧 For Developers - Extending the Code

### Access the Data in Your Own Code

```python
from flight_trajectory_display import TrickVariableClient

# Create client
client = TrickVariableClient(host="192.168.121.35", port=7108)
client.connect()

# Get data
while True:
    if client.update():
        pos = client.get_position()      # [X, Y, Z] in meters
        vel = client.get_velocity()      # [X, Y, Z] in m/s
        acc = client.get_acceleration()  # [X, Y, Z] in m/s²
        time = client.get_time()         # seconds
        
        # Do your math here!
        print("Position:", pos)
```

### Add More Variables

Edit `TrickVariableClient.__init__()`:

```python
self.trick_vars.append("Sim.Your.New.Variable.Here")
```

### Change to 3D Plotting

The code is structured to make this easy:
1. Import `Axes3D` from `mpl_toolkits.mplot3d`
2. Create 3D axes instead of 2D
3. Plot X, Y, Z together instead of pairs

## 🤝 Getting Help

- **Trick-specific questions**: Talk to Sara or Colby Lewis
- **SOC VM questions**: Consult the ts-pss team
- **Code questions**: Check `ARCHITECTURE.md` for internals
- **Connection issues**: Run `test_trick_connection.py` first

## 📝 Next Steps

1. ✅ Read this file (you just did!)
2. ⏭️ Install dependencies: `pip install matplotlib numpy`
3. ⏭️ Start your Trick simulation (follow PDF procedure)
4. ⏭️ Run test script: `python test_trick_connection.py HOST PORT`
5. ⏭️ Run main display: `python flight_trajectory_display.py`
6. ⏭️ Verify the trajectory looks correct
7. ⏭️ Show your supervisor/coworker!

## 🎓 Learning Resources

- **NASA Trick**: https://github.com/nasa/trick
- **Matplotlib**: https://matplotlib.org/stable/tutorials/index.html
- **Python Sockets**: https://realpython.com/python-sockets/
- **ECI Coordinate System**: https://en.wikipedia.org/wiki/Earth-centered_inertial

## ✅ Pre-Flight Checklist

Before showing this to your team:

- [ ] Installed matplotlib and numpy
- [ ] Started Trick simulation (Luna 2.1 VM)
- [ ] Simulation is in RUN mode
- [ ] Test script passes: `python test_trick_connection.py`
- [ ] Main display connects and shows data
- [ ] Trajectory plot is updating
- [ ] Can toggle between X-Y, Y-Z, X-Z views
- [ ] Data values look reasonable (position ~10^6 m for orbit)

---

## 🚀 Ready to Launch!

You now have everything you need to visualize the Orion flight trajectory in real-time. 

**Start with the test script**, then move to the full display. Good luck with your project!

*Questions? Check the other documentation files or ask your team!*


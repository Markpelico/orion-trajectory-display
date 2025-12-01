# 3D Trajectory Display - Version Comparison

## Quick Start Guide

You now have **two versions** of the trajectory display with 3D capabilities:

---

## 📊 Matplotlib Version
**File:** `flight_trajectory_display.py`

### Pros:
- ✅ **No extra dependencies** - uses what you already have
- ✅ **Toggle 2D/3D** with one button click
- ✅ **All-in-one window** - everything in a single GUI
- ✅ **Easy to use** - familiar matplotlib interface
- ✅ **2D views available** - X-Y, Y-Z, X-Z planes

### Cons:
- ⚠️ Can be **choppy with >500 points**
- ⚠️ **CPU-only rendering** (no GPU acceleration)
- ⚠️ Limited to ~1000 points max

### Best For:
- Quick testing and demos
- When you need both 2D and 3D views
- Smaller datasets
- Minimal setup

### Run It:
```bash
python flight_trajectory_display.py
```

---

## 🚀 PyVista Version
**File:** `flight_trajectory_display_pyvista.py`

### Pros:
- ✅ **GPU-accelerated** - very smooth rendering
- ✅ **Handles 10,000+ points** easily
- ✅ **Professional quality** - VTK-based (used by NASA)
- ✅ **Better performance** for real-time data
- ✅ **Interactive 3D** - rotate, zoom, pan effortlessly

### Cons:
- ⚠️ **Requires installation**: `pip install pyvista pyvistaqt PyQt5`
- ⚠️ **3D only** - no 2D plane views
- ⚠️ **Separate control window** - 3D plot in one window, controls in another

### Best For:
- Long simulations with lots of data
- When matplotlib 3D is too slow
- Professional presentations
- Maximum visual quality

### Install:
```bash
pip install pyvista pyvistaqt PyQt5
```

### Run It:
```bash
python flight_trajectory_display_pyvista.py
```

---

## Feature Comparison Table

| Feature | Matplotlib | PyVista |
|---------|-----------|---------|
| 2D Views | ✅ Yes | ❌ No |
| 3D View | ✅ Yes | ✅ Yes |
| GPU Acceleration | ❌ No | ✅ Yes |
| Max Points (smooth) | ~500 | 10,000+ |
| Dependencies | Minimal | Requires PyVista |
| Window Layout | Single window | Dual window |
| Rotation/Zoom | Manual controls | Click & drag |
| CSV Export | ✅ Yes | ✅ Yes |
| Auto-save | ✅ Yes | ✅ Yes |
| Installation | Easy | Moderate |

---

## Recommendations

### 🎯 Try This First:
1. **Start with Matplotlib** version - it's already installed
2. Test it with your simulation data
3. If the 3D view is choppy or slow, **switch to PyVista**

### 🔧 Installation Steps for PyVista:

```bash
# Install PyVista and dependencies
pip install pyvista pyvistaqt PyQt5

# Or uncomment the PyVista lines in requirements.txt, then:
pip install -r requirements.txt

# Run the PyVista version
python flight_trajectory_display_pyvista.py
```

---

## Both Versions Include:

✅ Real-time connection to Trick Variable Server  
✅ Position, velocity, acceleration tracking  
✅ Auto-save to CSV on disconnect  
✅ Manual "Save Data" button  
✅ Zoom controls  
✅ Clear trajectory button  
✅ Live statistics display  
✅ Speed calculations  

---

## CSV Output Format

Both versions create identical CSV files:

```csv
Time (UTC sec),Position X (m),Position Y (m),Position Z (m),Velocity X (m/s),...
0.0,6578137.0,0.0,0.0,0.0,7784.5,0.0,...
0.02,6578137.0,155.69,0.0,0.0,7784.3,0.0,...
...
```

Filename: `orion_trajectory_YYYY-MM-DD_HH-MM-SS.csv`

---

## Questions?

**"Which one should I use?"**
- Start with **Matplotlib** (easier)
- Switch to **PyVista** if you need better performance

**"Can I use both?"**
- Yes! They're completely independent
- Same data source, different visualization

**"Is PyVista hard to install?"**
- Just one pip command: `pip install pyvista pyvistaqt PyQt5`
- Takes about 1-2 minutes to install

**"Will my CSV files be the same?"**
- Yes, identical format from both versions

---

Enjoy your trajectory visualization! 🚀


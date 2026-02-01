# LinuxCNC MESA Stepgen Calculator - Usage Guide

## Quick Start

1. **Edit the script** - Open `linuxcnc_mesa_calculator.py` in a text editor
2. **Update the values** at the top of the file (lines 10-35)
3. **Run the script**: `python3 linuxcnc_mesa_calculator.py`
4. **Copy/paste** the output into your INI and HAL files

## What to Edit

### Required Values (you MUST change these):

```python
# Motor & Drive Specifications
MOTOR_STEPS_PER_REV = 200      # Your motor (200 or 400 typically)
MICROSTEPPING = 8               # Your driver setting (1, 2, 4, 8, 16, etc.)
LEAD_SCREW_PITCH = 5.0          # mm per revolution (or inches)
GEAR_RATIO = 1.0                # Motor:Screw ratio (2:1 = 2.0, 1:1 = 1.0)

# Driver Timing - CHECK YOUR DRIVER DATASHEET!
STEPLEN = 2500                  # Minimum step pulse width (ns)
STEPSPACE = 2500                # Minimum time between steps (ns)
DIRSETUP = 10000                # Time before direction change (ns)
DIRHOLD = 10000                 # Time after direction change (ns)

# What you want your machine to do
DESIRED_MAX_VELOCITY = 100.0    # mm/s (or inches/s)
DESIRED_MAX_ACCELERATION = 500.0 # mm/s²
```

### Optional Values (good defaults, but you can tune):

```python
# Safety & Headroom
SAFETY_FACTOR = 0.95            # Use 95% of theoretical max
STEPGEN_HEADROOM = 1.25         # 1.25 = 25% headroom (minimum)
                                # 2.0 = 100% headroom (use with backlash)

# Multi-axis
NUM_AXES_SIMULTANEOUS = 2       # 2 for XY, 3 for XYZ moves

# Machine info
MACHINE_NAME = "My CNC Mill"
AXIS_NAME = "X"                 # X, Y, Z, A, etc.
JOINT_NUM = 0                   # 0, 1, 2, 3, etc.
UNITS = "mm"                    # "mm" or "inch"
```

## Finding Driver Timing Values

### Check Your Driver Datasheet

Look for these specifications:
- **Pulse width** or **Step width** → STEPLEN
- **Pulse space** or **Minimum step time** → STEPSPACE
- **Direction setup time** → DIRSETUP
- **Direction hold time** → DIRHOLD

### Common Driver Examples:

**TB6600 (typical Chinese drivers):**
```python
STEPLEN = 2500      # 2.5 µs
STEPSPACE = 2500    # 2.5 µs
DIRSETUP = 5000     # 5 µs
DIRHOLD = 5000      # 5 µs
```

**Leadshine DM542/DM556:**
```python
STEPLEN = 2500      # 2.5 µs
STEPSPACE = 2500    # 2.5 µs
DIRSETUP = 5000     # 5 µs
DIRHOLD = 5000      # 5 µs
```

**Gecko G540:**
```python
STEPLEN = 500       # 0.5 µs (very fast)
STEPSPACE = 4000    # 4 µs
DIRSETUP = 1000     # 1 µs
DIRHOLD = 1000      # 1 µs
```

**ClearPath or modern servos with step/dir:**
```python
STEPLEN = 1000      # 1 µs
STEPSPACE = 1000    # 1 µs
DIRSETUP = 2000     # 2 µs
DIRHOLD = 2000      # 2 µs
```

### Conservative Default (works with most drivers):
```python
STEPLEN = 5000      # 5 µs - very safe
STEPSPACE = 5000    # 5 µs
DIRSETUP = 20000    # 20 µs
DIRHOLD = 20000     # 20 µs
```

## Motor Maximum Frequency Limits

### Understanding Motor Step Rate Limits

**The Truth About Motor Datasheets:**
Motor datasheets typically specify a "maximum step rate" that is VERY conservative. For example:
- NEMA 17 datasheet: 1000 steps/s
- NEMA 23 datasheet: 2000-5000 steps/s
- NEMA 34 datasheet: 3000-10000 steps/s

**Reality with Modern Drivers and Microstepping:**
With good drivers and microstepping, motors can typically handle **10-50× their datasheet limit**. For example:
- NEMA 23 with 8× microstepping can easily handle 100-200 kHz
- This is 20-40× the datasheet "maximum"

### When to Set MOTOR_MAX_STEP_RATE

**Set to 0 (recommended for most users):**
```python
MOTOR_MAX_STEP_RATE = 0  # No motor limit check
```
Use this unless you have a specific reason to limit motor frequency.

**Set to datasheet value (very conservative):**
```python
# NEMA 23 datasheet says 5000 steps/s
MOTOR_MAX_STEP_RATE = 5000
```
This will severely limit your speed, but guarantees you're within spec.

**Set to tested value (recommended if limiting):**
```python
# Tested my NEMA 23 and it handles 80kHz before stalling
MOTOR_MAX_STEP_RATE = 80000
```

### How to Test Your Motor's Real Limit

1. **Start conservative** (e.g., 10,000 steps/s)
2. **Set up a test** with the calculator
3. **Gradually increase DESIRED_MAX_VELOCITY**
4. **Run the machine** and watch for:
   - Missed steps (position errors)
   - Excessive vibration
   - Motor stalling
   - Unusual noise
5. **Find the failure point**
6. **Back off 20-30%** from failure
7. **Set MOTOR_MAX_STEP_RATE** to this safe value

### Example: Testing a NEMA 23

```python
# Initial test
MOTOR_MAX_STEP_RATE = 10000
DESIRED_MAX_VELOCITY = 31.25  # Results in 10,000 steps/s
# Run machine - works fine

# Increase
MOTOR_MAX_STEP_RATE = 50000
DESIRED_MAX_VELOCITY = 156.25  # Results in 50,000 steps/s
# Run machine - works fine

# Keep increasing
MOTOR_MAX_STEP_RATE = 100000
DESIRED_MAX_VELOCITY = 312.5  # Results in 100,000 steps/s
# Run machine - starts to stall at high speeds

# Back off
MOTOR_MAX_STEP_RATE = 80000  # 20% below failure point
DESIRED_MAX_VELOCITY = 250.0  # Results in 80,000 steps/s
# Run machine - reliable
```

### What Usually Limits You

**Priority order (most to least restrictive):**

1. **MESA Timing** (STEPLEN + STEPSPACE)
   - Usually allows 100-500 kHz
   - This is your primary limit with conservative timing
   
2. **Motor Torque at Speed**
   - Motors lose torque at high RPM
   - You'll mechanically stall before frequency limit
   
3. **Driver Capability**
   - Modern drivers handle 200+ kHz easily
   - Rarely the limiting factor
   
4. **Motor Frequency Limit**
   - Usually NOT the limit with microstepping
   - Only matters for very old or very cheap motors

### Recommendation

**For most users:**
```python
MOTOR_MAX_STEP_RATE = 0  # Don't limit by motor frequency
```

Your actual limits will be:
- MESA timing (hardware)
- Motor torque (mechanical - you'll stall before frequency limit)
- Mechanical rigidity (vibration, accuracy)

**Only set a motor limit if:**
- You have unusually low-frequency motors
- You've tested and found a specific limit
- You're being extremely conservative for safety-critical application

## BASE_PERIOD vs MESA Hardware Limits

### Understanding Step Generation on MESA Boards

**CRITICAL: BASE_PERIOD is IRRELEVANT for MESA Ethernet/PCI boards!**

**For Parallel Port (software stepping):**
- BASE_PERIOD determines how often the CPU toggles step/dir pins
- Typically 25-50µs (25000-50000ns)
- CPU must generate every step pulse
- Affected by PC latency and jitter

**For MESA Boards (hardware stepping):**
- Steps are generated by **FPGA hardware** on the MESA board
- FPGA runs at ~10MHz+ internal clock
- BASE_PERIOD in INI file is **ignored/not used**
- Only SERVO_PERIOD matters (how often position updates are sent)

### What Actually Limits Step Rate on MESA?

**The ONLY limit is STEPLEN + STEPSPACE:**

```
Maximum Step Rate (Hz) = 1,000,000,000 / (STEPLEN + STEPSPACE)
```

**Example Calculations:**

Conservative timing (STEPLEN=5000, STEPSPACE=5000):
- Max rate = 1,000,000,000 ÷ 10,000 = **100,000 steps/s (100 kHz)**

Fast timing (STEPLEN=1000, STEPSPACE=1000):
- Max rate = 1,000,000,000 ÷ 2,000 = **500,000 steps/s (500 kHz)**

**The calculator automatically validates your desired velocity against this FPGA hardware limit. You do NOT need to separately check BASE_PERIOD.**

### Why You Might See BASE_PERIOD in Your INI

It's a legacy parameter that LinuxCNC requires in the config file, but for MESA boards it has no effect on step generation. The value doesn't matter - could be 100000, 200000, or any valid number.

**What Actually Matters:**
1. ✅ **STEPLEN + STEPSPACE** (checked by calculator) - FPGA step timing
2. ✅ **SERVO_PERIOD** (typically 1000000ns) - position update rate
3. ❌ **BASE_PERIOD** - ignored for MESA boards

## Example Workflow

### For X Axis:

1. Edit script:
```python
MOTOR_STEPS_PER_REV = 200
MICROSTEPPING = 8
LEAD_SCREW_PITCH = 5.0
GEAR_RATIO = 1.0
DESIRED_MAX_VELOCITY = 100.0
AXIS_NAME = "X"
JOINT_NUM = 0
```

2. Run: `python3 linuxcnc_mesa_calculator.py > x_axis_config.txt`

3. Copy the INI section into your machine.ini file

4. Copy the HAL section into your custom.hal file

### For Y Axis:

1. Edit script:
```python
AXIS_NAME = "Y"
JOINT_NUM = 1
# Keep other values the same if Y is identical to X
# OR change LEAD_SCREW_PITCH, DESIRED_MAX_VELOCITY, etc. if different
```

2. Run: `python3 linuxcnc_mesa_calculator.py > y_axis_config.txt`

3. Copy/paste into your files

### For Z Axis (typically slower):

1. Edit script:
```python
DESIRED_MAX_VELOCITY = 50.0     # Z is usually slower
DESIRED_MAX_ACCELERATION = 200.0
AXIS_NAME = "Z"
JOINT_NUM = 2
```

2. Run: `python3 linuxcnc_mesa_calculator.py > z_axis_config.txt`

## Understanding the Output

### Validation Checks

The script performs three critical checks:

✓ **StepGen Headroom: 1.25x PASS**
- StepGen must run at least 25% faster than axis
- If FAIL: Increase STEPGEN_HEADROOM

✓ **StepGen vs Hardware: 0.21 PASS**
- StepGen velocity must be under hardware limit
- If FAIL: Reduce DESIRED_MAX_VELOCITY or improve timing

✓ **Step Rate: 40,000 steps/s (20% of max) PASS**
- Shows how much of hardware capacity you're using
- Ideally 60-95%
- <20% means you can go much faster if needed
- >95% means you're pushing limits

### Quick Reference Section

```
Position Scale:      320.0000 steps/mm
Resolution:          0.003125 mm/step      ← Your machine precision
Max Step Rate:       200,000 steps/s       ← Hardware limit
Axis Max Velocity:   100.00 mm/s (6000 mm/min)
StepGen Max Vel:     125.00 mm/s (7500 mm/min)
Headroom Factor:     1.25x (25% extra)
Hardware Utilization: 20.0%                 ← How much you're using
```

## Common Issues

### "WARNING: Desired velocity exceeds hardware capability!"

**Problem:** You want to go faster than your timing allows

**Solutions:**
1. Reduce STEPLEN and STEPSPACE (check driver datasheet first!)
2. Reduce microstepping (e.g., 8 → 4)
3. Use larger pitch lead screw
4. Accept slower maximum velocity

### "ERROR: STEPGEN_MAXVEL exceeds hardware limit!"

**Problem:** Your headroom factor pushes you over the limit

**Solutions:**
1. Reduce DESIRED_MAX_VELOCITY
2. Reduce STEPGEN_HEADROOM (but keep ≥1.25)
3. Improve timing parameters (if driver allows)

### "StepGen Headroom: 1.10x ✗ FAIL"

**Problem:** Not enough headroom for PID loop

**Solution:**
- Increase STEPGEN_HEADROOM to at least 1.25

## Tips

### For Each Axis

Run the calculator separately for each axis:
- X axis might be fast (100 mm/s)
- Y axis might be fast (100 mm/s)
- Z axis typically slower (50 mm/s)
- A/B/C rotary axes in degrees/s

### Headroom Factor Choice

- **1.25 (25%)**: Minimum, standard for most machines
- **1.5 (50%)**: Better, more margin
- **2.0 (100%)**: Required with BACKLASH compensation

### Testing Acceleration

The script can't know your actual acceleration limits. To find them:

1. Start conservative (e.g., 100 mm/s²)
2. Gradually increase while jogging
3. Watch for:
   - Missed steps
   - Excessive vibration
   - Parts shifting
4. Back off 20-30% from failure point
5. Update DESIRED_MAX_ACCELERATION in script

## Complete Example

### 3-Axis Mill Setup

**Specifications:**
- NEMA 23 motors, 200 steps/rev
- 8× microstepping
- 5mm pitch ball screws on all axes
- TB6600 drivers
- Z axis geared 2:1 for more torque

**X Axis:**
```python
MOTOR_STEPS_PER_REV = 200
MICROSTEPPING = 8
LEAD_SCREW_PITCH = 5.0
GEAR_RATIO = 1.0
STEPLEN = 2500
STEPSPACE = 2500
DIRSETUP = 5000
DIRHOLD = 5000
DESIRED_MAX_VELOCITY = 100.0
DESIRED_MAX_ACCELERATION = 500.0
AXIS_NAME = "X"
JOINT_NUM = 0
```

**Y Axis (same as X):**
```python
# Same as X, just change:
AXIS_NAME = "Y"
JOINT_NUM = 1
```

**Z Axis (geared and slower):**
```python
MOTOR_STEPS_PER_REV = 200
MICROSTEPPING = 8
LEAD_SCREW_PITCH = 5.0
GEAR_RATIO = 2.0              # 2:1 gearing for torque
STEPLEN = 2500
STEPSPACE = 2500
DIRSETUP = 5000
DIRHOLD = 5000
DESIRED_MAX_VELOCITY = 50.0   # Slower on Z
DESIRED_MAX_ACCELERATION = 200.0
AXIS_NAME = "Z"
JOINT_NUM = 2
```

Run the script 3 times (once per axis) and combine the outputs into your configuration!

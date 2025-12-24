# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **LinuxCNC configuration for a CNC plasma cutting machine** using QtPlasmaC (Qt-based plasma cutting control interface). The project consists of HAL (Hardware Abstraction Layer) configuration files and utilities that define how the LinuxCNC controller interfaces with plasma cutter hardware.

**Hardware Stack:**
- MESA 7i95T Ethernet FPGA motion control board (10.10.10.10)
- 4-axis stepper system: XYYZ gantry (dual Y motors)
- 2x THCAD-2 boards for arc voltage and ohmic sensing
- XHC-WHB04B-6 wireless pendant (USB)
- Open loop, 4 wire stepper motors - 23HE45 (NEMA 23, 3.0Nm, 4.2A)
- CW5045 stepper drivers (4.5A, 24-50VDC, microstepping)

**Key Technologies:**
- LinuxCNC real-time CNC controller
- HAL (Hardware Abstraction Layer) component system
- QtPlasmaC GUI (QtVCP-based interface)
- Python 3 for utilities and M-code scripts
- TCL for HAL scripting

**Design decisions:**
- Single switch for all home and limit
- No homing of Z axis

## Documentation

**LinuxCNC:**
- https://linuxcnc.org/docs/stable/html/
- https://linuxcnc.org/docs/html/plasma/qtplasmac.html

**Hardware:**
- Stepper motor: https://www.stepperonline.co.uk/e-series-nema-23-bipolar-1-8deg-3-0nm-425oz-in-4-2a-57x57x113mm-4-wires-23he45-4204s.html
- Stepper driver: https://www.cnc4you.co.uk/Stepper-Motor-Driver-4.5A,-50V-CNC-Microstepping-CW5045
- CW5045 Datasheet: https://cnc4you.co.uk/resources/CW5045.pdf
- MESA 7i95T: https://www.mesanet.com/pdf/parallel/7i95tman.pdf
- THCAD-2: https://www.mesanet.com/pdf/analog/thcad2man.pdf
- XHC-WHB04B-6: https://linuxcnc.org/docs/2.8/html/man/man1/xhc-whb04b-6.1.html

**Plasma Specific:**
- Plasma CNC Primer: https://linuxcnc.org/docs/html/plasma/plasma-cnc-primer.html
- Ohmic sensing: https://linuxcnc.org/docs/2.9/html/plasma/plasma-cnc-primer.html#_initial_height_sensing

## Current Known Issues / Limitations

### Hardware Limitations
- Only a single switch for limits and float switch
- No positive limit switches
- Open loop steppers (no encoder feedback)

### Configuration Issues Requiring Attention

**CRITICAL (Must fix before running machine):**
1. **Z-axis STEPGEN_MAX_ACC corrupted** (qtplasmac.ini:277)
   - Current: `STEPGEN_MAX_ACC = 900/clke`
   - Fix: Should be `STEPGEN_MAX_ACC = 900`
   - Impact: Will cause LinuxCNC parsing error or unpredictable behavior

**Important (Should fix for consistency):**
2. **Acceleration headroom comment mismatch** (qtplasmac.ini:132, 184, 225)
   - Current: STEPGEN_MAX_ACC=1080 with comment "20% on the max value"
   - Reality: 1080/800 = 1.35 (35% headroom, not 20%)
   - Fix: Update comment to "35% headroom" OR change value to 960 (true 20%)
   - Recommendation: Keep 1080, fix comment (extra margin is good for open-loop)

3. **TRAJ MAX_LINEAR_VELOCITY inconsistency** (qtplasmac.ini:105)
   - Current: TRAJ=350 but AXIS_X/Y max=300
   - Fix: Change TRAJ MAX_LINEAR_VELOCITY to 300 for consistency
   - Impact: System clamps to 300 anyway; just confusing

**Already Fixed (Good work!):**
- ✅ SERVO_PERIOD now 1000000ns (was 1500000) - optimal for 7i95T
- ✅ STEPLEN/STEPSPACE now 10000ns for all joints - meets CW5045 spec
- ✅ DIRSETUP 5000ns meets minimum requirements

**Consider (Optional):**
4. Current velocities are conservative (appropriate for plasma cutting)
   - X/Y at 150mm/s uses ~10-25% of motor capability
   - Could increase to 200-250mm/s for faster rapids if desired
   - Recommendation: Keep conservative for reliability and cut quality

## Architecture

### Configuration Hierarchy

```
qtplasmac.ini                 # Main configuration (motion, display, plasma parameters)
├── mesa.hal                  # Hardware setup (MESA board, I/O, THCAD, sensors)
├── qtplasmac_comp.hal        # QtPlasmaC component connections
└── pendant.hal               # Optional wireless pendant interface
```

### HAL Component Flow

```
THCAD Boards → MESA Encoders → HAL Components → plasmac → Motion Control
                                    ↓                ↓
                               ohmicsense        thc (torch height)
                                    ↓                ↓
USB Pendant → xhc-whb04b-6 ─────→ HAL ──────────→ Motion/GUI
                                    ↓
G-code → custom_filter.py → plasmac_gcode → Motion → MESA → Steppers
```

### Key HAL Components

- **plasmac**: Main plasma control (arc voltage, THC, cut sequencing)
- **thc**: Torch Height Controller (move-up/move-down generation)
- **ohmicsense**: Conductive height sensing via THCAD
- **dbounce** (x4): Input debouncing for float, ohmic, breakaway, arc-ok
- **pid** (x4): Position control loops per joint (X, Y0, Y1, Z)
- **lut5**: Home/limit switch logic disambiguation

### File Organization

**Root Configuration Files:**
- `qtplasmac.ini`: Main INI with all parameters (302 lines)
- `mesa.hal`: MESA hardware interface (357 lines)
- `qtplasmac_comp.hal`: Component connections (52 lines)
- `pendant.hal`: Wireless pendant setup (165 lines)
- `machine.tcl`: HAL simulation scripting (114 lines)

**Runtime Files:**
- `qtplasmac-metric.prefs`: User GUI preferences
- `qtplasmac-metric_material.cfg`: Materials database
- `metric_tool.tbl`: Tool table

**Custom Scripts:**
- `M190`: Material change M-code (Python, uses halcmd)
- `custom_filter.py`: G-code preprocessing hooks (pre/post parse)

**Utilities:**
- `utils/thcad_calc.py`: THCAD calibration calculator

**Setup:**
- `setup/`: udev rules for USB pendant

## Development Commands

### THCAD Calibration

Calculate scale/offset parameters for THCAD boards:

```bash
uv run utils/thcad_calc.py
```

Edit `boards` list in `thcad_calc.py` with actual frequency measurements from THCAD LEDs, then run to get scale/offset values for `qtplasmac.ini` or GUI parameters screen.

### HAL Testing

Test HAL configurations without running full LinuxCNC:

```bash
halrun                          # Start HAL runtime
loadusr xhc-whb04b-6 -uek      # Test pendant (with -uek for extended keys)
```

Query/modify HAL pins (used in M190 script):

```bash
halcmd getp qtplasmac.material_change_number
halcmd setp qtplasmac.material_change_number 5
```

### Network Testing

Check MESA board connectivity (critical for real-time performance):

```bash
ping -i .2 -c 4 10.10.10.10                    # Basic latency check
sudo chrt 99 ping -i .001 -q 10.10.10.10       # Real-time latency test (run for several minutes)
```

### Latency Testing

Test system real-time performance (required before running machine):

```bash
latency-histogram --nobase --sbinsize 1000
```

### USB Device Detection

Check pendant connection:

```bash
sudo lsusb                     # Look for "Silicon Labs" manufacturer
```

## Stepper Driver Specifications (CW5045)

**Electrical:**
- Input voltage: 24-50VDC
- Output current: 1.3-4.5A (adjustable)
- Microstepping: 1, 1/2, 1/4, 1/8, 1/16, 1/32, 1/64, 1/128, 1/256

**Critical Timing Requirements:**
- **Minimum step pulse width: 10µs** (STEPLEN parameter)
- **Minimum step pulse spacing: 10µs recommended** (STEPSPACE parameter)
- Direction setup/hold: 5µs minimum (DIRSETUP, DIRHOLD parameters)

**Current Configuration (verify on physical drivers):**
- X/Y axes: 50.93 steps/mm suggests ~8x microstepping (with 5mm pitch) or ~4x (with 10mm pitch)
- Z axis: 800 steps/mm suggests ~16x microstepping (with 4mm pitch leadscrew)

**Current Configuration Status:**
- ✅ STEPLEN/STEPSPACE now correctly set to 10000ns (10µs) - meets specification
- ✅ DIRSETUP=5000ns, DIRHOLD=10000ns - exceeds 5µs minimum requirement
- ⚠️ Verify microstepping DIP switch settings match calculated values below

## Critical Configuration Notes

### THCAD Parameters

IMPORTANT: If using QtPlasmaC, offset/scale parameters are set in the GUI Parameters screen. The values in HAL files are ignored. Always enable "ohmic probe enable" in GUI if using ohmic sensing.

**Current Configuration:**
- Board 1 (Arc Voltage): F0=100.4kHz, FFS=904.9kHz, 5V scale, 40:1 divider
- Board 2 (Ohmic): F0=101.2kHz, FFS=904.4kHz, 5V scale, 1:1 divider
- Frequency divider: 32 (recommended for QtPlasmaC)

### Network Configuration

MESA board requires dedicated Ethernet interface:
- Board IP: 10.10.10.10
- Host IP: 10.10.10.1
- No gateway on this interface

### BIOS Requirements

For real-time performance, disable in BIOS:
- Secure boot
- All power management (turbo modes, EIST, C-states > C1, Cool&Quiet)
- Hyperthreading
- Management engine network options (AMT)
- IRQ coalescing (Intel Ethernet)

### Machine Specifications

**Axes Configuration (qtplasmac.ini):**

X-axis (JOINT_0):
- Travel: 0-550mm
- MAX_VELOCITY: 150 mm/s (STEPGEN_MAX_VEL: 180 mm/s)
- MAX_ACCELERATION: 800 mm/s² (STEPGEN_MAX_ACC: 1080 mm/s²)
- SCALE: 50.93 steps/mm
- Homing: Shared switch, negative direction, HOME_SEQUENCE=0

Y-axis (JOINT_1, JOINT_2 - dual motor gantry):
- Travel: 0-550mm
- MAX_VELOCITY: 150 mm/s (STEPGEN_MAX_VEL: 180 mm/s)
- MAX_ACCELERATION: 800 mm/s² (STEPGEN_MAX_ACC: 1080 mm/s²)
- SCALE: 50.93 steps/mm
- Homing: Shared switch, negative direction, HOME_SEQUENCE=-1 (simultaneous)

Z-axis (JOINT_3):
- Travel: -200 to +200mm
- MAX_VELOCITY: 75 mm/s (STEPGEN_MAX_VEL: 90 mm/s)
- MAX_ACCELERATION: 750 mm/s² (STEPGEN_MAX_ACC: 900 mm/s²)
- SCALE: 800 steps/mm
- Homing: Disabled (HOME_SEQUENCE=2, but no homing motion)

**Motion Control:**
- BASE_PERIOD: 80000ns (not used for Ethernet MESA)
- SERVO_PERIOD: 1000000ns (1ms = 1kHz servo thread) ✅ Optimal
- Step timing: STEPLEN=10000ns, STEPSPACE=10000ns ✅ Meets CW5045 spec
- Direction timing: DIRSETUP=5000ns, DIRHOLD=10000ns ✅ Exceeds 5µs minimum

**PID Parameters (all joints):**
- P=1000, I=0, D=0, FF1=1 (standard stepper configuration)
- FERROR=0.5mm, MIN_FERROR=0.05mm

**Plasma Parameters:**
- Max torch voltage: 200V
- Arc voltage scale: 0.009944
- Arc voltage offset: 3137.5
- Height per volt: 0.1mm

**Performance Notes:**
- Current velocities are conservative (motors capable of 1000-1500 RPM)
- X/Y at 150mm/s = ~287 RPM @ 8x microstep or ~143 RPM @ 16x (only ~10-25% motor capability)
- Z at 75mm/s = ~750 RPM @ 16x microstep or ~375 RPM @ 32x (moderate utilization)
- Open loop system means no feedback if steps are lost
- Conservative settings prioritize reliability and cut quality over speed
- Could increase X/Y to 200-250mm/s for faster rapids if desired (test incrementally)

## Python Code Style

Follow standard Python conventions:
- Type hints for all functions
- Docstrings for public APIs
- snake_case for functions/variables
- Line length: 88 characters max

When modifying utilities:
- `M190` uses subprocess to call halcmd
- `custom_filter.py` provides hooks via method attachment (see comments in file)
- `thcad_calc.py` is a simple calculator script

## HAL Signal Conventions

HAL files use declarative signal routing between component pins:

```
net signal-name component.pin-out => component.pin-in
setp component.parameter value
```

All physical inputs are debounced via `dbounce` components with appropriate delays (typically 10-15ms).

## QtPlasmaC GUI

Enable keyboard shortcuts in Settings page for keyboard jogging.

Material changes can be triggered via:
1. GUI material selector
2. M190 P# command in G-code (# = material number)

## Configuration Tuning Guide

### Stepper Timing Parameters

**Current Status:** ✅ Correctly configured at 10000ns

**When to adjust STEPLEN/STEPSPACE:**
- ✅ Currently at 10µs (10000ns) - meets CW5045 requirements
- Can increase to 15000-20000ns if experiencing electrical noise
- Must never decrease below 10µs driver specification

**When to adjust velocities:**
- Test incrementally: start conservative, increase 10% at a time
- Monitor for missed steps (check positioning accuracy)
- Consider: plasma cutting rarely needs high rapids
- X/Y could potentially run 250-350 mm/s if torque sufficient
- Z is already fairly aggressive at 75 mm/s for 800 steps/mm

**When to adjust accelerations:**
- Match velocity increases with proportional acceleration increases
- Maintain 20% headroom for STEPGEN_MAX_ACC
- Listen for motor stalling or grinding
- Reduce if experiencing positioning errors

### Servo Thread Timing

**Current Configuration:** SERVO_PERIOD = 1000000ns (1ms = 1kHz) ✅

Standard SERVO_PERIOD values for 7i95T:
- 1000000ns (1.0ms): Standard recommendation ⬅️ **You are here**
- 500000ns (0.5ms): Aggressive (better THC response, requires low-latency system)

Your system is now optimally configured. Only consider reducing to 500000ns if:
1. Latency testing shows max jitter < 200µs consistently
2. You need improved THC response time
3. After running: `latency-histogram --nobase --sbinsize 1000` for several minutes

### PID Tuning

Current FF1=1 configuration works for most steppers. Tune if:
- Position errors during motion (increase FF1 slightly)
- Oscillation at end of moves (reduce P gain)
- Sluggish response (increase P gain)

#!/usr/bin/env python3
"""
LinuxCNC MESA Hardware Stepgen Configuration Calculator
Simple script to calculate all parameters and print INI/HAL configuration strings
"""
import math

# ============================================================================
# USER INPUTS - EDIT THESE VALUES FOR YOUR MACHINE
# ============================================================================

# Spur gear
SPUR_GEAR_TEETH = 20          # Number of teeth on the spur gear
SPUR_GEAR_MOD = 1.0             # Module of the spur gear (mm) or Diametral Pitch (inches)

# Calculate Spur Gear Circumference
SPUR_GEAR_CIRCUMFERENCE = SPUR_GEAR_TEETH * (math.pi * SPUR_GEAR_MOD)  # mm or inches




# Motor & Drive Specifications
MOTOR_STEPS_PER_REV = 200      # Typically 200 for 1.8° or 400 for 0.9° motors
MICROSTEPPING = 16               # Driver microstepping (1, 2, 4, 8, 16, 32, etc.)
LEAD_SCREW_PITCH = SPUR_GEAR_CIRCUMFERENCE          # mm or inches per revolution
GEAR_RATIO = 1.0                # Motor:Screw ratio (e.g., 2:1 = 2.0, 1:1 = 1.0)

# MESA Hardware Stepgen Timing (nanoseconds)
# Check your driver datasheet - these are conservative defaults
STEPLEN = 2000                  # Step pulse width (ns) - typical 1000-5000
STEPSPACE = 8000                # Step pulse space (ns) - typical 1000-5000
DIRSETUP = 5000                 # Direction setup time (ns) - typical 5000-20000
DIRHOLD = 5000                  # Direction hold time (ns) - typical 5000-20000

# Desired Machine Performance
DESIRED_MAX_VELOCITY = 150.0    # mm/s (or inches/s) - what speed you want
DESIRED_MAX_ACCELERATION = DESIRED_MAX_VELOCITY * 10 # mm/s² (or inches/s²)

# Motor Maximum Step Rate (check motor datasheet!)
# Typical values:
#   - NEMA 17: 1000-2000 steps/s per datasheet spec
#   - NEMA 23: 2000-5000 steps/s per datasheet spec (can often do 200kHz with microstepping)
#   - NEMA 34: 3000-10000 steps/s base, higher with microstepping
#   - Set to 0 to disable motor limit check
MOTOR_MAX_STEP_RATE = 0         # steps/s (0 = no limit, or specify motor datasheet limit)
                                # NOTE: This is often much lower than what motors can actually do
                                # with modern drivers. Conservative: use datasheet value.
                                # Realistic: Test and find actual limit, often 10-50x higher.

# Safety & Headroom Factors
SAFETY_FACTOR = 0.95            # Use 95% of theoretical max (0.90-0.95 recommended)
STEPGEN_HEADROOM = 1.25         # StepGen runs 25% faster (1.25-2.0, use 2.0 with backlash)

# Multi-Axis Motion (for TRAJ calculations)
NUM_AXES_SIMULTANEOUS = 2       # 2 for XY, 3 for XYZ diagonal moves

# Units
UNITS = "mm"                    # "mm" or "inch"

# Machine Name (for comments in output)
MACHINE_NAME = "CNC-Plasma"
AXIS_NAME = "X"                 # Which axis is this for? (X, Y, Z, A, etc.)
JOINT_NUM = 0                   # Which joint number? (0, 1, 2, etc.)

# ============================================================================
# CALCULATIONS - DO NOT EDIT BELOW THIS LINE
# ============================================================================

import math

print("=" * 80)
print(f"LinuxCNC MESA Hardware Stepgen Configuration Calculator")
print(f"Machine: {MACHINE_NAME} - Axis: {AXIS_NAME} / Joint: {JOINT_NUM}")
print("=" * 80)
print()

# Calculate mechanical values
total_steps_per_rev = MOTOR_STEPS_PER_REV * MICROSTEPPING
effective_lead = LEAD_SCREW_PITCH / GEAR_RATIO
position_scale = total_steps_per_rev / effective_lead
resolution = 1.0 / position_scale

print("MECHANICAL CALCULATIONS:")
print("-" * 80)
print(f"Total Steps per Revolution:     {total_steps_per_rev:,.0f} steps/rev")
print(f"Effective Lead (with gearing):  {effective_lead:.4f} {UNITS}/rev")
print(f"POSITION_SCALE:                 {position_scale:.4f} steps/{UNITS}")
print(f"Resolution (step size):         {resolution:.6f} {UNITS}")
print()

# Calculate MESA hardware limits
# NOTE: For MESA Ethernet/PCI boards, step generation happens in FPGA hardware.
# BASE_PERIOD (used for parallel port software stepping) is IRRELEVANT.
# The ONLY limit is the FPGA step timing: STEPLEN + STEPSPACE
# The FPGA can generate steps continuously at this rate regardless of PC latency.
min_step_time_ns = STEPLEN + STEPSPACE
max_step_rate_hw = 1_000_000_000 / min_step_time_ns  # FPGA hardware step limit
max_vel_hw = max_step_rate_hw / position_scale

# Apply motor limit if specified
if MOTOR_MAX_STEP_RATE > 0:
    max_step_rate_motor = MOTOR_MAX_STEP_RATE
    max_vel_motor = max_step_rate_motor / position_scale
    max_step_rate = min(max_step_rate_hw, max_step_rate_motor)
    max_vel_theoretical = min(max_vel_hw, max_vel_motor)
    limiting_factor = "motor" if max_step_rate_motor < max_step_rate_hw else "hardware timing"
else:
    max_step_rate_motor = None
    max_vel_motor = None
    max_step_rate = max_step_rate_hw
    max_vel_theoretical = max_vel_hw
    limiting_factor = "hardware timing"

max_vel_safe = max_vel_theoretical * SAFETY_FACTOR

print("MESA HARDWARE LIMITS:")
print("-" * 80)
print(f"Minimum Time per Step:          {min_step_time_ns:,.0f} ns")
print(f"Maximum Step Rate (hardware):   {max_step_rate_hw:,.0f} steps/s ({max_step_rate_hw/1000:.1f} kHz)")
print(f"Maximum Velocity (from HW):     {max_vel_hw:.2f} {UNITS}/s")

if MOTOR_MAX_STEP_RATE > 0:
    print()
    print("MOTOR LIMITS:")
    print("-" * 80)
    print(f"Motor Max Step Rate (datasheet):{max_step_rate_motor:,.0f} steps/s ({max_step_rate_motor/1000:.1f} kHz)")
    print(f"Maximum Velocity (from motor):  {max_vel_motor:.2f} {UNITS}/s")
    
print()
print("EFFECTIVE LIMITS (most restrictive):")
print("-" * 80)
print(f"Limited by:                     {limiting_factor}")
print(f"Maximum Step Rate:              {max_step_rate:,.0f} steps/s ({max_step_rate/1000:.1f} kHz)")
print(f"Maximum Velocity (theoretical): {max_vel_theoretical:.2f} {UNITS}/s")
print(f"Maximum Velocity (safe 95%):    {max_vel_safe:.2f} {UNITS}/s")
print()

# Determine actual axis limits
axis_maxvel = min(DESIRED_MAX_VELOCITY, max_vel_safe)
axis_maxaccel = DESIRED_MAX_ACCELERATION

# Check if desired velocity is achievable
if DESIRED_MAX_VELOCITY > max_vel_safe:
    print("WARNING: Desired velocity exceeds hardware capability!")
    print(f"  Requested: {DESIRED_MAX_VELOCITY:.2f} {UNITS}/s")
    print(f"  Maximum:   {max_vel_safe:.2f} {UNITS}/s")
    print(f"  Using:     {axis_maxvel:.2f} {UNITS}/s")
    print()

# Calculate StepGen parameters (with headroom)
stepgen_maxvel = axis_maxvel * STEPGEN_HEADROOM
stepgen_maxaccel = axis_maxaccel * STEPGEN_HEADROOM

# Verify StepGen doesn't exceed hardware
if stepgen_maxvel > max_vel_safe:
    print("ERROR: STEPGEN_MAXVEL exceeds hardware limit!")
    print(f"  STEPGEN_MAXVEL: {stepgen_maxvel:.2f} {UNITS}/s")
    print(f"  Hardware Max:   {max_vel_safe:.2f} {UNITS}/s")
    print(f"  Solution: Reduce DESIRED_MAX_VELOCITY or increase STEPGEN_HEADROOM factor")
    print()

# Calculate TRAJ values (for multi-axis coordinated motion)
traj_multiplier = math.sqrt(NUM_AXES_SIMULTANEOUS)
traj_maxvel = axis_maxvel * traj_multiplier
traj_maxaccel = axis_maxaccel * traj_multiplier

print("AXIS/JOINT CONFIGURATION:")
print("-" * 80)
print(f"MAX_VELOCITY:                   {axis_maxvel:.2f} {UNITS}/s")
print(f"MAX_ACCELERATION:               {axis_maxaccel:.2f} {UNITS}/s²")
print()

print("STEPGEN CONFIGURATION:")
print("-" * 80)
print(f"STEPGEN_MAXVEL:                 {stepgen_maxvel:.2f} {UNITS}/s (headroom: {STEPGEN_HEADROOM:.2f}x)")
print(f"STEPGEN_MAXACCEL:               {stepgen_maxaccel:.2f} {UNITS}/s²")
print()

print("TRAJ CONFIGURATION (for multi-axis motion):")
print("-" * 80)
print(f"Number of simultaneous axes:    {NUM_AXES_SIMULTANEOUS}")
print(f"Multiplier (√{NUM_AXES_SIMULTANEOUS}):                   {traj_multiplier:.3f}")
print(f"MAX_LINEAR_VELOCITY:            {traj_maxvel:.2f} {UNITS}/s")
print(f"MAX_LINEAR_ACCELERATION:        {traj_maxaccel:.2f} {UNITS}/s²")
print()

# Validation checks
print("VALIDATION CHECKS:")
print("-" * 80)

headroom_ratio = stepgen_maxvel / axis_maxvel
print(f"StepGen Headroom:               {headroom_ratio:.2f}x ", end="")
if headroom_ratio >= 1.25:
    print("✓ PASS (≥1.25)")
else:
    print("✗ FAIL (<1.25) - Increase STEPGEN_HEADROOM")

hw_limit_ratio = stepgen_maxvel / max_vel_safe
print(f"StepGen vs Hardware:            {hw_limit_ratio:.2f} ", end="")
if hw_limit_ratio < 1.0:
    print("✓ PASS (<1.0)")
else:
    print("✗ FAIL (≥1.0) - Exceeds hardware limits!")

actual_step_rate = stepgen_maxvel * position_scale
step_rate_pct = (actual_step_rate / max_step_rate) * 100
print(f"Step Rate at STEPGEN_MAXVEL:    {actual_step_rate:,.0f} steps/s ({step_rate_pct:.1f}% of max)")
if step_rate_pct < 100:
    print("                                ✓ PASS (<100%)")
else:
    print("                                ✗ FAIL (≥100%) - Reduce velocity!")

# Check motor frequency if specified
if MOTOR_MAX_STEP_RATE > 0:
    motor_step_rate_pct = (actual_step_rate / MOTOR_MAX_STEP_RATE) * 100
    print(f"Step Rate vs Motor Limit:       {actual_step_rate:,.0f} / {MOTOR_MAX_STEP_RATE:,.0f} ({motor_step_rate_pct:.1f}%)")
    if motor_step_rate_pct <= 100:
        print("                                ✓ PASS (≤100%)")
    else:
        print("                                ✗ FAIL (>100%) - Motor cannot handle this speed!")
        print(f"                                Maximum safe velocity: {(MOTOR_MAX_STEP_RATE / position_scale):.2f} {UNITS}/s")

# Check at axis velocity too
axis_step_rate = axis_maxvel * position_scale
print()
print(f"Step Rate at AXIS MAX_VELOCITY: {axis_step_rate:,.0f} steps/s ({axis_step_rate/1000:.1f} kHz)")

if MOTOR_MAX_STEP_RATE > 0:
    motor_axis_pct = (axis_step_rate / MOTOR_MAX_STEP_RATE) * 100
    if motor_axis_pct > 100:
        print(f"                                ⚠ WARNING: Exceeds motor limit!")
        print(f"                                Motor limit: {MOTOR_MAX_STEP_RATE:,.0f} steps/s")
        print(f"                                Reduce DESIRED_MAX_VELOCITY to {(MOTOR_MAX_STEP_RATE / position_scale):.2f} {UNITS}/s")

print()

# ============================================================================
# CONFIGURATION OUTPUT - COPY/PASTE INTO YOUR FILES
# ============================================================================

print("=" * 80)
print("INI FILE CONFIGURATION")
print("=" * 80)
print()

print("#" + "=" * 78)
print("# TRAJ Section - Trajectory Planner")
print("#" + "=" * 78)
print("[TRAJ]")
print(f"MAX_LINEAR_VELOCITY = {traj_maxvel:.2f}")
print(f"MAX_LINEAR_ACCELERATION = {traj_maxaccel:.2f}")
print()

print("#" + "=" * 78)
print(f"# AXIS_{AXIS_NAME} Section - {AXIS_NAME} Axis Limits")
print("#" + "=" * 78)
print(f"[AXIS_{AXIS_NAME}]")
print(f"MAX_VELOCITY = {axis_maxvel:.2f}")
print(f"MAX_ACCELERATION = {axis_maxaccel:.2f}")
print(f"# MIN_LIMIT = -xxx.x  # Set based on your machine")
print(f"# MAX_LIMIT = xxx.x   # Set based on your machine")
print()

print("#" + "=" * 78)
print(f"# JOINT_{JOINT_NUM} Section - Motor Driving {AXIS_NAME} Axis")
print("# NOTE: For trivkins, JOINT MAX_VELOCITY/ACCEL should MATCH AXIS values!")
print("#" + "=" * 78)
print(f"[JOINT_{JOINT_NUM}]")
print(f"TYPE = LINEAR")
print(f"MAX_VELOCITY = {axis_maxvel:.2f}")
print(f"MAX_ACCELERATION = {axis_maxaccel:.2f}")
print(f"STEPGEN_MAXVEL = {stepgen_maxvel:.2f}")
print(f"STEPGEN_MAXACCEL = {stepgen_maxaccel:.2f}")
print(f"STEP_SCALE = {position_scale:.4f}")
print(f"STEPLEN = {STEPLEN}")
print(f"STEPSPACE = {STEPSPACE}")
print(f"DIRSETUP = {DIRSETUP}")
print(f"DIRHOLD = {DIRHOLD}")
print(f"# MIN_LIMIT = -xxx.x  # Should MATCH AXIS_{AXIS_NAME} MIN_LIMIT")
print(f"# MAX_LIMIT = xxx.x   # Should MATCH AXIS_{AXIS_NAME} MAX_LIMIT")
print()
print("# Homing (configure as needed)")
print("# HOME = 0.0")
print("# HOME_OFFSET = 0.0")
print("# HOME_SEARCH_VEL = -50.0")
print("# HOME_LATCH_VEL = 1.0")
print("# HOME_IGNORE_LIMITS = YES")
print("# HOME_SEQUENCE = 1")
print()

print("=" * 80)
print("HAL FILE CONFIGURATION")
print("=" * 80)
print()
print("# Replace <board> with your MESA board name (e.g., 7i76e, 7i96, 5i25)")
print(f"# Replace XX with your stepgen number (e.g., 0{JOINT_NUM})")
print()

board = "<board>"
sg = f"0{JOINT_NUM}"
joint = f"JOINT_{JOINT_NUM}"

print(f"# StepGen Timing Parameters")
print(f"setp hm2_{board}.0.stepgen.{sg}.steplen [{joint}]STEPLEN")
print(f"setp hm2_{board}.0.stepgen.{sg}.stepspace [{joint}]STEPSPACE")
print(f"setp hm2_{board}.0.stepgen.{sg}.dirsetup [{joint}]DIRSETUP")
print(f"setp hm2_{board}.0.stepgen.{sg}.dirhold [{joint}]DIRHOLD")
print()

print(f"# StepGen Scaling and Limits")
print(f"setp hm2_{board}.0.stepgen.{sg}.position-scale [{joint}]STEP_SCALE")
print(f"setp hm2_{board}.0.stepgen.{sg}.maxvel [{joint}]STEPGEN_MAXVEL")
print(f"setp hm2_{board}.0.stepgen.{sg}.maxaccel [{joint}]STEPGEN_MAXACCEL")
print()

print(f"# StepGen Mode (step/dir, position control)")
print(f"setp hm2_{board}.0.stepgen.{sg}.step_type 0")
print(f"setp hm2_{board}.0.stepgen.{sg}.control-type 0")
print()

print(f"# Connect to Motion Controller")
axis_lower = AXIS_NAME.lower()
print(f"net {axis_lower}-pos-cmd joint.{JOINT_NUM}.motor-pos-cmd => hm2_{board}.0.stepgen.{sg}.position-cmd")
print(f"net {axis_lower}-pos-fb hm2_{board}.0.stepgen.{sg}.position-fb => joint.{JOINT_NUM}.motor-pos-fb")
print(f"net {axis_lower}-enable joint.{JOINT_NUM}.amp-enable-out => hm2_{board}.0.stepgen.{sg}.enable")
print()

print("=" * 80)
print("QUICK REFERENCE")
print("=" * 80)
print()
print(f"Position Scale:      {position_scale:.4f} steps/{UNITS}")
print(f"Resolution:          {resolution:.6f} {UNITS}/step")
print(f"Max Step Rate:       {max_step_rate:,.0f} steps/s ({max_step_rate/1000:.1f} kHz)")
print(f"Axis Max Velocity:   {axis_maxvel:.2f} {UNITS}/s ({axis_maxvel*60:.0f} {UNITS}/min)")
print(f"StepGen Max Vel:     {stepgen_maxvel:.2f} {UNITS}/s ({stepgen_maxvel*60:.0f} {UNITS}/min)")
print(f"Headroom Factor:     {STEPGEN_HEADROOM:.2f}x ({(STEPGEN_HEADROOM-1)*100:.0f}% extra)")
print(f"Hardware Utilization: {step_rate_pct:.1f}% of maximum")
print()

print("=" * 80)
print("NOTES")
print("=" * 80)
print()
print("1. IMPORTANT: For simple machines (trivkins), AXIS and JOINT values")
print("   for MAX_VELOCITY and MAX_ACCELERATION should be IDENTICAL!")
print()
print("2. TRAJ values should be HIGHER (√2 or √3 times) to allow full-speed")
print("   diagonal moves when multiple axes move simultaneously.")
print()
print("3. STEPGEN_MAXVEL/MAXACCEL should be 25-100% HIGHER than JOINT values")
print("   to provide headroom for the PID control loop.")
print()
print("4. Timing parameters (STEPLEN, STEPSPACE, etc.) are in NANOSECONDS")
print("   and are sent to the MESA hardware FPGA, not used by software.")
print()
print("5. MESA hardware stepgen is NOT affected by PC latency - it runs")
print("   independently on the FPGA at ~10MHz clock rate.")
print()
print("6. BASE_PERIOD is IRRELEVANT for MESA boards. It's only used for")
print("   parallel port software stepping. For MESA, the FPGA hardware")
print("   generates steps based solely on STEPLEN+STEPSPACE timing.")
print("   The hardware limit check above IS your step generation limit.")
print()
print("8. MOTOR FREQUENCY LIMITS: Motor datasheet specs are often very")
print("   conservative. With modern drivers and microstepping, motors can")
print("   typically handle 10-50x their datasheet 'max step rate'. Test")
print("   carefully and gradually increase speed to find real limits.")
print()
print("9. The PRIMARY limit is usually MESA hardware timing (STEPLEN+STEPSPACE),")
print("   NOT the motor. Set MOTOR_MAX_STEP_RATE=0 unless you know your motor")
print("   has unusually low frequency limits.")
print()
print("10. To use this for another axis, update AXIS_NAME and JOINT_NUM")
print("   at the top of this script and run again.")
print()

print("=" * 80)

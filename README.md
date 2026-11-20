# Caretta Simulator

Gazebo simulation for the FS-1 Caretta robot by Field Stack Robotics.

Tested on Ubuntu 22.04, ROS 2 Humble, Ignition Gazebo Fortress.

## Setup

Install [ROS 2 Humble](https://docs.ros.org/en/humble/Installation.html) first.

### 1. Install the tools

Install rosdep (installs package dependencies), colcon (builds the workspace) and git (downloads the repos):

```bash
sudo apt install python3-rosdep python3-colcon-common-extensions git
```

Install the keyboard teleop, used to drive the robot:

```bash
sudo apt install ros-humble-teleop-twist-keyboard
```

### 2. Create the workspace

Create the workspace folder. All packages go inside `src/`:

```bash
mkdir -p ~/caretta_ws/src
```

Go into `src/`:

```bash
cd ~/caretta_ws/src
```

### 3. Clone the repos

Download the robot model (needed by the simulation):

```bash
git clone -b humble https://github.com/field-stack-robotics/caretta.git
```

Download this simulation:

```bash
git clone -b humble https://github.com/field-stack-robotics/caretta_simulator.git
```

### 4. Install the dependencies

Go back to the workspace root:

```bash
cd ~/caretta_ws
```

Set up rosdep. This is needed only once per computer; skip it if it says "already exists":

```bash
sudo rosdep init
```

Download the latest list of ROS packages:

```bash
rosdep update
```

Install every package the repos need (Gazebo, ros2_control, ...):

```bash
rosdep install --from-paths src --ignore-src -y
```

### 5. Build

Build all packages in `src/`. This creates the `build/`, `install/` and `log/` folders:

```bash
colcon build
```

Load the built packages into this terminal so `ros2` can find them:

```bash
source install/setup.bash
```

Run `source ~/caretta_ws/install/setup.bash` in every new terminal.

## Run

Start Gazebo with the robot, and RViz:

```bash
ros2 launch caretta_gazebo gazebo.launch.py rviz:=true
```

Drive the robot with the keyboard (in a second terminal):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r cmd_vel:=/diff_drive_controller/cmd_vel_unstamped
```

## Topics

- `/scan`: LiDAR
- `/camera/image_raw`: camera
- `/diff_drive_controller/odom`: odometry

## License

Apache-2.0

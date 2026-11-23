# Caretta Simulator

https://github.com/user-attachments/assets/5369956b-e824-4f32-9cb9-5ca2b4d7fa6d

Gazebo simulation for the FS-1 Caretta robot by Field Stack Robotics.

Tested on Ubuntu 22.04, ROS 2 Humble, Ignition Gazebo Fortress.

## 1. Setup

Install [ROS 2 Humble](https://docs.ros.org/en/humble/Installation.html) first.

### 1.1 Install the tools

Install rosdep (installs package dependencies), colcon (builds the workspace) and git (downloads the repos):

```bash
sudo apt install python3-rosdep python3-colcon-common-extensions git
```

Install the keyboard teleop, used to drive the robot:

```bash
sudo apt install ros-humble-teleop-twist-keyboard
```

### 1.2 Create the workspace

Create the workspace folder. All packages go inside `src/`:

```bash
mkdir -p ~/caretta_ws/src
```

Go into `src/`:

```bash
cd ~/caretta_ws/src
```

### 1.3 Clone the repos

Download the robot, model and control (needed by the simulation):

```bash
git clone -b humble https://github.com/field-stack-robotics/caretta.git
```

Download this simulation:

```bash
git clone -b humble https://github.com/field-stack-robotics/caretta_simulator.git
```

### 1.4 Install the dependencies

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

### 1.5 Build

Build all packages in `src/`. This creates the `build/`, `install/` and `log/` folders:

```bash
colcon build
```

Load the built packages into this terminal so `ros2` can find them:

```bash
source install/setup.bash
```

Run `source ~/caretta_ws/install/setup.bash` in every new terminal.

## 2. Run

### 2.1 Start Simulation

Start Gazebo with the robot, and RViz:

```bash
ros2 launch caretta_gazebo gazebo.launch.py rviz:=true
```

The default world is empty. Pick another one with `world:=<name>`:

- `caretta_house`: corridor and three rooms (SLAM)
- `caretta_office`: 30 x 20 m building (harder SLAM)
- `caretta_outdoor`: open field (GPS)

<table>
  <tr>
    <td align="center"><img src="docs/media/world_house.jpg" width="270" alt="caretta_house world"><br><code>caretta_house</code></td>
    <td align="center"><img src="docs/media/world_office.jpg" width="270" alt="caretta_office world"><br><code>caretta_office</code></td>
    <td align="center"><img src="docs/media/world_outdoor.jpg" width="270" alt="caretta_outdoor world"><br><code>caretta_outdoor</code></td>
  </tr>
</table>

```bash
ros2 launch caretta_gazebo gazebo.launch.py rviz:=true world:=caretta_house
```

Open a new terminal and run the command below:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r cmd_vel:=cmd_vel_teleop
```

### 2.2 Emergency Stop

`true` stops the robot: every velocity command (teleop and Nav2) is blocked until you release it:

```bash
ros2 topic pub --once /e_stop std_msgs/msg/Bool "data: true"
```

`false` releases it, the robot accepts commands again:

```bash
ros2 topic pub --once /e_stop std_msgs/msg/Bool "data: false"
```

## 3. Topics

Sensors:

- `/scan`: LiDAR
- `/camera/image_raw`: camera
- `/imu`: IMU (BNO055, 100 Hz)
- `/diff_drive_controller/odom`: wheel odometry
- `/odometry/filtered`: EKF output, wheel odometry + IMU (also the TF `odom` -> `caretta_base_footprint`)

Velocity commands (`twist_mux` picks one; the higher priority wins):

- `/cmd_vel_teleop`: keyboard, priority 100
- `/cmd_vel`: autonomous navigation (Nav2), priority 10
- `/e_stop`: `std_msgs/Bool`, `true` stops the robot

## 4. License

Apache-2.0

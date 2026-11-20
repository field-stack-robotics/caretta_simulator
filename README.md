# Caretta Simulator

Gazebo (Ignition Fortress) simulation for the FS-1 Caretta robot. ROS 2 Humble.

Needs the [caretta](https://github.com/field-stack-robotics/caretta) repo in the same workspace.

## Run

```bash
ros2 launch caretta_gazebo gazebo.launch.py rviz:=true
```

Drive it:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r cmd_vel:=/diff_drive_controller/cmd_vel_unstamped
```

## License

Apache-2.0

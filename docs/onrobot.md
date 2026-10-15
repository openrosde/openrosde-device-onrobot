# OnRobot Grippers

Documentation of the OnRobot device of OpenRoSDE, which packages the [`onrobot`](https://github.com/UOsaka-Harada-Laboratory/onrobot) driver of the Harada Laboratory of Osaka University for the OnRobot RG grippers, with the description of the OnRobot Quick Changer.

[[_TOC_]]

## 🔗 External Resources

- OnRobot RG2: [https://onrobot.com/products/rg2](https://onrobot.com/products/rg2)
- OnRobot RG6: [https://onrobot.com/products/rg6](https://onrobot.com/products/rg6)
- OnRobot Quick Changer: [https://onrobot.com/products/quick-changer](https://onrobot.com/products/quick-changer)
- Osaka University Harada Laboratory OnRobot ROS: [https://github.com/UOsaka-Harada-Laboratory/onrobot](https://github.com/UOsaka-Harada-Laboratory/onrobot)
- RoboticsGroup UPatras Gazebo Plugins: [https://github.com/roboticsgroup/roboticsgroup_upatras_gazebo_plugins](https://github.com/roboticsgroup/roboticsgroup_upatras_gazebo_plugins)

## 🔩 Hardware Overview

- **Gripper:** an OnRobot RG2 or RG6 electric parallel gripper, which the `gripper` argument of the launch files selects (`rg2` by default).
- **Gripper controller:** the OnRobot Compute Box, connected to the gripper through the OnRobot Quick Changer and to the Ubuntu development machine through Ethernet.
  It communicates over Modbus TCP on port `502`.
- **Quick changer:** the robot side of the OnRobot Quick Changer (QC-R v3), mounted on the tool flange of the robot, on which the gripper locks.

The `onrobot` submodule also holds the packages of the OnRobot VG10 and VGC10 vacuum grippers, which this device builds but does not launch yet.

## ⚙️ Configuration

Activate the device in `.env.custom`, or in the template of a setup, beside the other extensions:

```shell
OPENROSDE_ROBOT_EXTENSIONS="openrosde-device-onrobot"
```

Then set the IP address of the OnRobot Compute Box:

```shell
OPENROSDE_ONROBOT_COMPUTE_BOX_IP=<compute-box-ip>
```

`docker/docker-compose-onrobot.yaml` passes it to the container, and `onrobot_rg_control_default_realworld.launch` reads it, or uses the factory address `192.168.1.1` when it is not set.
The `ip` argument of the launch file still overrides it for one launch.

## 🌐 Network Configuration

The OnRobot Compute Box broadcasts no host name, so it is reached at a fixed IP address.
Its factory address is `192.168.1.1`.

> [!NOTE]
> To give the Compute Box an address on the network of the robot, connect to it directly through Ethernet and open its web interface at `http://192.168.1.1`.
> The default username is `admin` and the default password is `OnRobot`.
> A factory reset brings the address back to `192.168.1.1`.

## 🦾 Real Gripper

To start the driver of the OnRobot RG2 through the Compute Box:

```shell
roslaunch openrosde_onrobot_launch onrobot_rg_control_default_realworld.launch
```

Add `gripper:=rg6` for an OnRobot RG6.
The driver publishes the status of the gripper on `/OnRobotRGInput` and serves the `/onrobot_rg/set_command` service, which takes `o` to open, `c` to close, `i` and `d` to raise and lower the grip force, or a width in 1/10 millimeters:

```shell
rosservice call /onrobot_rg/set_command "command: 'o'"
```

> [!IMPORTANT]
> Always have the emergency stop button of the robot in your hand while using the gripper.
> In the case of any collision or emergency, press it immediately!

## 🎮 Simulated Gripper

A robot description for Gazebo that holds the gripper, such as one that calls the `onrobot_rg2` macro of `onrobot_rg_description` with its Gazebo transmissions, gets its controllers from:

```shell
roslaunch openrosde_onrobot_launch onrobot_rg_control_default_gazebo.launch
```

It spawns the controllers in `/onrobot_<gripper>` and serves the same `/onrobot_rg/set_command` service as the real gripper, so a client drives both alike.
The mimic joints of the fingers need `roboticsgroup_upatras_gazebo_plugins`, which this device builds from its submodule.

## 🤏 Gripper Action

To serve a `control_msgs/GripperCommand` action on `/gripper_controller/gripper_action`, over `/onrobot_rg/set_command` of the real or the simulated gripper:

```shell
roslaunch openrosde_onrobot_launch onrobot_rg_gripper_action.launch
```

A goal with a position of `0.05` or more opens the gripper, and a smaller one closes it.
The node answers on the `result` and `status` topics of the action, as a client that sends one goal at a time expects, rather than running a full `actionlib` server.

## 🦴 Joint States

The real gripper publishes no joint state, so its fingers stay still in RViz without:

```shell
roslaunch openrosde_onrobot_launch onrobot_rg_joint_states.launch
```

It turns the width of `/OnRobotRGInput` into the angles of the six finger joints on `/joint_states`, and publishes zero positions for the joints that no other node publishes while no status arrives.
Pass `prefix:=<prefix>` when the gripper macro got a prefix, and `gripper:=rg6` for an OnRobot RG6.

## 🕹️ Joystick Button

To toggle the gripper between open and closed with a button of any `sensor_msgs/Joy` device, such as Button 1 of a 3Dconnexion SpaceMouse:

```shell
roslaunch openrosde_onrobot_launch onrobot_rg_joy_button.launch joy_topic:=/spacenav/joy
```

`joy_topic` defaults to `/joy`, and `gripper_button_index` to `1`, so the device depends on no input device, and the setup names the topic of its own.

## 🔌 Quick Changer Description

`openrosde_onrobot_description` defines the macro `onrobot_qc_r_v3` of the robot side of the OnRobot Quick Changer (QC-R v3), with the links `qc_robot_mount`, `qc_body`, and `qc_tool_mount`, where the gripper mounts 13.6 mm above the robot side:

```xml
<xacro:include filename="$(find openrosde_onrobot_description)/urdf/onrobot_quick_changer_qc-r_v3.xacro"/>

<xacro:onrobot_qc_r_v3 parent="tool0">
  <origin xyz="0 0 0" rpy="0 0 0"/>
</xacro:onrobot_qc_r_v3>
```

- `prefix` starts every name, `qc_` by default.
- The body is drawn as a cylinder of the size of the quick changer, 71 mm across and 13.6 mm thick, since this repository ships no mesh of it.
- `visual_mesh` and `collision_mesh` take the URIs of meshes that replace the cylinder, such as meshes that a setup holds, and change nothing else.

See the README of [`openrosde_onrobot_description`](../ros/onrobot_catkin_ws/src/openrosde_onrobot_description/README.md) for every parameter.

## 🩹 Submodule Patch

`patches/ros/onrobot_catkin_ws/src/onrobot/0001-fix-duplicate-world.patch` comments out the `world` link of `onrobot_rg2.xacro` and its joint, which would duplicate the `world` link of the robot that carries the gripper.
`bash ./scripts/update-git-submodules.bash` of OpenRoSDE applies it to the `onrobot` submodule of this device.

## 📋 Launch Files Reference

The launch files of the device are in the package `openrosde_onrobot_launch`:

| Launch File | Description |
| --- | --- |
| `onrobot_rg_control_default_realworld.launch` | OnRobot RG2 or RG6 through the Compute Box over Modbus TCP |
| `onrobot_rg_control_default_gazebo.launch` | OnRobot RG2 or RG6 in Gazebo, behind the same service |
| `onrobot_rg_gripper_action.launch` | `control_msgs/GripperCommand` action over the service of the gripper |
| `onrobot_rg_joint_states.launch` | Joint states of the fingers from the status of the gripper |
| `onrobot_rg_joy_button.launch` | Button of a `sensor_msgs/Joy` device that toggles the gripper |

A device ships no `tmux` panes, so the setup that activates it starts these launch files from its own panes.

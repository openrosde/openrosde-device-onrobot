# openrosde_onrobot_launch

The `openrosde_onrobot_launch` package provides the launch files and nodes of the OnRobot RG grippers (RG2 and RG6) in OpenRoSDE, around the `onrobot_rg_control` driver of the `onrobot` submodule.

- Maintainer: Lotfi El Hafi ([lotfi@coarobo.com](mailto:lotfi@coarobo.com)).
- Author: Lotfi El Hafi ([lotfi@coarobo.com](mailto:lotfi@coarobo.com)).
- License: [Apache License 2.0](../../../../LICENSE).

## Launch Files

| Launch File | Description |
| --- | --- |
| `onrobot_rg_control_default_realworld.launch` | Driver of the real gripper over Modbus TCP, with the `/onrobot_rg/set_command` service |
| `onrobot_rg_control_default_gazebo.launch` | Controllers of the simulated gripper in Gazebo, behind the same `/onrobot_rg/set_command` service |
| `onrobot_rg_gripper_action.launch` | `control_msgs/GripperCommand` action on `/gripper_controller/gripper_action`, over `/onrobot_rg/set_command` |
| `onrobot_rg_joint_states.launch` | Joint states of the fingers on `/joint_states`, from the status of the gripper |

Every launch file takes `gripper:=rg2` or `gripper:=rg6`, apart from the action, which only sends open and close commands.

## Real Gripper

```shell
roslaunch openrosde_onrobot_launch onrobot_rg_control_default_realworld.launch
```

This includes `bringup_server.launch` of `onrobot_rg_control`, which connects to the OnRobot Compute Box at `ip`, publishes the status of the gripper on `/OnRobotRGInput`, and serves the `/onrobot_rg/set_command` service.
`ip` defaults to `OPENROSDE_ONROBOT_COMPUTE_BOX_IP`, or to the factory address `192.168.1.1` of the Compute Box when that variable is not set.
The service takes `o` to open, `c` to close, `i` and `d` to raise and lower the grip force by a step, or a width in 1/10 millimeters.

## Simulated Gripper

```shell
roslaunch openrosde_onrobot_launch onrobot_rg_control_default_gazebo.launch
```

This spawns the `joint_state_controller` and `joint_position_controller` of the gripper in the namespace `/onrobot_<gripper>`, from `config/<gripper>_control_params.yaml` of `onrobot_rg_control`, for a robot description in Gazebo that holds the gripper.
It then starts `onrobot_rg_command_bridge.py` in its service bridge mode, which serves `/onrobot_rg/set_command` and turns each command into a position of `/onrobot_<gripper>/joint_position_controller/command`, so that a client drives the simulated gripper as it drives the real one.
There `i` and `d` widen and narrow the gripper by a step, since the simulation has no grip force.

## Gripper Action

```shell
roslaunch openrosde_onrobot_launch onrobot_rg_gripper_action.launch
```

`onrobot_rg_gripper_action.py` subscribes to `/gripper_controller/gripper_action/goal` and answers on its `result` and `status` topics, as a `control_msgs/GripperCommand` action client expects.
A commanded position at or above `open_position_threshold` (`0.05`) opens the gripper through `/onrobot_rg/set_command`, and a smaller one closes it.
It is not a full `actionlib` server, so it serves a client that sends one goal at a time.

## Joint States

```shell
roslaunch openrosde_onrobot_launch onrobot_rg_joint_states.launch
```

`onrobot_rg_joint_states.py` turns the width of `/OnRobotRGInput` into the angles of the six finger joints and publishes them on `/joint_states`, so that `robot_state_publisher` moves the fingers in RViz.
Without a status, it publishes zero positions for the finger joints that no other node publishes, and it ignores its own messages by its node name.
`prefix` matches the prefix given to the gripper macro of `onrobot_rg_description`, and `gripper` sets the width range and the `finger_joint` limits of the RG2 or the RG6.

## Joystick Button

`onrobot_rg_command_bridge.py` also has a joy mode, on by default, in which a button of any `sensor_msgs/Joy` device toggles the gripper between open and closed through `/onrobot_rg/set_command`:

```xml
<node pkg="openrosde_onrobot_launch" type="onrobot_rg_command_bridge.py" name="onrobot_rg_joy_button" output="screen">
  <param name="joy_topic" value="/spacenav/joy" />
  <param name="gripper_button_index" value="1" />
</node>
```

Parameters of the joy mode:

- `joy_topic`: Topic of the `sensor_msgs/Joy` device. Defaults to `/joy`.
- `gripper_button_index`: Index of the button that toggles the gripper. Defaults to `1`.
- `gripper_service_name`: Command service of the gripper. Defaults to `/onrobot_rg/set_command`.
- `gripper_open_command`: Command that opens the gripper. Defaults to `o`.
- `gripper_close_command`: Command that closes the gripper. Defaults to `c`.
- `gripper_initial_state`: Assumed state of the gripper at start, `open` or `closed`. Defaults to `open`.

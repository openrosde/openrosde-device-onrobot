#!/usr/bin/env python3

"""Bridge commands to an OnRobot RG gripper, in two modes, each switched on by its own parameter.

In the joy mode (~enable_joy_control), a button of any sensor_msgs/Joy device, such as a
3Dconnexion SpaceMouse on /spacenav/joy, toggles the gripper between open and closed through
the SetCommand service of onrobot_rg_control (/onrobot_rg/set_command by default).

In the service bridge mode (~enable_service_bridge), the node serves that SetCommand service
itself and turns each command into a position of the joint position controller of a simulated
gripper in Gazebo, so that a client drives the simulated gripper as it drives the real one.
"""

import rospy
from onrobot_rg_control.srv import SetCommand, SetCommandResponse
from sensor_msgs.msg import Joy
from std_msgs.msg import Float64


class OnrobotRgCommandBridge(object):
    def __init__(self):
        self.enable_joy_control = rospy.get_param("~enable_joy_control", True)
        self.enable_service_bridge = rospy.get_param("~enable_service_bridge", False)

        self.joy_topic = rospy.get_param("~joy_topic", "/joy")
        self.gripper_button_index = rospy.get_param("~gripper_button_index", 1)
        self.gripper_service_name = rospy.get_param("~gripper_service_name", "/onrobot_rg/set_command")
        self.gripper_open_command = rospy.get_param("~gripper_open_command", "o")
        self.gripper_close_command = rospy.get_param("~gripper_close_command", "c")
        self.gripper_initial_state = rospy.get_param("~gripper_initial_state", "open")

        self.command_topic = rospy.get_param(
            "~command_topic", "/onrobot_rg2/joint_position_controller/command"
        )
        self.gripper = rospy.get_param("~gripper", "rg2")
        self.closed_joint_position = rospy.get_param("~closed_joint_position", 0.0)
        self.open_joint_position = rospy.get_param("~open_joint_position", 0.5)
        self.step_joint_position = rospy.get_param("~step_joint_position", 0.05)
        self.initial_joint_position = rospy.get_param(
            "~initial_joint_position", self.open_joint_position
        )
        self.publish_initial_position = rospy.get_param("~publish_initial_position", True)

        self.gripper_is_open = self.gripper_initial_state.lower() != "closed"
        self.previous_gripper_button_state = False
        self.gripper_service = None
        self.gripper_command_publisher = None
        self.gripper_command_service = None
        self.max_width = 1100.0 if self.gripper == "rg2" else 1600.0
        self.current_joint_position = self._clamp_joint_position(
            self.initial_joint_position
        )

        if self.enable_joy_control:
            try:
                self.gripper_service = rospy.ServiceProxy(
                    self.gripper_service_name, SetCommand
                )
            except rospy.ServiceException:
                rospy.logwarn(
                    "Failed to create gripper service proxy for %s",
                    self.gripper_service_name,
                )

            self.joy_subscriber = rospy.Subscriber(
                self.joy_topic, Joy, self._handle_joy, queue_size=1
            )

        if self.enable_service_bridge:
            self.gripper_command_publisher = rospy.Publisher(
                self.command_topic, Float64, queue_size=1
            )
            self.gripper_command_service = rospy.Service(
                self.gripper_service_name,
                SetCommand,
                self._handle_set_command,
            )

            if self.publish_initial_position:
                self._publish_joint_position(self.current_joint_position)

    def _handle_joy(self, joy_message):
        gripper_button_pressed = False
        if 0 <= self.gripper_button_index < len(joy_message.buttons):
            gripper_button_pressed = bool(joy_message.buttons[self.gripper_button_index])

        if gripper_button_pressed and not self.previous_gripper_button_state:
            self._toggle_gripper()

        self.previous_gripper_button_state = gripper_button_pressed

    def _toggle_gripper(self):
        if self.gripper_service is None:
            rospy.logwarn_throttle(5.0, "Gripper service %s is not available", self.gripper_service_name)
            return

        command = self.gripper_close_command if self.gripper_is_open else self.gripper_open_command

        try:
            self.gripper_service(command)
            self.gripper_is_open = not self.gripper_is_open
        except rospy.ServiceException as error:
            rospy.logwarn("Failed to call gripper service %s: %s", self.gripper_service_name, error)

    def _clamp_joint_position(self, value):
        minimum = min(self.closed_joint_position, self.open_joint_position)
        maximum = max(self.closed_joint_position, self.open_joint_position)
        return max(minimum, min(maximum, value))

    def _publish_joint_position(self, value):
        if self.gripper_command_publisher is not None:
            self.gripper_command_publisher.publish(Float64(data=value))

    def _joint_position_from_width(self, width):
        ratio = max(0.0, min(1.0, width / self.max_width))
        return self.closed_joint_position + ratio * (
            self.open_joint_position - self.closed_joint_position
        )

    def _handle_set_command(self, request):
        command = request.command.strip().lower()

        if command == "c":
            target = self.closed_joint_position
        elif command == "o":
            target = self.open_joint_position
        elif command == "i":
            target = self.current_joint_position + self.step_joint_position
        elif command == "d":
            target = self.current_joint_position - self.step_joint_position
        else:
            try:
                target = self._joint_position_from_width(float(command))
            except ValueError:
                return SetCommandResponse(
                    success=False,
                    message=(
                        "Unsupported command '{}'. Use c, o, i, d, or a numeric width."
                    ).format(request.command),
                )

        target = self._clamp_joint_position(target)
        self.current_joint_position = target
        self._publish_joint_position(target)

        return SetCommandResponse(
            success=True,
            message="Published {:.4f} to {}".format(target, self.command_topic),
        )


def main():
    rospy.init_node("onrobot_rg_command_bridge")
    OnrobotRgCommandBridge()
    rospy.spin()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

"""Expose a control_msgs/GripperCommand action interface for the OnRobot RG-2 gripper.

This node lets a GripperCommand action client, for example the Coarobo Sightline OpenXR
application, open and close the OnRobot RG-2. The commanded gripper position is translated
into an open or close command and forwarded to the OnRobot RG service.

The node does not implement a full actionlib server. It subscribes to the action goal topic
and publishes on the action result and status topics, which is what the Coarobo Sightline
ActionClient wrapper consumes.
"""

import rospy
from actionlib_msgs.msg import GoalStatus, GoalStatusArray
from control_msgs.msg import GripperCommandActionGoal, GripperCommandActionResult
from onrobot_rg_control.srv import SetCommand


class Ur5eOnrobotRgControlGripperAction(object):
    def __init__(self):
        self.action_name = rospy.get_param("~action_name", "/gripper_controller/gripper_action")
        self.gripper_service_name = rospy.get_param("~gripper_service_name", "/onrobot_rg/set_command")
        self.gripper_open_command = rospy.get_param("~gripper_open_command", "o")
        self.gripper_close_command = rospy.get_param("~gripper_close_command", "c")
        # A commanded position at or above this threshold opens the gripper, below it closes.
        self.open_position_threshold = rospy.get_param("~open_position_threshold", 0.05)

        self.gripper_service = rospy.ServiceProxy(self.gripper_service_name, SetCommand)

        self.result_publisher = rospy.Publisher(
            self.action_name + "/result", GripperCommandActionResult, queue_size=1
        )
        self.status_publisher = rospy.Publisher(
            self.action_name + "/status", GoalStatusArray, queue_size=1
        )
        self.goal_subscriber = rospy.Subscriber(
            self.action_name + "/goal", GripperCommandActionGoal, self._handle_goal, queue_size=1
        )

        rospy.loginfo(
            "ur5e_onrobot_rg_control_gripper_action ready. Action: %s -> service: %s.",
            self.action_name, self.gripper_service_name,
        )

    def _handle_goal(self, goal_message):
        position = goal_message.goal.command.position
        opening = position >= self.open_position_threshold
        command = self.gripper_open_command if opening else self.gripper_close_command

        success = False
        try:
            response = self.gripper_service(command)
            success = bool(response.success)
        except rospy.ServiceException as error:
            rospy.logwarn("Failed to call gripper service %s: %s", self.gripper_service_name, error)

        # Echo the commanded position back in the result so the action client can classify the gripper as open or closed.
        # reached_goal drives that classification on the client side.
        result = GripperCommandActionResult()
        result.header.stamp = rospy.Time.now()
        result.status.goal_id = goal_message.goal_id
        result.status.status = GoalStatus.SUCCEEDED if success else GoalStatus.ABORTED
        result.result.position = position
        result.result.effort = goal_message.goal.command.max_effort
        result.result.stalled = False
        result.result.reached_goal = success
        self.result_publisher.publish(result)

        status_array = GoalStatusArray()
        status_array.header.stamp = rospy.Time.now()
        status_array.status_list = [result.status]
        self.status_publisher.publish(status_array)


def main():
    rospy.init_node("ur5e_onrobot_rg_control_gripper_action")
    Ur5eOnrobotRgControlGripperAction()
    rospy.spin()


if __name__ == "__main__":
    main()

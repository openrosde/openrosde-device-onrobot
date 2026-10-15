#!/usr/bin/env python3

# This script publishes fallback joint states for the OnRobot RG2 gripper.
# If real gripper joint states are available, it does not override them.
# If they are missing, it publishes zero positions so robot_state_publisher
# can still compute TF for all gripper links.
#
# Usage: run via roslaunch (openrosde_ur5e_launch/launch/ur5e_bringup_default_realworld.launch)

################################################################################

import rospy
from sensor_msgs.msg import JointState

try:
    from onrobot_rg_control.msg import OnRobotRGInput
except Exception:  # pragma: no cover - runtime-only optional dependency
    OnRobotRGInput = None

################################################################################

# Joint names that are revolute (non-mimic and mimic) in the RG2 URDF.
# robot_state_publisher computes TF for all of these from /joint_states.
GRIPPER_JOINTS = [
    'finger_joint',
    'right_outer_knuckle_joint',
    'left_inner_knuckle_joint',
    'right_inner_knuckle_joint',
    'left_inner_finger_joint',
    'right_inner_finger_joint',
]

GRIPPER_SET = set(GRIPPER_JOINTS)

################################################################################

def main():
    rospy.init_node('gripper_joint_state_publisher')

    timeout_sec = rospy.get_param('~timeout_sec', 0.5)
    status_timeout_sec = rospy.get_param('~status_timeout_sec', 0.5)
    publish_rate_hz = rospy.get_param('~publish_rate_hz', 30.0)

    # RG2 width command/status range is in 1/10 millimeters.
    min_width_tenth_mm = rospy.get_param('~min_width_tenth_mm', 0.0)
    max_width_tenth_mm = rospy.get_param('~max_width_tenth_mm', 1100.0)

    # These limits match the RG2 `finger_joint` URDF limits.
    finger_joint_lower = rospy.get_param('~finger_joint_lower', -0.558505)
    finger_joint_upper = rospy.get_param('~finger_joint_upper', 0.785398)

    # For RG2, wider opening corresponds to smaller angle in this URDF.
    invert_width_mapping = rospy.get_param('~invert_width_mapping', True)

    pub = rospy.Publisher('/joint_states', JointState, queue_size=10)
    rate = rospy.Rate(publish_rate_hz)

    # Track when each gripper joint was last seen from a non-self publisher.
    last_seen_real = {joint_name: rospy.Time(0) for joint_name in GRIPPER_JOINTS}

    # Track latest OnRobot status timestamp and width.
    last_status_time = rospy.Time(0)
    last_width_tenth_mm = None

    def on_joint_states(msg):
        caller_id = msg._connection_header.get('callerid', '') if hasattr(msg, '_connection_header') else ''
        if caller_id == '/gripper_joint_state_publisher':
            return

        now = rospy.Time.now()
        for joint_name in msg.name:
            if joint_name in GRIPPER_SET:
                last_seen_real[joint_name] = now

    def on_onrobot_status(msg):
        nonlocal last_status_time
        nonlocal last_width_tenth_mm

        last_status_time = rospy.Time.now()
        last_width_tenth_mm = float(msg.gWDF)

    def clamp(value, min_value, max_value):
        return max(min_value, min(max_value, value))

    def width_to_finger_angle(width_tenth_mm):
        # Normalize width to [0, 1] and map linearly to joint range.
        width_clamped = clamp(width_tenth_mm, min_width_tenth_mm, max_width_tenth_mm)
        span = max_width_tenth_mm - min_width_tenth_mm
        ratio = 0.0 if span <= 1e-9 else (width_clamped - min_width_tenth_mm) / span

        if invert_width_mapping:
            ratio = 1.0 - ratio

        return finger_joint_lower + ratio * (finger_joint_upper - finger_joint_lower)

    rospy.Subscriber('/joint_states', JointState, on_joint_states, queue_size=20)

    if OnRobotRGInput is not None:
        rospy.Subscriber('/OnRobotRGInput', OnRobotRGInput, on_onrobot_status, queue_size=10)
        rospy.loginfo('gripper_joint_state_publisher: subscribed to /OnRobotRGInput for live gripper motion')
    else:
        rospy.logwarn('gripper_joint_state_publisher: OnRobotRGInput message not available; using fallback mode only')

    rospy.loginfo(
        'gripper_joint_state_publisher: publishing fallback zeros for joints without real state for %.2fs: %s',
        timeout_sec,
        GRIPPER_JOINTS,
    )

    while not rospy.is_shutdown():
        now = rospy.Time.now()

        # Prefer live OnRobot status when available.
        if last_width_tenth_mm is not None and (now - last_status_time).to_sec() <= status_timeout_sec:
            finger_angle = width_to_finger_angle(last_width_tenth_mm)
            msg = JointState()
            msg.header.stamp = now
            msg.name = GRIPPER_JOINTS
            msg.position = [
                finger_angle,          # finger_joint
                -finger_angle,         # right_outer_knuckle_joint (mimic multiplier -1)
                -finger_angle,         # left_inner_knuckle_joint (mimic multiplier -1)
                -finger_angle,         # right_inner_knuckle_joint (mimic multiplier -1)
                finger_angle,          # left_inner_finger_joint (mimic multiplier +1)
                finger_angle,          # right_inner_finger_joint (mimic multiplier +1)
            ]
            msg.velocity = []
            msg.effort = []
            pub.publish(msg)
            rate.sleep()
            continue

        missing_joints = []

        for joint_name in GRIPPER_JOINTS:
            if (now - last_seen_real[joint_name]).to_sec() > timeout_sec:
                missing_joints.append(joint_name)

        if not missing_joints:
            rate.sleep()
            continue

        msg = JointState()
        msg.header.stamp = rospy.Time.now()
        msg.name = missing_joints
        msg.position = [0.0] * len(missing_joints)
        msg.velocity = []
        msg.effort = []

        pub.publish(msg)
        rate.sleep()

################################################################################

if __name__ == '__main__':
    main()

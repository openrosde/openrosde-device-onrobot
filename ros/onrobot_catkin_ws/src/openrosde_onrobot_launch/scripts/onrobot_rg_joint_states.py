#!/usr/bin/env python3

# This script publishes the joint states of an OnRobot RG2 or RG6 gripper on '/joint_states'.
# While the status of the gripper arrives on '/OnRobotRGInput', it turns the measured width into the angles of the finger joints.
# Otherwise it publishes zero positions for the joints that no other node publishes,
# so that 'robot_state_publisher' can still compute the TF of every gripper link.
# It never overrides the joint states of another publisher, and ignores its own messages by its node name.
#
# Parameters:
#   ~prefix: Prefix of the joint names, as given to the gripper macro of 'onrobot_rg_description' (default: '').
#   ~gripper: 'rg2' or 'rg6', which sets the defaults of the width range and of the 'finger_joint' limits (default: 'rg2').
#
# Usage: roslaunch openrosde_onrobot_launch onrobot_rg_joint_states.launch

################################################################################

import rospy
from sensor_msgs.msg import JointState

try:
    from onrobot_rg_control.msg import OnRobotRGInput
except Exception:  # pragma: no cover - runtime-only optional dependency
    OnRobotRGInput = None

################################################################################

# Joint names that are revolute (non-mimic and mimic) in the RG2 and RG6 URDFs, without their prefix.
# robot_state_publisher computes TF for all of these from /joint_states.
GRIPPER_JOINT_NAMES = [
    'finger_joint',
    'right_outer_knuckle_joint',
    'left_inner_knuckle_joint',
    'right_inner_knuckle_joint',
    'left_inner_finger_joint',
    'right_inner_finger_joint',
]

# Defaults of each gripper: the width range of its status in 1/10 millimeters,
# and the limits of its `finger_joint` in the URDF of 'onrobot_rg_description'.
GRIPPER_DEFAULTS = {
    'rg2': {
        'max_width_tenth_mm': 1100.0,
        'finger_joint_lower': -0.558505,
        'finger_joint_upper': 0.785398,
    },
    'rg6': {
        'max_width_tenth_mm': 1600.0,
        'finger_joint_lower': -0.628319,
        'finger_joint_upper': 0.628319,
    },
}

################################################################################

def main():
    rospy.init_node('onrobot_rg_joint_states')
    node_name = rospy.get_name()

    prefix = rospy.get_param('~prefix', '')
    gripper = rospy.get_param('~gripper', 'rg2')
    if gripper not in GRIPPER_DEFAULTS:
        rospy.logwarn('%s: unknown gripper %s, using the defaults of the rg2', node_name, gripper)
    defaults = GRIPPER_DEFAULTS.get(gripper, GRIPPER_DEFAULTS['rg2'])

    gripper_joints = [prefix + joint_name for joint_name in GRIPPER_JOINT_NAMES]
    gripper_set = set(gripper_joints)

    timeout_sec = rospy.get_param('~timeout_sec', 0.5)
    status_timeout_sec = rospy.get_param('~status_timeout_sec', 0.5)
    publish_rate_hz = rospy.get_param('~publish_rate_hz', 30.0)
    status_topic = rospy.get_param('~status_topic', '/OnRobotRGInput')

    # The width command/status range is in 1/10 millimeters.
    min_width_tenth_mm = rospy.get_param('~min_width_tenth_mm', 0.0)
    max_width_tenth_mm = rospy.get_param('~max_width_tenth_mm', defaults['max_width_tenth_mm'])

    # These limits match the `finger_joint` URDF limits of the gripper.
    finger_joint_lower = rospy.get_param('~finger_joint_lower', defaults['finger_joint_lower'])
    finger_joint_upper = rospy.get_param('~finger_joint_upper', defaults['finger_joint_upper'])

    # For the RG2, wider opening corresponds to smaller angle in this URDF.
    invert_width_mapping = rospy.get_param('~invert_width_mapping', True)

    pub = rospy.Publisher('/joint_states', JointState, queue_size=10)
    rate = rospy.Rate(publish_rate_hz)

    # Track when each gripper joint was last seen from a non-self publisher.
    last_seen_real = {joint_name: rospy.Time(0) for joint_name in gripper_joints}

    # Track latest OnRobot status timestamp and width.
    last_status_time = rospy.Time(0)
    last_width_tenth_mm = None

    def on_joint_states(msg):
        caller_id = msg._connection_header.get('callerid', '') if hasattr(msg, '_connection_header') else ''
        if caller_id == node_name:
            return

        now = rospy.Time.now()
        for joint_name in msg.name:
            if joint_name in gripper_set:
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
        rospy.Subscriber(status_topic, OnRobotRGInput, on_onrobot_status, queue_size=10)
        rospy.loginfo('%s: subscribed to %s for live gripper motion', node_name, status_topic)
    else:
        rospy.logwarn('%s: OnRobotRGInput message not available; using fallback mode only', node_name)

    rospy.loginfo(
        '%s: publishing fallback zeros for joints without real state for %.2fs: %s',
        node_name,
        timeout_sec,
        gripper_joints,
    )

    while not rospy.is_shutdown():
        now = rospy.Time.now()

        # Prefer live OnRobot status when available.
        if last_width_tenth_mm is not None and (now - last_status_time).to_sec() <= status_timeout_sec:
            finger_angle = width_to_finger_angle(last_width_tenth_mm)
            msg = JointState()
            msg.header.stamp = now
            msg.name = gripper_joints
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

        for joint_name in gripper_joints:
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

#!/bin/bash

# This script checks the OnRobot device inside the container of a setup that activates it, as part of the CI of OpenRoSDE.
# 'gitlab-ci/run-extension-checks.bash' of OpenRoSDE runs it once the Catkin workspaces of the setup are built and sourced, in a container without any network.
# It resolves every launch file of 'openrosde_onrobot_launch' with 'roslaunch --files' and '--dump-params', which start no node, compiles its Python nodes, and renders the OnRobot Quick Changer with 'xacro', then checks it with 'check_urdf' and its links, joints, and origins.
#
# Usage: bash ./ci/check-in-container.bash <robot-setup>
#
# <robot-setup>: The setup whose container runs the check, such as 'ur5e'.

################################################################################

# Remember the checks that fail, so that every check runs before the script fails.
OPENROSDE_ONROBOT_FAILED_CHECKS=""

# Record a failed check by its name.
function openrosde-onrobot-fail-check () {
  echo "Error: $1"
  OPENROSDE_ONROBOT_FAILED_CHECKS="${OPENROSDE_ONROBOT_FAILED_CHECKS}"$'\n'"  - $1"
}

# Find the packages of the device in the sourced workspaces.
OPENROSDE_ONROBOT_LAUNCH_DIR="$(rospack find openrosde_onrobot_launch)"
OPENROSDE_ONROBOT_DESCRIPTION_DIR="$(rospack find openrosde_onrobot_description)"
if [ -z "${OPENROSDE_ONROBOT_LAUNCH_DIR}" ] || [ -z "${OPENROSDE_ONROBOT_DESCRIPTION_DIR}" ]; then
  echo "Error: The packages 'openrosde_onrobot_launch' and 'openrosde_onrobot_description' are not in the sourced workspaces of the setup '$1'."
  exit 1
fi
echo "Checking the OnRobot device in the setup '$1'."

################################################################################

# Resolve every launch file and dump its parameters, which starts no node and needs no ROS master.
for OPENROSDE_ONROBOT_LAUNCH_FILE in "${OPENROSDE_ONROBOT_LAUNCH_DIR}"/launch/*.launch; do
  if roslaunch --files "${OPENROSDE_ONROBOT_LAUNCH_FILE}" > /dev/null && roslaunch --dump-params "${OPENROSDE_ONROBOT_LAUNCH_FILE}" > /dev/null; then
    echo "Resolved '$(basename "${OPENROSDE_ONROBOT_LAUNCH_FILE}")'."
  else
    openrosde-onrobot-fail-check "'$(basename "${OPENROSDE_ONROBOT_LAUNCH_FILE}")' does not resolve its files or its parameters."
  fi
done

# Compile every Python node, into a temporary folder rather than next to the sources.
OPENROSDE_ONROBOT_PYCACHE_DIR="$(mktemp -d)"
for OPENROSDE_ONROBOT_SCRIPT_FILE in "${OPENROSDE_ONROBOT_LAUNCH_DIR}"/scripts/*.py; do
  if ! PYTHONPYCACHEPREFIX="${OPENROSDE_ONROBOT_PYCACHE_DIR}" python3 -m py_compile "${OPENROSDE_ONROBOT_SCRIPT_FILE}"; then
    openrosde-onrobot-fail-check "'$(basename "${OPENROSDE_ONROBOT_SCRIPT_FILE}")' does not compile."
  fi
done
rm -rf "${OPENROSDE_ONROBOT_PYCACHE_DIR}"

################################################################################

# Render the quick changer alone with the prefix 'qc_', drawn with primitive shapes and with meshes, and check each description.
OPENROSDE_ONROBOT_URDF_DIR="$(mktemp -d)"
OPENROSDE_ONROBOT_QC_XACRO_FILE="${OPENROSDE_ONROBOT_DESCRIPTION_DIR}/urdf/onrobot_quick_changer_qc-r_v3_standalone.xacro"
if xacro "${OPENROSDE_ONROBOT_QC_XACRO_FILE}" prefix:=qc_ > "${OPENROSDE_ONROBOT_URDF_DIR}/primitive.urdf" \
  && xacro "${OPENROSDE_ONROBOT_QC_XACRO_FILE}" prefix:=qc_ visual_mesh:=package://openrosde_onrobot_description/visual.stl collision_mesh:=package://openrosde_onrobot_description/collision.stl > "${OPENROSDE_ONROBOT_URDF_DIR}/mesh.urdf"; then
  for OPENROSDE_ONROBOT_URDF_NAME in primitive mesh; do
    if ! check_urdf "${OPENROSDE_ONROBOT_URDF_DIR}/${OPENROSDE_ONROBOT_URDF_NAME}.urdf" > /dev/null; then
      openrosde-onrobot-fail-check "The quick changer drawn with ${OPENROSDE_ONROBOT_URDF_NAME} geometry fails 'check_urdf'."
    fi
  done
  # Check the links, the joints with their parents, children, and origins, and the geometry of the body, against the description of the SDE.
  if ! python3 - "${OPENROSDE_ONROBOT_URDF_DIR}" <<'PYTHON'
import sys
import xml.etree.ElementTree as ET

expected_links = ['tool0', 'qc_robot_mount', 'qc_body', 'qc_tool_mount']
expected_joints = {
    'qc_robot_mount_joint': ('tool0', 'qc_robot_mount', '0 0 0'),
    'qc_robot_joint': ('qc_robot_mount', 'qc_body', '0 0 0'),
    'qc_tool_joint': ('qc_body', 'qc_tool_mount', '0 0 0.0136'),
}
expected_geometry = {
    'primitive': ['cylinder length=0.0136 radius=0.0355', 'cylinder length=0.0136 radius=0.0355'],
    'mesh': ['mesh filename=package://openrosde_onrobot_description/visual.stl', 'mesh filename=package://openrosde_onrobot_description/collision.stl'],
}
errors = []
for name, geometry in expected_geometry.items():
    robot = ET.parse('%s/%s.urdf' % (sys.argv[1], name)).getroot()
    links = [link.get('name') for link in robot.findall('link')]
    if sorted(links) != sorted(expected_links):
        errors.append('%s: links %s instead of %s' % (name, links, expected_links))
    joints = {}
    for joint in robot.findall('joint'):
        joints[joint.get('name')] = (joint.find('parent').get('link'), joint.find('child').get('link'), joint.find('origin').get('xyz'))
    if joints != expected_joints:
        errors.append('%s: joints %s instead of %s' % (name, joints, expected_joints))
    body = robot.find("link[@name='qc_body']")
    shapes = []
    for part in ('visual', 'collision'):
        shape = body.find(part + '/geometry')[0]
        shapes.append(' '.join([shape.tag] + ['%s=%s' % item for item in sorted(shape.attrib.items())]))
    if shapes != geometry:
        errors.append('%s: geometry %s instead of %s' % (name, shapes, geometry))
for error in errors:
    print('Error: The quick changer, ' + error)
sys.exit(1 if errors else 0)
PYTHON
  then
    openrosde-onrobot-fail-check "The quick changer does not render the links, joints, origins, and geometry of the description of the SDE."
  else
    echo "Rendered the quick changer with 'qc_robot_mount', 'qc_body', and 'qc_tool_mount' and their origins, with primitive shapes and with meshes."
  fi
else
  openrosde-onrobot-fail-check "'onrobot_quick_changer_qc-r_v3_standalone.xacro' does not render with 'xacro'."
fi
rm -rf "${OPENROSDE_ONROBOT_URDF_DIR}"

################################################################################

# Report the result, and fail if any check failed.
if [ -n "${OPENROSDE_ONROBOT_FAILED_CHECKS}" ]; then
  echo "These checks of the OnRobot device failed:${OPENROSDE_ONROBOT_FAILED_CHECKS}"
  exit 1
fi
echo "Every check of the OnRobot device passed."

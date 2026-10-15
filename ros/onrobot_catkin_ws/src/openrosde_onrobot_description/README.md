# openrosde_onrobot_description

The `openrosde_onrobot_description` package describes the OnRobot equipment that mounts an OnRobot gripper on a robot, for OpenRoSDE.
The grippers themselves are described by `onrobot_rg_description` and `onrobot_vg_description` of the `onrobot` submodule.

- Maintainer: Lotfi El Hafi ([lotfi@coarobo.com](mailto:lotfi@coarobo.com)).
- Author: Lotfi El Hafi ([lotfi@coarobo.com](mailto:lotfi@coarobo.com)).
- License: [Apache License 2.0](../../../../LICENSE).

## OnRobot Quick Changer

`urdf/onrobot_quick_changer_qc-r_v3.xacro` defines the macro `onrobot_qc_r_v3` of the robot side of the OnRobot Quick Changer (QC-R v3), with three links and three fixed joints:

| Element | Name with the default prefix | Origin |
| --- | --- | --- |
| Link | `qc_robot_mount` | The `origin` block of the macro, from `parent` |
| Link | `qc_body` | `0 0 0` from `qc_robot_mount` |
| Link | `qc_tool_mount` | `0 0 0.0136` from `qc_body`, where a gripper mounts |
| Joint | `qc_robot_mount_joint` | From `parent` to `qc_robot_mount` |
| Joint | `qc_robot_joint` | From `qc_robot_mount` to `qc_body` |
| Joint | `qc_tool_joint` | From `qc_body` to `qc_tool_mount` |

Its parameters:

- `parent`: Link the quick changer mounts on, such as `tool0` or `flange`.
- `origin` (block): Pose of `qc_robot_mount` in `parent`.
- `prefix`: Start of the name of every link, joint, and material. Defaults to `qc_`, so give each quick changer of one robot its own prefix, such as `left_qc_`.
- `visual_mesh`: URI of a mesh that replaces the cylinder of the visual geometry, such as `package://<package>/meshes/onrobot_quick_changer_qc-r_v3.stl`. Defaults to empty, for the cylinder.
- `collision_mesh`: URI of a mesh that replaces the cylinder of the collision geometry. Defaults to empty, for the cylinder.

The body is drawn as a cylinder of the size of the quick changer, 71 mm across (radius `0.0355`) and 13.6 mm thick (length `0.0136`), centered on `qc_body`, with the mass and inertia of that cylinder.
The package ships no mesh of the quick changer, so a setup that holds one passes it through `visual_mesh` and `collision_mesh`, and the links, joints, and origins stay the same.

```xml
<xacro:include filename="$(find openrosde_onrobot_description)/urdf/onrobot_quick_changer_qc-r_v3.xacro"/>

<xacro:onrobot_qc_r_v3 parent="tool0">
  <origin xyz="0 0 0" rpy="0 0 0"/>
</xacro:onrobot_qc_r_v3>
```

`urdf/onrobot_quick_changer_qc-r_v3_standalone.xacro` mounts the quick changer alone on a `parent` link, to view it or to check it:

```shell
rosrun xacro xacro $(rospack find openrosde_onrobot_description)/urdf/onrobot_quick_changer_qc-r_v3_standalone.xacro prefix:=qc_ > /tmp/qc.urdf
check_urdf /tmp/qc.urdf
```

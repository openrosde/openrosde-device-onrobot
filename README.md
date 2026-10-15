# OpenRoSDE Device: OnRobot

`openrosde-device-onrobot` is the device extension of [OpenRoSDE](https://gitlab.com/coarobo/SDE) for the OnRobot RG grippers, which packages the [`onrobot`](https://github.com/UOsaka-Harada-Laboratory/onrobot) driver of the Harada Laboratory of Osaka University, with the description of the OnRobot Quick Changer, a `control_msgs/GripperCommand` action, and the joint states of the fingers.
It names no robot, so any platform or setup of OpenRoSDE that carries an OnRobot gripper activates it.

[![Pipeline](https://img.shields.io/gitlab/pipeline-status/coarobo%2Fopenrosde%2Fopenrosde-device-onrobot?branch=main&logo=gitlab&label=Pipeline)](https://gitlab.com/coarobo/openrosde/openrosde-device-onrobot/-/pipelines)
[![ROS Noetic](https://img.shields.io/badge/ROS_Noetic-Framework-blue?logo=ros&logoColor=white)](http://wiki.ros.org/noetic)
[![Docker](https://img.shields.io/badge/Docker-Layer-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![OpenRoSDE](https://img.shields.io/badge/OpenRoSDE-Device-blue)](https://gitlab.com/coarobo/SDE)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green)](LICENSE)

## 📑 Content

[[_TOC_]]

## 🦾 Supported Devices

| Device | Driver | Documentation |
| --- | --- | --- |
| OnRobot RG2 and RG6 electric grippers, through the OnRobot Compute Box | `onrobot_rg_control` of [`onrobot`](https://github.com/UOsaka-Harada-Laboratory/onrobot) | [docs/onrobot.md](docs/onrobot.md) |
| OnRobot Quick Changer, robot side (QC-R v3) | Description only | [docs/onrobot.md](docs/onrobot.md#quick-changer-description) |

## 🚀 Quick Start

1. Clone the device into `extensions/` of OpenRoSDE, then fetch its submodules and apply its patch:

    ```shell
    git clone https://gitlab.com/coarobo/openrosde/openrosde-device-onrobot.git extensions/openrosde-device-onrobot
    bash ./scripts/update-git-submodules.bash
    ```

2. Activate it in `.env.custom`, with the IP address of the OnRobot Compute Box:

    ```shell
    OPENROSDE_ROBOT_EXTENSIONS="openrosde-device-onrobot"
    OPENROSDE_ONROBOT_COMPUTE_BOX_IP=<compute-box-ip>
    ```

3. Build the images and the workspaces, which adds the Docker layer and the Catkin workspace of the device:

    ```shell
    bash ./BUILD-DOCKER-IMAGE.bash
    bash ./RUN-DOCKER-CONTAINER.bash
    openrosde-reset-catkin-workspaces
    ```

4. Start the driver of the gripper in the container:

    ```shell
    roslaunch openrosde_onrobot_launch onrobot_rg_control_default_realworld.launch
    ```

A setup usually activates the device in its template and starts its launch files from its own panes, as [`docs/extensions.md`](https://gitlab.com/coarobo/SDE/-/blob/dev/docs/extensions.md) of OpenRoSDE describes.

## 📁 Directory Structure

```
openrosde-device-onrobot/
  ci/check-in-container.bash                         # Checks that the CI of OpenRoSDE runs in the container of a setup.
  docker/onrobot-devel/Dockerfile                    # Docker layer: 'ros_control', 'ros_controllers', and 'pymodbus'.
  docker/docker-compose-onrobot.yaml                 # Docker Compose overlay: 'OPENROSDE_ONROBOT_COMPUTE_BOX_IP'.
  docs/onrobot.md                                    # Documentation of the device.
  patches/ros/onrobot_catkin_ws/src/onrobot/         # Patch of the 'onrobot' submodule.
  ros/onrobot_catkin_ws/src/
    onrobot/                                         # Submodule: OnRobot RG and VG descriptions and drivers.
    roboticsgroup_upatras_gazebo_plugins/            # Submodule: mimic joints of the RG grippers in Gazebo.
    openrosde_onrobot_description/                   # Description of the OnRobot Quick Changer.
    openrosde_onrobot_launch/                        # Launch files and nodes of the RG grippers.
```

## 📖 Documentation

| Document | Content |
| --- | --- |
| [docs/onrobot.md](docs/onrobot.md) | Hardware, configuration, network, launch files, gripper action, joint states, and quick changer |
| [openrosde_onrobot_launch](ros/onrobot_catkin_ws/src/openrosde_onrobot_launch/README.md) | Launch files and parameters of the nodes |
| [openrosde_onrobot_description](ros/onrobot_catkin_ws/src/openrosde_onrobot_description/README.md) | Macro of the OnRobot Quick Changer and its parameters |

## 🧪 Testing

The pipeline of this repository clones OpenRoSDE on `dev`, adds this device to the `ur5e` setup, builds its Docker layer and its workspace on the published `ur5e-devel:dev` image, and runs `ci/check-in-container.bash` in a container without network.
That check resolves every launch file with `roslaunch --files` and `--dump-params`, which start no node, compiles the Python nodes, and checks the quick changer with `xacro` and `check_urdf`.

## 🔗 External Resources

- OpenRoSDE: [https://gitlab.com/coarobo/SDE](https://gitlab.com/coarobo/SDE)
- Coarobo GK: [https://coarobo.com/](https://coarobo.com/)

## 🐛 Reporting Issues

Please report any issue using the GitLab issue tracker: [https://gitlab.com/coarobo/openrosde/openrosde-device-onrobot/-/issues](https://gitlab.com/coarobo/openrosde/openrosde-device-onrobot/-/issues).

## 🤝 Contributing

- This repository uses explicit commit messages following the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
- This project follows [Semantic Versioning](https://semver.org/) for releases.
- This project follows the conventions of OpenRoSDE, which its [`AGENTS.md`](https://gitlab.com/coarobo/SDE/-/blob/dev/AGENTS.md) describes.

## 👥 Authors & Acknowledgment

### 🔧 Maintainers

- **Lotfi El Hafi** (lotfi@coarobo.com)

### ✍️ Authors

- **Lotfi El Hafi**

## ⚖️ License

```
Copyright 2019 Coarobo GK

Licensed under the Apache License, Version 2.0
```

See [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE) for details, including the MIT License of the earlier versions of these files in the SDE.

## 📜 Third-Party Software

| Component | Use | License |
| --- | --- | --- |
| [`onrobot`](https://github.com/UOsaka-Harada-Laboratory/onrobot) | Git submodule, patched by `0001-fix-duplicate-world.patch` | MIT License (Takuya Kiyokawa) |
| [`roboticsgroup_upatras_gazebo_plugins`](https://github.com/roboticsgroup/roboticsgroup_upatras_gazebo_plugins) | Git submodule | BSD 3-Clause License (Konstantinos Chatzilygeroudis) |
| [`ros_control`](https://github.com/ros-controls/ros_control), [`ros_controllers`](https://github.com/ros-controls/ros_controllers) | Installed by the Docker layer from the ROS repositories | BSD 3-Clause License |
| [`pymodbus`](https://github.com/pymodbus-dev/pymodbus) 2.5.3 | Installed by the Docker layer from PyPI | BSD 3-Clause License |

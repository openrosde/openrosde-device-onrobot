# OpenRoSDE Device OnRobot

The OnRobot device of [OpenRoSDE](https://github.com/openrosde/openrosde), read "Open Robotic SDE", the open-source Software Development Environment for collaborative robotics research maintained by [Coarobo GK](https://coarobo.com/).
It packages the [`onrobot`](https://github.com/UOsaka-Harada-Laboratory/onrobot) driver of the Harada Laboratory of Osaka University for the OnRobot RG grippers, with the description of the OnRobot Quick Changer, a `control_msgs/GripperCommand` action, and the joint states of the fingers.
It is an extension that OpenRoSDE finds by name once it is cloned into `extensions/openrosde-device-onrobot/` of the core, activated by a setup or by `OPENROSDE_ROBOT_EXTENSIONS`, and it names no robot, so that any platform or setup that carries an OnRobot gripper can use it.

[![Test with OpenRoSDE](https://github.com/openrosde/openrosde-device-onrobot/actions/workflows/test-with-openrosde.yml/badge.svg?branch=main)](https://github.com/openrosde/openrosde-device-onrobot/actions/workflows/test-with-openrosde.yml)
[![ROS Noetic](https://img.shields.io/badge/ROS_Noetic-Framework-blue?logo=ros&logoColor=white)](http://wiki.ros.org/noetic)
[![Docker](https://img.shields.io/badge/Docker-Layer-blue?logo=docker&logoColor=white)](https://www.docker.com/)
[![OpenRoSDE](https://img.shields.io/badge/OpenRoSDE-Device-blue)](https://github.com/openrosde/openrosde)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green)](LICENSE)

## 🦾 Supported Devices

| Device                                                                 | Driver                                                                                   | Documentation                                                 |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| OnRobot RG2 and RG6 electric grippers, through the OnRobot Compute Box | `onrobot_rg_control` of [`onrobot`](https://github.com/UOsaka-Harada-Laboratory/onrobot) | [docs/onrobot.md](docs/onrobot.md)                            |
| OnRobot Quick Changer, robot side (QC-R v3)                            | Description only                                                                         | [docs/onrobot.md](docs/onrobot.md#-quick-changer-description) |

## 🚀 Quick Start

1. Clone the device into `extensions/` of OpenRoSDE, then fetch its submodules and apply its patch:

    ```shell
    git clone https://github.com/openrosde/openrosde-device-onrobot.git extensions/openrosde-device-onrobot
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

A setup usually activates the device in its template and starts its launch files from its own panes, as [`docs/extensions.md`](https://github.com/openrosde/openrosde/blob/dev/docs/extensions.md) of OpenRoSDE describes.

## 📁 Directory Structure

| Path                                        | Content                                                                                                                                                                                                                                 |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docker/onrobot-devel/Dockerfile`           | Docker layer `onrobot-devel`, built on the image below it: `ros_control`, `ros_controllers`, and `pymodbus`.                                                                                                                            |
| `docker/docker-compose-onrobot.yaml`        | Docker Compose overlay, which passes `OPENROSDE_ONROBOT_COMPUTE_BOX_IP` to the container.                                                                                                                                               |
| `ros/onrobot_catkin_ws/`                    | Catkin workspace with `openrosde_onrobot_launch`, `openrosde_onrobot_description` (the OnRobot Quick Changer), and the Git submodules `onrobot` and `roboticsgroup_upatras_gazebo_plugins` (mimic joints of the RG grippers in Gazebo). |
| `patches/`                                  | Patch of the `onrobot` submodule that comments out the `world` link of the RG2 description and its joint.                                                                                                                               |
| `ci/check-in-container.bash`                | Check of the device, which the CI runs in the container of a setup with no network.                                                                                                                                                     |
| `docs/onrobot.md`                           | Documentation of the device.                                                                                                                                                                                                            |
| `.github/workflows/test-with-openrosde.yml` | Workflow that tests this device with the core of OpenRoSDE, as [Continuous Integration](#-continuous-integration) describes.                                                                                                            |
| `.gitmodules`                               | Git submodules of the Catkin workspace, which `bash ./scripts/update-git-submodules.bash` of the core clones.                                                                                                                           |
| `LICENSE`                                   | Text of the Apache License 2.0.                                                                                                                                                                                                         |
| `NOTICE`                                    | MIT notice of the earlier code and notices of third-party software.                                                                                                                                                                     |

The layout is the one of the core, which the [Extensions](https://github.com/openrosde/openrosde/blob/dev/docs/extensions.md) guide of OpenRoSDE describes.

## 📖 Documentation

| Document                                                                                             | Description                                                                                     |
| ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [OnRobot Grippers](docs/onrobot.md)                                                                  | Hardware, configuration, network, launch files, gripper action, joint states, and quick changer |
| [`openrosde_onrobot_launch`](ros/onrobot_catkin_ws/src/openrosde_onrobot_launch/README.md)           | Launch files and parameters of the nodes                                                        |
| [`openrosde_onrobot_description`](ros/onrobot_catkin_ws/src/openrosde_onrobot_description/README.md) | Macro of the OnRobot Quick Changer and its parameters                                           |
| [Basic Usage](https://github.com/openrosde/openrosde/blob/dev/docs/basic-usage.md)                   | Full setup guide of the core of OpenRoSDE                                                       |
| [Extensions](https://github.com/openrosde/openrosde/blob/dev/docs/extensions.md)                     | How OpenRoSDE finds the files of a cloned extension and tests it                                |

## 🧪 Continuous Integration

`.github/workflows/test-with-openrosde.yml` runs on every push to `main`, on every pull request, and by hand (`workflow_dispatch`).
It calls the reusable workflow `extension.yml` of the core, `openrosde/openrosde/.github/workflows/extension.yml@dev` with `core-ref: dev`, which publishes nothing:

- It checks out the core on `dev` and clones the public extensions that `gitlab-ci/extensions.repos` of the core pins, then checks out the commit under test into `extensions/openrosde-device-onrobot/`, so that a pull request from a fork is tested too.
- No setup of the core lists this device, and the core does not pin devices in `gitlab-ci/extensions.repos`, so the workflow passes `extra-extensions: openrosde-device-onrobot`, which adds the device to every setup.
- It passes `setups: ur5e`, so that this device of ROS 1 is tested on the setup `ur5e` alone and never built on a setup of ROS 2.
- It builds the image of the UR5e locally on the published images of the core, then the Docker layer and the Catkin workspace of this device.
- It checks every launch entry point of the panes of the setup and runs `ci/check-in-container.bash` of this device in a container with no network.
- It also checks that no script of the CI can move a robot, and that the meshes of the workspaces convert into valid GLB files.

`ci/check-in-container.bash` resolves every launch file with `roslaunch --files` and `--dump-params`, which start no node, compiles the Python nodes, and checks the quick changer with `xacro` and `check_urdf`.

## 🔗 External Resources

- OpenRoSDE: [https://github.com/openrosde/openrosde](https://github.com/openrosde/openrosde)
- OpenRoSDE website: [https://openrosde.org/](https://openrosde.org/)
- Coarobo GK: [https://coarobo.com/](https://coarobo.com/)
- Osaka University Harada Laboratory OnRobot ROS: [https://github.com/UOsaka-Harada-Laboratory/onrobot](https://github.com/UOsaka-Harada-Laboratory/onrobot)

## 🐛 Reporting Issues

Please report any issue of this device using the GitHub issue tracker: [https://github.com/openrosde/openrosde-device-onrobot/issues](https://github.com/openrosde/openrosde-device-onrobot/issues).
Report any issue of the scripts, the images, or the CI of OpenRoSDE in the issue tracker of the core: [https://github.com/openrosde/openrosde/issues](https://github.com/openrosde/openrosde/issues).

## 🤝 Contributing

- This repository uses explicit commit messages following the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification.
- Open pull requests into `main`, where the workflow of [Continuous Integration](#-continuous-integration) tests them with the core.
- This repository follows the conventions of the core, which [https://github.com/openrosde/openrosde/blob/dev/AGENTS.md](https://github.com/openrosde/openrosde/blob/dev/AGENTS.md) and [https://github.com/openrosde/openrosde/blob/dev/CONTRIBUTING.md](https://github.com/openrosde/openrosde/blob/dev/CONTRIBUTING.md) describe.
- The contributing guide of the organization applies to this repository, which has none of its own: [https://github.com/openrosde/.github/blob/main/CONTRIBUTING.md](https://github.com/openrosde/.github/blob/main/CONTRIBUTING.md).
- Report a security vulnerability privately, as the security policy of the organization describes: [https://github.com/openrosde/.github/blob/main/SECURITY.md](https://github.com/openrosde/.github/blob/main/SECURITY.md).

## 👥 Authors & Acknowledgment

OpenRoSDE is maintained by [Coarobo GK](https://coarobo.com/).
Its maintainers, authors, and contributors are listed in the README of the core: [https://github.com/openrosde/openrosde#-authors--acknowledgment](https://github.com/openrosde/openrosde#-authors--acknowledgment).

## 🕰️ History

The patch of the `onrobot` submodule, the description of the quick changer, the two control launch files, and the three gripper scripts of this device come from the SDE, the predecessor of OpenRoSDE archived at [https://gitlab.com/coarobo/SDE](https://gitlab.com/coarobo/SDE), at commit [`041d164`](https://gitlab.com/coarobo/SDE/-/commit/041d164201db41ac35db5efd7889e6424a84deca) of `dev`, where their earlier history lives.
They were imported without their history, then moved into the Catkin workspace of this device and renamed after what they do rather than after a robot.

## ⚖️ License

```
Copyright 2019 Coarobo GK

Licensed under the Apache License, Version 2.0
```

See [`LICENSE`](LICENSE) for the license, and [`NOTICE`](NOTICE) for the MIT notice of the earlier code and the notices of third-party software.

## 📜 Third-Party Software

This repository holds no third-party code apart from the Git submodules that it pins, which it does not redistribute, and the patch that it applies to one of them.
The Docker layer and the Catkin workspace bring the third-party software below, each under its own license, as [`NOTICE`](NOTICE) records.

| Component                                                                                                                          | Source                                                     | License                                              |
| ---------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------- |
| [`onrobot`](https://github.com/UOsaka-Harada-Laboratory/onrobot)                                                                   | Git submodule, patched by `0001-fix-duplicate-world.patch` | MIT License (Takuya Kiyokawa)                        |
| [`roboticsgroup_upatras_gazebo_plugins`](https://github.com/roboticsgroup/roboticsgroup_upatras_gazebo_plugins)                    | Git submodule                                              | BSD 3-Clause License (Konstantinos Chatzilygeroudis) |
| [`ros_control`](https://github.com/ros-controls/ros_control), [`ros_controllers`](https://github.com/ros-controls/ros_controllers) | Installed by the Docker layer from the ROS repositories    | BSD 3-Clause License                                 |
| [`pymodbus`](https://github.com/pymodbus-dev/pymodbus) 2.5.3                                                                       | Installed by the Docker layer from PyPI                    | BSD 3-Clause License                                 |

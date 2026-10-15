# General guidelines and recommendations for writing 'Dockerfile':
# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/

################################################################################

# Inherit from the image below this layer, given by 'BUILD-DOCKER-IMAGE.bash' of OpenRoSDE.
ARG OPENROSDE_PARENT_IMAGE
FROM ${OPENROSDE_PARENT_IMAGE}

################################################################################

# Install the OnRobot RG2/RG6/VG10/VGC10 grippers ROS dependencies.
# https://github.com/UOsaka-Harada-Laboratory/onrobot

# Gather the OnRobot package dependencies from the ROS repositories.
RUN apt-get update && apt-get install -y --no-install-recommends \
  ros-noetic-ros-control \
  ros-noetic-ros-controllers \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Gather the OnRobot package dependencies from the Python 3 repositories.
RUN pip3 install \
  pymodbus==2.5.3

################################################################################

# Embed the commit hash of this Dockerfile for traceability.
ARG OPENROSDE_DOCKERFILE_COMMIT_SHORT_SHA

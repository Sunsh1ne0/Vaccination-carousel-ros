#!/bin/bash

# Script to run ROS Kinetic with GUI support in Docker

IMAGE_NAME=rostest
CONTAINER_NAME=RosTest

# Handling command line arguments
while [ -n "$1" ]
do
case "$1" in
-n ) CONTAINER_NAME=$2
      shift
      ;;
-i ) IMAGE_NAME=$2
      shift
      ;;
*) echo "$1 unsupported arguement" 
      exit 1
      ;;
esac
shift
done

echo $IMAGE_NAME
echo $CONTAINER_NAME

# Allow X server to be accessed from the local machine
xhost +local:

# Run the Docker container
docker run --rm -it\
  --name=$CONTAINER_NAME \
  --user root \
  --network host \
  --ipc=host \
  -v ./docker_files:/home/docker_files \
  --privileged \
  --env="QT_X11_NO_MITSHM=1" \
  --volume="/etc/localtime:/etc/localtime:ro" \
  -v /dev/bus/usb:/dev/bus/usb \
  --device=/dev/dri \
  --group-add video \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  --env="DISPLAY=$DISPLAY" \
  --env ROS_MASTER_URI=http://localhost:11311 \
  $IMAGE_NAME \
  /bin/bash -c 'source /root/catkin_ws/devel/setup.bash & roscore & rosrun config_manager config_manager.py && wait' 
#   /bin/bash -c "roscore & rosrun config_manager config_manager.py && wait"

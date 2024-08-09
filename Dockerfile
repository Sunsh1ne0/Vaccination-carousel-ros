FROM ros:melodic-ros-base-bionic

RUN echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc && \
    bash ros_entrypoint.sh && \
    mkdir -p root/catkin_ws/src

ENTRYPOINT ["/ros_entrypoint.sh"]

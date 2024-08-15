# FROM ros:melodic-ros-base-bionic
# FROM ros:melodic
FROM tiryoh/ros-melodic-desktop

RUN sudo apt-get update && \
    sudo apt-get install -y cmake && \
    sudo apt install -y python-pip &&\
    pip install pyyaml &&\
    apt install -y python3-pip python3-all-dev python3-rospkg &&\
    pip install psycopg2

RUN apt-get install -y \
    ros-melodic-rospy \
    ros-melodic-rosbash && \
    sudo apt install -y ros-melodic-roslaunch

RUN sudo apt install -y python-rosdep python-rosinstall python-rosinstall-generator python-wstool build-essential
# RUN sudo apt install -y python-rospy


RUN echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc && \
    bash ros_entrypoint.sh && \
    mkdir -p root/catkin_ws/src

WORKDIR /root/catkin_ws/src

RUN /bin/bash -c '. /opt/ros/melodic/setup.bash; catkin_init_workspace /root/catkin_ws/src'

# RUN source /opt/ros/melodic/setup.bash &&\
#     catkin_init_workspace /root/catkin_ws/src

RUN rosdep install --from-paths ./ --ignore-src --rosdistro melodic -y

WORKDIR /root/catkin_ws
RUN /bin/bash -c '. /opt/ros/melodic/setup.bash; cd /root/catkin_ws; catkin_make'

# RUN /bin/bash -c 'source /root/catkin_ws/devel/setup.bash'


WORKDIR /root/catkin_ws/src
RUN /bin/bash -c ". /root/catkin_ws/devel/setup.bash; cd /root/catkin_ws/src; catkin_create_pkg config_manager rospy std_msgs"
# RUN catkin_create_pkg config_manager rospy std_msgse

WORKDIR /root/catkin_ws
RUN /bin/bash -c '. /opt/ros/melodic/setup.bash; cd /root/catkin_ws; catkin_make'


RUN mkdir -p /root/catkin_ws/src/config_manager/scripts

COPY ./config_manager.py /root/catkin_ws/src/config_manager/scripts

# RUN /bin/bash -c "source /opt/ros/melodic/setup.bash; chmod +x /root/catkin_ws/src/config_manager/scripts/config_manager.py"
RUN chmod +x /root/catkin_ws/src/config_manager/scripts/config_manager.py

RUN rm /root/catkin_ws/src/config_manager/CMakeLists.txt

COPY ./CMakeLists.txt /root/catkin_ws/src/config_manager

RUN mkdir -p /home/ubuntu/web/carousel_backend

RUN /bin/bash -c 'source /opt/ros/melodic/setup.bash; cd /root/catkin_ws; catkin_make' && \
    echo "source /root/catkin_ws/devel/setup.bash" >> ~/.bashrc


WORKDIR /
RUN  sudo printf '#!/bin/bash  \n\
    set -e  \n\
    # setup ros environment  \n\
    source "/opt/ros/melodic/setup.bash" --  \n\
    source /root/catkin_ws/devel/setup.bash \n\
    exec "$@"' > ros_entrypoint.sh

        # tail -f /dev/null" > ros_entrypoint.sh

# RUN apt-get install -y supervisor




ENTRYPOINT ["/ros_entrypoint.sh"]

# CMD ["rosrun", "config_manager", "config_manager.py"]
# CMD /bin/bash -c 'source /root/catkin_ws/devel/setup.bash; rosrun config_manager config_manager.py' 
CMD roscore & \
    # rosrun config_manager config_manager.py && \
    python /root/catkin_ws/src/config_manager/scripts/config_manager.py && \
    wait
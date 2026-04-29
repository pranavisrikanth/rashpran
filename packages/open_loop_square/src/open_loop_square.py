#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState


class Drive_Square:
    def __init__(self):
        self.cmd_msg = Twist2DStamped()
        self.is_moving = False

        rospy.init_node('drive_square_node', anonymous=True)

        self.bot_name = "mybota002833"

        self.pub = rospy.Publisher(
            f'/{self.bot_name}/car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )

        rospy.Subscriber(
            f'/{self.bot_name}/fsm_node/mode',
            FSMState,
            self.fsm_callback,
            queue_size=1
        )

        rospy.loginfo("Drive square node started.")

    def fsm_callback(self, msg):
        rospy.loginfo("State: %s", msg.state)

        if msg.state == "NORMAL_JOYSTICK_CONTROL":
            self.stop_robot()
            self.is_moving = False

        elif msg.state == "LANE_FOLLOWING":
            if not self.is_moving:
                rospy.sleep(1)
                self.move_robot()

    def publish_command(self, v, omega):
        self.cmd_msg.header.stamp = rospy.Time.now()
        self.cmd_msg.v = v
        self.cmd_msg.omega = omega
        self.pub.publish(self.cmd_msg)

    def stop_robot(self):
        self.publish_command(0.0, 0.0)

    def move_robot(self):
        self.is_moving = True
        rospy.loginfo("Starting open-loop square movement.")

        for side in range(4):
            rospy.loginfo("Moving forward: side %d", side + 1)
            self.publish_command(0.3, 0.0)
            rospy.sleep(3.5)

            self.stop_robot()
            rospy.sleep(1.0)

            rospy.loginfo("Turning 90 degrees.")
            self.publish_command(0.0, 4.0)
            rospy.sleep(1.0)

            self.stop_robot()
            rospy.sleep(1.0)

        rospy.loginfo("Square movement completed.")
        self.stop_robot()
        self.is_moving = False

    def run(self):
        rospy.spin()


if __name__ == '__main__':
    try:
        duckiebot_movement = Drive_Square()
        duckiebot_movement.run()
    except rospy.ROSInterruptException:
        pass

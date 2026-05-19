#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import AprilTagDetectionArray


class Target_Follower:
    def __init__(self):

        rospy.init_node('target_follower_node', anonymous=True)
        rospy.on_shutdown(self.clean_shutdown)

        self.cmd_vel_pub = rospy.Publisher(
            '/mybota00617/car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )

        rospy.Subscriber(
            '/mybota00617/apriltag_detector_node/detections',
            AprilTagDetectionArray,
            self.tag_callback,
            queue_size=1
        )

        rospy.loginfo("Target follower node started.")
        rospy.spin()

    def tag_callback(self, msg):
        self.move_robot(msg.detections)

    def clean_shutdown(self):
        rospy.loginfo("System shutting down. Stopping robot.")
        self.stop_robot()

    def stop_robot(self):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        cmd_msg.omega = 0.0
        self.cmd_vel_pub.publish(cmd_msg)

    def move_robot(self, detections):

        if len(detections) == 0:
            self.stop_robot()
            return

        x = detections[0].transform.translation.x
        z = detections[0].transform.translation.z

        rospy.loginfo("Tag position x: %.2f, z: %.2f", x, z)

        desired_distance = 0.35

        distance_error = z - desired_distance
        center_error = x

        kp_linear = 0.6
        kp_angular = 3.0

        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()

        cmd_msg.v = kp_linear * distance_error
        cmd_msg.omega = -kp_angular * center_error

        if cmd_msg.v > 0.25:
            cmd_msg.v = 0.25
        elif cmd_msg.v < -0.25:
            cmd_msg.v = -0.25

        if cmd_msg.omega > 4.0:
            cmd_msg.omega = 4.0
        elif cmd_msg.omega < -4.0:
            cmd_msg.omega = -4.0

        if abs(distance_error) < 0.05:
            cmd_msg.v = 0.0

        if abs(center_error) < 0.03:
            cmd_msg.omega = 0.0

        self.cmd_vel_pub.publish(cmd_msg)


if __name__ == '__main__':
    try:
        target_follower = Target_Follower()
    except rospy.ROSInterruptException:
        pass

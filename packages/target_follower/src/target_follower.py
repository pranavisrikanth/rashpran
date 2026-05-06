#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import AprilTagDetectionArray


class Target_Follower:
    def __init__(self):

        rospy.init_node('target_follower_node', anonymous=True)
        rospy.on_shutdown(self.clean_shutdown)

        # Because the launch file uses <group ns="$(env VEHICLE_NAME)">,
        # these topic names must be relative, not /mybota00617/...
        self.cmd_vel_pub = rospy.Publisher(
            'car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )

        rospy.Subscriber(
            'apriltag_detector_node/detections',
            AprilTagDetectionArray,
            self.tag_callback,
            queue_size=1
        )

        rospy.loginfo("Target follower node started.")
        rospy.spin()

    def tag_callback(self, msg):
        self.move_robot(msg.detections)

    def clean_shutdown(self):
        rospy.loginfo("System shutting down. Stopping robot...")
        self.stop_robot()

    def stop_robot(self):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        cmd_msg.omega = 0.0
        self.cmd_vel_pub.publish(cmd_msg)

    def move_robot(self, detections):
        cmd_msg = Twist2DStamped()
        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0

        # Feature 1: Seek object
        # If no AprilTag is visible, rotate slowly until one is found.
        if len(detections) == 0:
            rospy.loginfo("No tag detected - seeking object.")
            cmd_msg.omega = 1.5
            self.cmd_vel_pub.publish(cmd_msg)
            return

        # Feature 2: Look at object
        # Use the first detected tag and rotate to keep it centred.
        tag = detections[0]

        x = tag.transform.translation.x
        y = tag.transform.translation.y
        z = tag.transform.translation.z

        rospy.loginfo("Tag position x:%f y:%f z:%f", x, y, z)

        dead_zone = 0.05
        turn_speed = 1.5

        if x > dead_zone:
            rospy.loginfo("Tag is to the right - turning right.")
            cmd_msg.omega = -turn_speed

        elif x < -dead_zone:
            rospy.loginfo("Tag is to the left - turning left.")
            cmd_msg.omega = turn_speed

        else:
            rospy.loginfo("Tag centered - stopping rotation.")
            cmd_msg.omega = 0.0

        self.cmd_vel_pub.publish(cmd_msg)


if __name__ == '__main__':
    try:
        target_follower = Target_Follower()
    except rospy.ROSInterruptException:
        pass

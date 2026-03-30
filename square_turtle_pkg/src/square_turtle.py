#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist

def move_turtle_square():
    rospy.init_node('turtlesim_square_node', anonymous=True)

    velocity_publisher = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
    rospy.loginfo("Turtles are great at drawing squares!")

    rospy.sleep(1)
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        for _ in range(4):

            # Move forward
            cmd_vel_msg = Twist()
            cmd_vel_msg.linear.x = 2.0
            cmd_vel_msg.angular.z = 0.0

            starttime = rospy.Time.now().to_sec()
            while rospy.Time.now().to_sec() - starttime < 2.0 and not rospy.is_shutdown():
                velocity_publisher.publish(cmd_vel_msg)
                rate.sleep()

            velocity_publisher.publish(Twist())
            rospy.sleep(0.5)

            # Turn 90 degrees more smoothly
            cmd_vel_msg = Twist()
            cmd_vel_msg.linear.x = 0.0
            cmd_vel_msg.angular.z = 1.0

            starttime = rospy.Time.now().to_sec()
            while rospy.Time.now().to_sec() - starttime < 1.57 and not rospy.is_shutdown():
                velocity_publisher.publish(cmd_vel_msg)
                rate.sleep()

            velocity_publisher.publish(Twist())
            rospy.sleep(0.5)

if __name__ == '__main__':
    try:
        move_turtle_square()
    except rospy.ROSInterruptException:
        pass
#!/usr/bin/env python3

import numpy as np
import cv2

import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import CompressedImage


class Lane_Detector:
    def __init__(self):
        self.cv_bridge = CvBridge()

        self.image_sub = rospy.Subscriber(
            "/akandb/camera_node/image/compressed",
            CompressedImage,
            self.image_callback,
            queue_size=1
        )

        rospy.init_node("my_lane_detector")
        rospy.loginfo("my_lane_detector node started")

    def output_lines(self, original_image, lines, color):
        """
        Draws Hough lines on a copy of the image.
        """
        output = np.copy(original_image)

        if lines is not None:
            for i in range(len(lines)):
                l = lines[i][0]
                cv2.line(output, (l[0], l[1]), (l[2], l[3]), color, 2, cv2.LINE_AA)

                cv2.circle(output, (l[0], l[1]), 3, (0, 255, 0), -1)
                cv2.circle(output, (l[2], l[3]), 3, (0, 0, 255), -1)

        return output

    def image_callback(self, msg):
        rospy.loginfo("image_callback")

        img = self.cv_bridge.compressed_imgmsg_to_cv2(msg, "bgr8")

        print("Image is of type: ", type(img))
        print("No. of dimensions: ", img.ndim)
        print("Shape of image: ", img.shape)
        print("Size of image: ", img.size)
        print("Image stores elements of type: ", img.dtype)

        cropped = img[220:480, 0:640]

        hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 70, 255])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)

        kernel = np.ones((3, 3), np.uint8)
        white_mask = cv2.erode(white_mask, kernel, iterations=1)
        white_mask = cv2.dilate(white_mask, kernel, iterations=1)

        white_filtered = cv2.bitwise_and(cropped, cropped, mask=white_mask)

        lower_yellow = np.array([15, 80, 80])
        upper_yellow = np.array([40, 255, 255])
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        yellow_mask = cv2.erode(yellow_mask, kernel, iterations=1)
        yellow_mask = cv2.dilate(yellow_mask, kernel, iterations=1)

        yellow_filtered = cv2.bitwise_and(cropped, cropped, mask=yellow_mask)

        cropped_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        cropped_edges = cv2.Canny(cropped_gray, 80, 160)

        white_gray = cv2.cvtColor(white_filtered, cv2.COLOR_BGR2GRAY)
        white_edges = cv2.Canny(white_gray, 80, 160)

        white_lines = cv2.HoughLinesP(
            white_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=25,
            minLineLength=20,
            maxLineGap=20
        )

        yellow_gray = cv2.cvtColor(yellow_filtered, cv2.COLOR_BGR2GRAY)
        yellow_edges = cv2.Canny(yellow_gray, 80, 160)

        yellow_lines = cv2.HoughLinesP(
            yellow_edges,
            rho=1,
            theta=np.pi / 180,
            threshold=20,
            minLineLength=15,
            maxLineGap=20
        )

        hough_output = np.copy(cropped)

        hough_output = self.output_lines(hough_output, white_lines, (255, 0, 0))

        hough_output = self.output_lines(hough_output, yellow_lines, (0, 255, 255))

        cv2.imshow("Cropped road image", cropped)
        cv2.imshow("White filtered image", white_filtered)
        cv2.imshow("Yellow filtered image", yellow_filtered)
        cv2.imshow("Canny edges", cropped_edges)
        cv2.imshow("White edges", white_edges)
        cv2.imshow("Yellow edges", yellow_edges)
        cv2.imshow("Hough lines output", hough_output)

        cv2.waitKey(1)

    def run(self):
        rospy.spin()


if __name__ == "__main__":
    try:
        lane_detector_instance = Lane_Detector()
        lane_detector_instance.run()
    except rospy.ROSInterruptException:
        pass
    finally:
        cv2.destroyAllWindows()

# import the necessary packages
from imutils.video import VideoStream
import datetime
import imutils
import time
import os
import glob
import cv2

min_area = 500
delta_thresh = 5
min_upload_seconds = 1
min_motion_frames = 2
images_path = "/home/pi/images/"
disable_path = "/home/pi/disable_watch"
max_pictures = 3000


# initialize the first frame in the video stream

class Watcher:
    def __init__(self):
        self.vs = None

    def is_enabled(self):
        return not os.path.exists(disable_path)

    def save_image(self, frame):
        timestamp = datetime.datetime.now()
        save_path = images_path + timestamp.strftime("%Y%m%d.%H%M%S") + ".jpg"
        cv2.imwrite(save_path, frame)
        self.last_uploaded = timestamp
        print("Image saved to " + save_path)
        list_of_files = glob.glob(images_path + "*.jpg")
        full_path = [images_path + "{0}".format(x) for x in list_of_files]
        if len([name for name in list_of_files]) > max_pictures:
            oldest_file = min(full_path, key=os.path.getctime)
            os.remove(oldest_file)
            if os.path.exists(oldest_file.replace(".jpg", ".anlz")):
                os.remove(oldest_file.replace(".jpg", ".anlz"))

    def get_contours(self, gray, avg_frame):
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg_frame))

        thresh = cv2.threshold(frameDelta, delta_thresh, 255,
            cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        return cnts

    def stop_vs(self):
        self.vs.stop()
        cv2.destroyAllWindows()
        self.vs = None

    def create_gray(self, frame):
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

    def run(self):
        while True:
            if not self.is_enabled():
                if self.vs:
                    self.stop_vs()
                print("Disabled, sleeping for 5 seconds")
                time.sleep(5)
                continue

            time.sleep(0.1)
            if not self.vs:
                print("Starting the watch")
                self.vs = VideoStream(-1).start()
                time.sleep(2.0)
                avg_frame = None
                self.last_uploaded = datetime.datetime.now()
                motion_counter = 0

            frame = self.vs.read()
            is_occupied = False
            gray = self.create_gray(frame)

            if avg_frame is None:
                avg_frame = gray.copy().astype("float")
                self.save_image(frame)
                continue
            cv2.accumulateWeighted(gray, avg_frame, 0.7)
            cnts = self.get_contours(gray, avg_frame)

            for c in cnts:
                if cv2.contourArea(c) < min_area:
                    continue
                is_occupied = True
            timestamp = datetime.datetime.now()

            if is_occupied:
                if (timestamp - self.last_uploaded).seconds >= min_upload_seconds:
                    motion_counter += 1
                    if motion_counter >= min_motion_frames:
                        self.save_image(frame)
            else:
                motion_counter = 0
        self.stop_vs()

if __name__ == '__main__':
    catwatcher = Watcher()
    catwatcher.run()

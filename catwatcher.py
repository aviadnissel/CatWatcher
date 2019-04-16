# import the necessary packages
from imutils.video import VideoStream
import datetime
import imutils
import time
import os
import cv2

min_area = 500
delta_thresh = 5
show_video = False
min_upload_seconds = 1
min_motion_frames = 2
images_path = "/home/pi/images/"
disable_path = "/home/pi/disable_watch"
max_pictures = 3000

# construct the argument parser and parse the arguments

vs = None

# initialize the first frame in the video stream

class CatWatcher:
    def __init__(self):
        self.vs = None

    def run(self):
        # loop over the frames of the video
        while True:
            if os.path.exists(disable_path):
                if self.vs:
                    self.vs.stop()
                    cv2.destroyAllWindows()
                    self.vs = None
                print("Disabled, sleeping for 5 seconds")
                time.sleep(5)
                continue

            time.sleep(0.1)
            if not self.vs:
                print("Starting the watch")
                self.vs = VideoStream(src=0).start()
                time.sleep(2.0)
                avgFrame = None
                last_uploaded = datetime.datetime.now()
                motion_counter = 0

            # grab the current frame and initialize the occupied/unoccupied
            # text
            frame = self.vs.read()
            text = "Unoccupied"

            # if the frame could not be grabbed, then we have reached the end
            # of the video
            if frame is None:
                break

            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the first frame is None, initialize it
            if avgFrame is None:
                avgFrame = gray.copy().astype("float")
                continue
        
            cv2.accumulateWeighted(gray, avgFrame, 0.5)
            frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avgFrame))

            thresh = cv2.threshold(frameDelta, delta_thresh, 255,
                cv2.THRESH_BINARY)[1]

            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            biggest_change = None
            biggest_change_size = 0
            # loop over the contours
            marked_frame = frame.copy()
            for c in cnts:
                # if the contour is too small, ignore it
                if cv2.contourArea(c) < min_area:
                    continue

                # compute the bounding box for the contour, draw it on the frame,
                # and update the text
                (x, y, w, h) = cv2.boundingRect(c)
                if w * h > biggest_change_size:
                    biggest_change = frame[y:y+h, x:x+w]
                    biggest_change_size = w * h
                cv2.rectangle(marked_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                text = "Occupied"
            timestamp = datetime.datetime.now()
            # draw the text and timestamp on the frame
            cv2.putText(marked_frame, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
                        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

            if text == "Occupied":
                if (timestamp - last_uploaded).seconds >= min_upload_seconds:
                    motion_counter += 1
                    if motion_counter >= min_motion_frames:
                        save_path = images_path + timestamp.strftime("%Y%m%d.%H%M%S")
                        cv2.imwrite(save_path + ".orig.jpg", frame)
                        last_uploaded = timestamp
                        print("Image saved to " + save_path)
                        list_of_files = os.listdir(images_path)
                        full_path = [images_path + "{0}".format(x) for x in list_of_files]
                        if len([name for name in list_of_files]) > max_pictures:
                            oldest_file = min(full_path, key=os.path.getctime)
                            os.remove(oldest_file)
            else:
                motion_counter = 0
        
            if show_video:
                # show the frame and record if the user presses a key
    
                cv2.imshow("Security Feed", marked_frame)
                cv2.imshow("Thresh", thresh)
                cv2.imshow("Frame Delta", frameDelta)

            key = cv2.waitKey(1) & 0xFF
            # if the `q` key is pressed, break from the lop
            if key == ord("q"):
                break

        # cleanup the camera and close any open windows
        self.vs.stop()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    catwatcher = CatWatcher()
    catwatcher.run()

# import the necessary packages
from imutils.video import VideoStream
import datetime
import imutils
import time
import os
import cv2

min_area = 500
delta_thresh = 5
show_video = True
min_upload_seconds = 3
min_motion_frames = 3
images_path = "C:\\temp\\images\\"
disable_path = "C:\\temp\\disable_watch"

# construct the argument parser and parse the arguments

vs = VideoStream(src=0).start()
time.sleep(2.0)

# initialize the first frame in the video stream
avgFrame = None
last_uploaded = datetime.datetime.now()
motion_counter = 0

# loop over the frames of the video
while True:
    time.sleep(0.05)
    # grab the current frame and initialize the occupied/unoccupied
    # text
    frame = vs.read()
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
    
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < min_area:
            continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"
    timestamp = datetime.datetime.now()
    # draw the text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    if text == "Occupied" and not os.path.exists(disable_path):
        if (timestamp - last_uploaded).seconds >= min_upload_seconds:
            motion_counter += 1
            if motion_counter >= min_motion_frames:
                save_path = images_path + timestamp.strftime("%Y%m%d.%H%M%S") + ".jpg"
                cv2.imwrite(save_path, frame)
                last_uploaded = timestamp
                print("Image saved to " + save_path)
    else:
        motion_counter = 0
        
    if show_video:
        # show the frame and record if the user presses a key
    
        cv2.imshow("Security Feed", frame)
        cv2.imshow("Thresh", thresh)
        cv2.imshow("Frame Delta", frameDelta)

    key = cv2.waitKey(1) & 0xFF
    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

# cleanup the camera and close any open windows
vs.stop()
cv2.destroyAllWindows()

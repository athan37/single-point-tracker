'''
    Aim of this file is for a general enhanced tracking base on similarity on top
    of all the tracker. 
'''
import os
import numpy as np
import cv2
import json
import argparse
import time
from Tracker_DLIB import Tracker_DLIB_create
from similarity_helper import get_similarity

#Choose between the 8 trackers
OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.legacy.TrackerCSRT_create(),
        "kcf": cv2.legacy.TrackerKCF_create(),
        "boosting": cv2.legacy.TrackerBoosting_create(),
        "mil": cv2.legacy.TrackerMIL_create(),
        "tld": cv2.legacy.TrackerTLD_create(),
        "medianflow": cv2.legacy.TrackerMedianFlow_create(),
        "mosse": cv2.legacy.TrackerMOSSE_create(),
        "dlib": Tracker_DLIB_create()
    }

parser = argparse.ArgumentParser(description='Write --test [TEST_NUM] to run')
parser.add_argument('--test', type=int)
parser.add_argument('--tracker', type=str)
parser.add_argument('--log', type=bool)

args = parser.parse_args()
 
# Opening JSON file
NUM_TEST = args.test
data     = None
test_dir_path  = os.path.join(os.getcwd(), 'test_data', f'test{NUM_TEST}')
test_file_path = os.path.join(test_dir_path, 'test_info.json')

with open(test_file_path) as json_file:
    data = json.load(json_file)

TEST_FILE_NAME = data['name']
TRACK_POSITION = data['rect']

track_position = TRACK_POSITION

tracker    = None
prev_frame = None
template   = None
similarity = "None"
track_obj  = None
cap = cv2.VideoCapture(os.path.join(test_dir_path, TEST_FILE_NAME))

tracker = OPENCV_OBJECT_TRACKERS[args.tracker]

success, img = cap.read()
# [x1, y1, x2, y2] = track_position
# cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3, 1)
# cv2.imshow("Window img", img)
# cv2.waitKey(0)

'''
Uncomment the thing below to select region

'''
# # select a bounding box ( ROI )
# bbox = cv2.selectROI("Tracking", img, False, fromCenter=False)
# tracker.init(img, bbox)

x1, y1, x2, y2 = track_position
bbox = [x1, y1, x2 - x1, y2 - y1]
tracker.init(img, bbox)
tracker.init(img, TRACK_POSITION)

def drawBox(img, bbox):
    x, y, w, h = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 3, 1)
    cv2.putText(img, "Tracking", (75, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

guess_templates = []
guess = None
template = None
start = time.time()
while True:
    timer = cv2.getTickCount()
    success, img = cap.read()

    try:
        success, bbox = tracker.update(img)

        [startX, startY, endX, endY] = bbox
        
        guess = img[startY:endY, startX:endX]
    except Exception as e:
        pass

    if template is not None:
        try:
            similarity = get_similarity(template, guess)
            
            if similarity > 6:
                track_obj = (rgb, pos)
                guess_templates.append(track_obj)

        except Exception as e:
            print("Restart tracking")
            max_similarity = -float("inf")
            index = -1
            for i, guess_template in enumerate(guess_templates):
                if similarity > max_similarity:
                    max_similarity = similarity
                    index          = i

            if track_obj is not None:
                tracker.start_track(*guess_templates[index]) 
                #tracker.start_track(*track_obj)

    #Update prev frame
    template = guess

    if success and isinstance(similarity, int) and similarity > 10:
        drawBox(img, bbox)
    else:
        cv2.putText(img, "Loss", (75, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    try:
        cv2.imshow("Frame", img)
    except Exception as e:
        pass

    if cv2.waitKey(1) & 0xff == ord('q'):
        break

end = time.time()

# If the log argument equals True, then we will write a file
if args.log:
    with open(f"Test_{args.test}_result_with_{args.tracker}.txt", 'a') as f:
        f.truncate(0)
        fps = cap.get(cv2. CAP_PROP_FPS) 
        total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration    = total_frame / fps
        actual_duration = end - start
        lines = [
            f"Total frames: {total_frame} frames",
            f"Duration without detection: {duration} seconds",
            f"Duration with detection: {actual_duration} seconds",
            f"Detection time per frame: {(abs(actual_duration - duration) / total_frame) * 1000} ms",
        ]
        for line in lines:
            f.write(line)
            f.write('\n')
            
cap.release()
cv2.destroyAllWindows()
exit()
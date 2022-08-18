import os
import numpy as np
import cv2
import dlib
import json
import argparse
import time
import heapq
from similarity_helper import get_similarity

# VIDEO_URL      = 'https://drive.google.com/uc?id=1Ut903-OaQ6y1OQqyAI3vS6hd7Hf9Jn8m'
# TEST_FILE_NAME = 'output.mp4'
# TRACK_POSITION = (1094, 435, 1359, 657) #First frame
# if not os.path.exists(os.path.join(os.getcwd(), TEST_FILE_NAME)):
#     import gdown
#     gdown.download(TRACK_POSITION, TEST_FILE_NAME)



parser = argparse.ArgumentParser(description='Write --test [TEST_NUM] to run')
parser.add_argument('--test', type=int)
parser.add_argument('--log', type=bool)
parser.add_argument('--output', type=str)
parser.add_argument('--noOfTemplates', type=int, default=5)
parser.add_argument('--minSaveSimilarity', type=int, default=22)
parser.add_argument('--minDisplaySimilarity', type=int, default=14)

args = parser.parse_args()
 
# Opening JSON file
NUM_TEST = args.test
data = None
test_dir_path  = os.path.join(os.getcwd(), 'test_data', f'test{NUM_TEST}')
test_file_path = os.path.join(test_dir_path, 'test_info.json')

with open(test_file_path) as json_file:
    data = json.load(json_file)

TEST_FILE_NAME = data['name']
TRACK_POSITION = data['rect']


track_position = TRACK_POSITION

tracker = None
prev_frame = None
template = None
similarity = "None"
track_obj = None
cap = cv2.VideoCapture(os.path.join(test_dir_path, TEST_FILE_NAME))

total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2. CAP_PROP_FPS) 

#For ouput a video
if args.output:
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    out    = cv2.VideoWriter(f"enhanced_dlib.mp4", fourcc, 20, (width, height), isColor=True)

guess_templates = []
start = time.time()
while cap.isOpened():
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("End of vid")
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if not tracker:
        tracker = dlib.correlation_tracker()
        rect = dlib.rectangle(*track_position)
        tracker.start_track(rgb, rect)

    #Get guess position
    tracker.update(rgb)
    pos = tracker.get_position()
    startX, startY, endX, endY = map(int, [pos.left(), pos.top(), pos.right(), pos.bottom()])

    #Get similarity
    guess = rgb[startY:endY, startX:endX]

    if template is not None:
        try:
            similarity = get_similarity(template, guess)
            
            if similarity > args.minSaveSimilarity:
                track_obj = (rgb, pos)
                heapq.heappush(guess_templates, (similarity, track_obj))
                #guess_templates.append(track_obj)
            
            if len(heappush) > args.noOfTemplates:
                heapq.heappop(guess_templates)

        except Exception as e:
            print("Restart tracking")
            # max_similarity = -float("inf")
            # index = -1
            # for i, guess_template in enumerate(guess_templates):
            #     if similarity > max_similarity:
            #         max_similarity = similarity
            #         index          = i

            if track_obj is not None:
                tracker.start_track(*guess_templates[-1][-1]) 
            
                #tracker.start_track(*track_obj)

    #Update prev frame
    template = guess

    #Draw box + show frame
    if similarity and isinstance(similarity, int) and similarity > args.minDisplaySimilarity:
        cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
        cv2.putText(frame, f"{similarity}", (startX, startY - 15), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)


    if args.output is not None and len(args.output) > 0:
        args.log = None

        out.write(frame)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) == ord('q'): break

end = time.time()
    

if args.log:
    with open(f"Test_{args.test}_result_with_enhanced_dlib.txt", 'a') as f:
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

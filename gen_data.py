'''
This file helps generate data, and auto detect the next folder to be generated

The folder will be like this:
- test_data/
    -> test1/
        -> output.mp4
        -> test_info.json
    -> test2/
        ...

test1, test2, ..., testN is auto written

'''
import os
import cv2
import json
#Choose the folder to hold all test video
TEST_FOLDER_NAME = 'test_data'

#Get max test count to auto write new test
max_test_count = 0
subfolders = [ f.path for f in os.scandir(os.path.join(os.getcwd(), TEST_FOLDER_NAME)) if f.is_dir()] 
for subfolder in subfolders:
    test_count = int(subfolder[subfolder.rindex('test') + len('test'):])
    max_test_count = max(max_test_count, test_count)

new_test_folder = f"test{max_test_count + 1}"
#Use the max test count to write new current test folder
current_test_folder = os.path.join(os.getcwd(), TEST_FOLDER_NAME, new_test_folder)
os.mkdir(current_test_folder)
video_path = os.path.join(current_test_folder, 'output.mp4')
info_path  = os.path.join(current_test_folder, 'test_info.json')

#Click and drag to crop
current_pos = None
points = []
cropping = False
new_template = True
template = None

#Crop function, if count is 2 then the area is saved
def on_mouse(event, x, y, flags,params):

    global new_template, points, cropping, current_pos, template #, rect,startPoint,endPoint
    # get mouse click
    if event == cv2.EVENT_LBUTTONDOWN:
        if new_template:
            points = [(x, y)]
            cropping = True
            new_template = False
        else:
            points.append((x, y))
            cropping = False
            new_template = True
            template = None
            current_pos = None
    elif cropping:
        current_pos = (x, y)

cap = cv2.VideoCapture(0)
waitTime = 50

#Reading the first frame
(grabbed, frame) = cap.read()

count = 1
writtten = False
while True:
    (grabbed, frame) = cap.read()

    cv2.namedWindow('frame')
    cv2.setMouseCallback('frame', on_mouse)

    if cropping:
        [start] = points
        end = start if not current_pos else current_pos
        cv2.rectangle(frame, start, end, (255, 0, 255), 2)
    elif len(points) == 2:
        [(x1, y1), (x2, y2)] = points

        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        #Start writing video from this frame plus storing the position of the template

        #Write a video
        if writtten == False:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            out    = cv2.VideoWriter(video_path, fourcc, 20, (width, height), isColor=True)
            os.chdir(current_test_folder)
            
            with open(info_path, 'a') as f:
                f.truncate(0)
                data = {}
                data['name'] = 'output.mp4'
                data['rect'] = [x1, y1, x2, y2]
                json.dump(data, f)
            writtten = True
        else:
            out.write(frame)

    cv2.imshow('frame', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        out.release() 
        break

cap.release()
cv2.destroyAllWindows()
exit()


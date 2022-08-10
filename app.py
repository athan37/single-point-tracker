from dotenv import load_dotenv 
import os
import cv2
import dlib

load_dotenv()

filedir  = os.getenv("FILE_DIR")
foldername = os.getenv("FOLDER_NAME")
folder_path = os.path.join(os.getcwd(), filedir, foldername)


current_pos = None
points = []
cropping = False
new_template = True
template = None

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


fps = 4
frm_delay = int(1000 / fps)

tracker = None
track_object = None

for filename in os.listdir(folder_path):
    img_path = os.path.join(folder_path, filename)
    try:
        frame = cv2.imread(img_path)
        cv2.setMouseCallback('Frame', on_mouse)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

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

            #choose tracking method here

            if tracker is None:
                tracker = dlib.correlation_tracker()
                rect = dlib.rectangle(x1, y1, x2, y2) #Just a bounding box
                if track_object is None: track_object = (rgb, rect)
                tracker.start_track(*track_object)
            else:
                #tracking
                tracker.update(rgb)
                pos = tracker.get_position()

                startX, startY, endX, endY = map(int, [pos.left(), pos.top(), pos.right(), pos.bottom()])
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                        (0, 255, 0), 2)

        cv2.imshow("Frame", frame)
    except Exception as e:
        print("Error image", img_path, e)

    key = cv2.waitKey(frm_delay) & 0xFF
    if key == ord('q'): break


cv2.destroyAllWindows()
exit()


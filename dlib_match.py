import cv2
import dlib
from skimage.metrics import structural_similarity

#global var
FRAME_NAME = 'frame'

'''
#goal: 
- remove occlusion from other objects
- know when the object is out of the window
- Use ssim index to restart the tracker -> vulnerable to scaling, rotation

Fix this:

.....
 [[183 180 180]
  [184 179 180]
  [184 179 179]
  ...
  [175 152 151]
  [173 152 150]
  [172 152 150]]] asdf
Low similarity
[] [] asdf

'''

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

def is_out_of_box(pos):
    x, y, w, h = cv2.getWindowImageRect(FRAME_NAME)
    startX, startY, endX, endY = map(int, [pos.left(), pos.top(), pos.right(), pos.bottom()])

    horiz_check = startX < x or endX > x + w
    verti_check = startY < y or endY > y + h

    return not (horiz_check or verti_check)

def image_from_object(img_obj):
    rbg, rect = img_obj
    startX, startY, endX, endY = map(int, [pos.left(), pos.top(), pos.right(), pos.bottom()])
    return rbg[startY:endY, startX: endX, :]


def is_low_similarity(img_obj, track_object):
    # img1 = cv2.cvtColor(image_from_object(img_obj), cv2.COLOR_RGB2BGR)
    # img2 = cv2.cvtColor(image_from_object(track_object), cv2.COLOR_RGB2BGR)
    img1 = image_from_object(img_obj)
    img2 = image_from_object(track_object)

    if len(img1) < 7 or len(img2) < 7: return True

    #print(img1, img2, 'asdf')
    score, _ = structural_similarity(img1, img2, full=True, multichannel=True)
    print(score)
    
    return score * 100 < 50


cap = cv2.VideoCapture(0)
waitTime = 50

tracker = None
#Reading the first frame
(grabbed, frame) = cap.read()
method = cv2.TM_CCORR_NORMED


track_object = None
while True:
    (grabbed, frame) = cap.read()

    cv2.namedWindow(FRAME_NAME)
    cv2.setMouseCallback(FRAME_NAME, on_mouse)

    #for dlib
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

            # if is_out_of_box(pos):
            #     print("Out")
            #     tracker = dlib.correlation_tracker() 
            #     tracker.start_track(*track_object)
            #     continue

            # if is_low_similarity((rgb, pos), track_object):
            #     print("Low similarity")
            #     tracker.start_track(*track_object)
            #     cv2.imshow(FRAME_NAME, frame)
            #     tracker.update(rgb)
                # continue

            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())
            # draw the bounding box from the correlation object tracker
            cv2.rectangle(frame, (startX, startY), (endX, endY),
                      (0, 255, 0), 2)

        # ========= tracking by opencv only =========================
        # template = frame[y1 : y2, x1 : x2] if template is None else template
        # h, w = template.shape[:-1]
        # img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # res = cv2.matchTemplate(img_gray, cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), method)
        # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        #
        # top_left = max_loc
        # bottom_right = top_left[0] + w, top_left[1] + h
        #
        # cv2.rectangle(frame, top_left, bottom_right, 200, 2)

        #template = frame[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]

    cv2.imshow(FRAME_NAME, frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break

cap.release()
cv2.destroyAllWindows()
exit()

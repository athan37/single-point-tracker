import cv2
import numpy as np

current_pos = None
points = []
cropping = False
new_template = True
template = None

def get_similarity(img1, img2):
    MIN_MATCH_COUNT = 10
    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches=flann.knnMatch(np.asarray(des1,np.float32),np.asarray(des2,np.float32), 2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)

    return len(good)

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

method = cv2.TM_SQDIFF_NORMED

#Reading the first frame
(grabbed, frame) = cap.read()

count = 1
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
        template = frame[y1 : y2, x1 : x2] if template is None else template

        h, w = template.shape[:-1]
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_gray, cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)


        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        bottom_right = top_left[0] + w, top_left[1] + h

        x1, y1, x2, y2 = *top_left, *bottom_right

        similarity = "None"

        try:
            guess = img_gray[y1:y2, x1:x2]
            similarity = get_similarity(template, guess)

            # if similarity > 10:
            #     template = frame[y1:y2, x1:x2]
        except Exception as e:
            # print(e)
            pass


        cv2.rectangle(frame, top_left, bottom_right, 200, 2)
        cv2.putText(frame, f"{similarity}", (x1, y1 - 15), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

    cv2.imshow('frame', frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('t'):
        count += 1 
        x1, y1 = top_left
        x2, y2 = bottom_right
        cv2.imwrite(f"Img_{count}.png", frame[y1:y2, x1 : x2, :])
    if key == ord('q'): break

cap.release()
cv2.destroyAllWindows()
exit()


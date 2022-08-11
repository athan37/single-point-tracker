'''
2 things:
Record a video from webcam

Get the intial position of the object

'''

import cv2

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

cap = cv2.VideoCapture(0)
waitTime = 50

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

        #Start writing video from this frame plus storing the position of the template

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480))

        out.write(frame)


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

    if key == ord('q'):
        out.release() 
        break

cap.release()
cv2.destroyAllWindows()
exit()


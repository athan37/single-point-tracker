import os
import numpy as np

TEST_FILE_NAME = 'box.mp4'
TRACK_POSITION = (500, 300, 1150, 800) #First frame

if not os.path.exists(os.path.join(os.getcwd(), TEST_FILE_NAME)):
    import gdown
    url = 'https://drive.google.com/uc?id=1Ut903-OaQ6y1OQqyAI3vS6hd7Hf9Jn8m'
    gdown.download(url, TEST_FILE_NAME)

import cv2
import dlib

def get_similarity(img1, img2):
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

    MIN_MATCH_COUNT = 10
    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)
    FLANN_INDEX_KDTREE = 1
    index_params  = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches=flann.knnMatch(np.asarray(des1,np.float32),np.asarray(des2,np.float32), 2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.8*n.distance:
            good.append(m)

    return len(good)

track_position = TRACK_POSITION

tracker = None
prev_frame = None
template = None
similarity = "None"
track_obj = None
cap = cv2.VideoCapture(TEST_FILE_NAME)
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

            if similarity > 200:
                track_object = (rgb, pos)
        except Exception as e:
            print(e, "Restart tracking")
            tracker.start_track(*track_object)
        


    #Update prev frame
    template = guess

    #Draw box + show frame
    if similarity and isinstance(similarity, int) and similarity > 30:
        cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
    cv2.putText(frame, f"{similarity}", (startX, startY - 15), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) == ord('q'): break
    
cap.release()
cv2.destroyAllWindows()
exit()

import os
import numpy as np

# VIDEO_URL      = 'https://drive.google.com/uc?id=1Ut903-OaQ6y1OQqyAI3vS6hd7Hf9Jn8m'
# TEST_FILE_NAME = 'output.mp4'
# TRACK_POSITION = (1094, 435, 1359, 657) #First frame
# if not os.path.exists(os.path.join(os.getcwd(), TEST_FILE_NAME)):
#     import gdown
#     gdown.download(TRACK_POSITION, TEST_FILE_NAME)



import cv2
import dlib
import json
 
# Opening JSON file
data = None
test_dir_path  = os.path.join(os.getcwd(), 'test_data', 'test2')
test_file_path = os.path.join(test_dir_path, 'test_info.json')

with open(test_file_path) as json_file:
    data = json.load(json_file)

TEST_FILE_NAME = data['name']
TRACK_POSITION = data['rect']


def process_img(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.GaussianBlur(img,(3,3),cv2.BORDER_DEFAULT)
    img = cv2.resize(img, (50, 50)) 

    return img

def get_similarity(img1, img2):
    img1 = process_img(img1)
    img2 = process_img(img2)
    
    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)
    FLANN_INDEX_KDTREE = 1
    index_params  = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 60)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches=flann.knnMatch(np.asarray(des1,np.float32),np.asarray(des2,np.float32), 2)
    # store all the good matches as per Lowe's ratio test.
    good = []
    for m,n in matches:
        if m.distance < 0.6*n.distance:
            good.append(m)

    return len(good)

track_position = TRACK_POSITION

tracker = None
prev_frame = None
template = None
similarity = "None"
track_obj = None
cap = cv2.VideoCapture(os.path.join(test_dir_path, TEST_FILE_NAME))
print(os.path.join(test_file_path, TEST_FILE_NAME))
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

            if similarity > 12:
                track_obj = (rgb, pos)
        except Exception as e:
            print(e, "Restart tracking")
            if track_obj is not None:
                tracker.start_track(*track_obj)
        
    #Update prev frame
    template = guess

    #Draw box + show frame
    if similarity and isinstance(similarity, int) and similarity > 8:
        cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
        cv2.putText(frame, f"{similarity}", (startX, startY - 15), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) == ord('q'): break
    
cap.release()
cv2.destroyAllWindows()
exit()

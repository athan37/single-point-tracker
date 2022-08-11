import os

TEST_FILE_NAME = 'box.mp4'
if not os.path.exists(os.path.join(os.getcwd(), TEST_FILE_NAME)):
    import gdown
    url = 'https://drive.google.com/uc?id=1Ut903-OaQ6y1OQqyAI3vS6hd7Hf9Jn8m'
    gdown.download(url, TEST_FILE_NAME)


import cv2
import dlib


tracker = None
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
        rect = dlib.rectangle(500, 300, 1150, 800)
        tracker.start_track(rgb, rect)

    #Get guess position
    tracker.update(rgb)
    pos = tracker.get_position()
    startX, startY, endX, endY = map(int, [pos.left(), pos.top(), pos.right(), pos.bottom()])

    #Draw box + show frame
    cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) == ord('q'): break
    
cap.release()
cv2.destroyAllWindows()
exit()

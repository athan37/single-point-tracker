import cv2
import numpy as np

#Process image for faster similarity count
def process_img(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.GaussianBlur(img,(3,3),cv2.BORDER_DEFAULT)
    img = cv2.resize(img, (50, 50)) 

    return img

#Process image and count the sift features 
#Using FlannBasedMatcher to match the same features of 2 images
#Count the match and return it
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
        if m.distance < 0.7*n.distance:
            good.append(m)

    return len(good)
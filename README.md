# **Single-point-tracking**

## Installation

### **Install openCV for Mac**

- pip(3) install opencv-contrib-python

### **Install dlib for Mac and Window**

- Install cmake 

- Install dlib version 19.23.0 (window can be later version) via pip

## Step to run
1. Generate data  
2. Run a file

## Generate data
- Test folder have this look, where test_info.json contains the information of the object's position to be tracked, in the form **(x1, y1, x2, y2)** for the rectangular bounding box. The output.mp4 is the actual file we are testing. It has the first frame contains the position of the object in test_info.json   
```
test_data/  
  test1/  
    output.mp4  
    test_info.json  
  test2/  
    output.mp4  
    test_info.json  
    ...

To generate data, please take a look at the file gen_data.py

This file will detect how many test cases has been written and auto write a new test case accordingly.

Steps to test:
1. Prepare a webcam
2. Start the file
3. Drag and crop to choose the initial object position. Once you have the crop, it will auto record the video afterward
4. Just take the video normally, shake the webcam or whatever ways you use to record the video
5. When you are done, just hit `q`. The test case will be written.
```

## Tracking with different trackers
1. Check the file opencv_tracking.py to install all the requirements libraries
2. This file depends on Tracker_DLIB.py, which is a wrapper class for dlib.colleration_tracker(), make sure it's there
2. Select a tracker from list of tracker: ["csrt", "mil", "mosse", "tld", "boosting", "medianflow", "dlib", "kcf"]
3. Make sure there is a test case in the test_data/ folder
4. Run the tracker with arguments:  

_For example running test 3 with tracker mosse with output video:_  

> python opencv_tracing.py --tracker mosse --test 3 --output True  

_For example running test 3 with tracker mosse without video but with log data:_  

> python opencv_tracing.py --tracker mosse --test 3 --log True  

## Tracking on webcam with dlib
Run the file dlib_match.py with your webcam on and select a region of interest

## Tracking on webcam with openCV template matching

Run the file opencv_match.py with your webcam on and select a region of interest

## Try out the tracker build up on dlib
It's in the file dlib_enhanced.py, which can be run in the same way as other tracker, but no need to pass the `--tracker` argument  
> python dlib_enhanced.py --test 3 --log True  

This tracker depends on:
- similarity_helper.py file

_For example running test 3 with tracker mosse without video but with log data:_  
> python dlib_enhanced.py --tracker dlib --test 3 --log True  



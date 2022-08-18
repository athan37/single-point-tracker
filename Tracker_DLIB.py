import dlib, cv2
class Tracker_DLIB_create:
    '''
        Wrapper class for dlib so that it can run with the "framework"
    '''
    def __init__(self):
        self.tracker = dlib.correlation_tracker()

    def init(self, img, bbox):
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        x, y, w, h = bbox
        rect = dlib.rectangle(x, y, x + w, y + h) 
        self.tracker.start_track(rgb, rect)

    def update(self, img):
        rgb  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.tracker.update(rgb)
        pos  = self.tracker.get_position()
        x1, y1, x2, y2 = list(map(int, [pos.left(), pos.top(), pos.right(), pos.bottom()]))

        bbox = [x1, y1, x2 - x1, y2 - y1]
        return True, bbox
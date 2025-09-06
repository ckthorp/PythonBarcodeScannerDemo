import cv2
import time
import threading
from queue import Queue

class CaptureThread(threading.Thread):
    def __init__(self, cap, q):
        super().__init__()
        self._running = True
        self._q = q
        self._cap = cap
    
    def run(self):
        timestamp = time.time()
        fps = 0
        frame_count = 0

        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                break
            if not self._q.full():
                self._q.put(frame)
                # Compute FPS
                new_timestamp = time.time()
                frame_count += 1
                if (new_timestamp - timestamp) >= 1:
                    fps = frame_count / (new_timestamp - timestamp)
                    frame_count = 0
                    timestamp = new_timestamp
                    print(fps)

    def stop(self):
        self._running = False

def process(q):
    detector = cv2.QRCodeDetector()

    while True:
        frame = q.get(block=True)
        # detect and decode
        data, bbox, _ = detector.detectAndDecode(frame)

        # check if there is a QRCode in the image
        if data:
            print("data found: ", data)



def main():
    # Open the default camera
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 90)

    q = Queue(maxsize=2)

    thread1 = CaptureThread(cap, q)
    thread2 = threading.Thread(target=process, args=(q,))
    thread3 = threading.Thread(target=process, args=(q,))

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()

    # Release the capture and writer objects
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
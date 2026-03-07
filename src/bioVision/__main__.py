import cv2
import time
from cameraControl import Camera
from imgAnalysis import evaluate_clarity

def main():
    cam = Camera()
    
    while not cam.open():
        time.sleep(1)
    
    while True:
        ret, frame = cam.read_frame()
        cv2.imshow('Real-time Image', frame)
        print(f"当前帧清晰度分数: {evaluate_clarity(frame)}")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    main()
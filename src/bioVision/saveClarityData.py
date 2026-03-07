import cv2
import time
import csv
from common import setup_logger
from cameraControl import Camera
from imgAnalysis import evaluate_clarity

def main():
    logger = setup_logger(filename="SaveClarityData", with_console=True)

    cam = Camera(logger=logger)
    
    while not cam.open():
        time.sleep(1)
    
    with open('./data/clarity_scores.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Timestamp', 'Clarity Score'])
        start_time = time.time()

        while True:
            ret, frame = cam.read_frame()
            cv2.imshow('摄像头实时画面', frame)
            current_time = f"{time.time() - start_time:.3f}"
            evaluate_point = f"{evaluate_clarity(frame):.3f}"
            csv_writer.writerow([current_time, evaluate_point])
            logger.info(f"当前帧清晰度分数: {evaluate_point}")
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cam.release()
    cv2.destroyAllWindows()
    logger.info("程序已结束，摄像头已释放。")

if __name__ == '__main__':
    main()
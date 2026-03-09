import cv2
import time
import csv
import numpy as np
from common import setup_logger
from cameraControl import Camera
from imgAnalysis import evaluate_clarity

def main():
    '''
    该函数实现了摄像头变焦过程中清晰度分数的评估和记录。
    '''
    logger = setup_logger(filename="SaveClarityData", with_console=True)

    cam = Camera(logger=logger)
    
    while not cam.open():
        time.sleep(1)
    
    with open('./data/clarity_scores1.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Timestamp','Zoom Level', 'Clarity Score'])
        start_time = time.time()

        ret, frame = cam.read_frame()
        if not ret:
            logger.error("无法读取摄像头帧，程序将退出。")
            return
        cam.set_focus(1.0)
        time.sleep(3.0)  # 等待摄像头稳定

        for focus_level in np.arange(1.0, 161.0, 1.0):
            cam.set_focus(focus_level)
            time.sleep(0.12)
            ret, frame = cam.read_frame()
            current_time = f"{time.time() - start_time:.3f}"
            evaluate_point = f"{evaluate_clarity(frame):.3f}"
            focus_level = f"{focus_level:.1f}"
            logger.info(f"当前焦距: {focus_level}, 清晰度分数: {evaluate_point}")
            csv_writer.writerow([current_time, focus_level, evaluate_point])
    cam.release()
    logger.info("程序已结束，摄像头已释放。")

if __name__ == '__main__':
    main()
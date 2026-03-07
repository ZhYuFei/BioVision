import cv2
import time
import logging
from datetime import datetime
from cameraControl import Camera
from imgAnalysis import evaluate_clarity

# 设置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(
    filename=f'./logs/BioVision_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log',
    encoding='utf-8',
    mode='w'
)

console_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s-[%(levelname)s]-%(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def main():
    cam = Camera(logger=logger)
    logger.info("正在打开摄像头...")

    while not cam.open():
        logger.warning("摄像头未打开，正在重试...")
        time.sleep(1)
    logger.info("摄像头已成功打开！")
    
    while True:
        ret, frame = cam.read_frame()
        cv2.imshow('Real-time Image', frame)
        clarity_score = evaluate_clarity(frame)
        logger.info(f"当前帧清晰度分数: {clarity_score}")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
    logger.info("程序已结束，摄像头已释放。")


if __name__ == '__main__':
    main()
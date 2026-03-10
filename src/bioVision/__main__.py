import cv2
import time
from common import setup_logger
from cameraControl import Camera
from imgAnalysis import evaluate_clarity
from dataAnalysis import PeakFinder

def main():
    # 设置日志记录器
    logger = setup_logger(filename="BioVision",with_console=True)

    # 初始化摄像头
    cam = Camera(logger=logger)
    logger.info("正在打开摄像头...")
    while not cam.open():
        logger.warning("摄像头未打开，正在重试...")
        time.sleep(1)
    logger.info("摄像头已成功打开！")
    
    # 实时图像处理循环
    while True:
        ret, frame = cam.read_frame()
        cv2.imshow('Real-time Image', frame)
        clarity_score = evaluate_clarity(frame)
        logger.debug(f"当前帧清晰度分数: {clarity_score}")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
    logger.info("程序已结束，摄像头已释放。")


if __name__ == '__main__':
    main()
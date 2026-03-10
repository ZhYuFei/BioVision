from cameraControl import Camera
from dataAnalysis import PeakFinder
from common import setup_logger
from imgAnalysis import evaluate_clarity
import configparser
import time
import cv2

def main():
    config = configparser.ConfigParser()
    config.read('config/default.ini')

    logger = setup_logger(filename="FocusControlTest",with_console=True)

    cam = Camera(logger=logger)

    finder = PeakFinder(config=config)

    logger.info("正在打开摄像头...")
    while not cam.open():
        logger.warning("摄像头未打开，正在重试...")
        time.sleep(1)
    logger.info("摄像头已成功打开！")
    
    # 实时图像处理循环
    while True:
        ret, frame = cam.read_frame()
        cv2.imshow('Real-time Image', frame)

        x = finder.request_next_x()
        if x != -1:
            cam.set_focus(x)
            logger.info(f"正在调整焦距到位置: {x}")
            time.sleep(0.12)  # 等待焦距调整完成

            clarity_score = evaluate_clarity(frame)
            finder.receive_y(x,clarity_score)
            logger.info(f"当前清晰度评分: {clarity_score:.4f}")

            stats = finder.get_statistics()
            logger.info(f"当前进度: {stats['query_count']}次查询, 当前峰值: {stats['current_peak']}")
            logger.info("-" * 40)
        
        if cv2.waitKey(1) & 0xFF == ord('r'):
            finder.reset()
            logger.info("已重置搜索状态。")
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
    logger.info("程序已结束，摄像头已释放。")
    
    # Simulate capturing frames and analyzing them
    

if __name__ == "__main__":
    main()
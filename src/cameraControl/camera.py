import cv2


class Camera:
    """摄像头封装类，提供打开、读取和显示图像功能"""

    def __init__(self, index: int = 0):
        """初始化摄像头对象。
        Args:
            index: 摄像头索引，默认 0 表示默认摄像头。
        """
        self.index = index
        self.cap = None

    def open(self) -> bool:
        """打开摄像头。
        Returns:
            bool: 如果成功打开摄像头则返回 True，否则返回 False。
        """
        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            print("错误：无法打开摄像头")
            return False
        return True

    def read_frame(self):
        """读取一帧图像。
        Returns:
            tuple: (ret, frame)，其中 ret 为布尔值表示读取是否成功，frame 为图像数据。
        """
        if self.cap is None:
            raise RuntimeError("摄像头未打开，请先调用 open()")
        return self.cap.read()

    def release(self):
        """释放摄像头资源。"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

if __name__ == '__main__':
    cam = Camera()
    if not cam.open():
        exit()
    while True:
        ret, frame = cam.read_frame()
        if not ret:
            print("错误：无法读取帧")
            break
        cv2.imshow('摄像头实时画面', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
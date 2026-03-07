import cv2
import configparser

class Camera:
    """摄像头封装类，提供打开、读取和显示图像功能"""

    def __init__(self, index: int = 0):
        """初始化摄像头对象。
        Args:
            index: 摄像头索引，默认 0 表示默认摄像头。
        """
        self.index = index
        self.cap = None

        self.focus = 0.0
        self.zoom = 1.0
        self.flip_mode = 0

        # 从配置文件读取摄像头参数
        config = configparser.ConfigParser()
        if config.read('./config/default.ini'):
            self.focus = config.getfloat('camera', 'focus', fallback=self.focus)
            self.zoom = config.getfloat('camera', 'zoom', fallback=self.zoom)
            self.flip_mode = config.getint('camera', 'flip_mode', fallback=self.flip_mode)
        else:
            print("警告：配置文件 config.ini 未找到，使用默认摄像头参数")
        print(f"摄像头参数 - 焦距: {self.focus}, 变焦: {self.zoom}, 翻转模式: {self.flip_mode}")

        

    def open(self) -> bool:
        """打开摄像头。
        Returns:
            bool: 如果成功打开摄像头则返回 True，否则返回 False。
        """
        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            print("错误：无法打开摄像头")
            return False
        
        self.cap.set(cv2.CAP_PROP_FOCUS, self.focus)
        self.cap.set(cv2.CAP_PROP_ZOOM, self.zoom)


        return True
    
    def set_focus(self, focus: float):
        """设置摄像头焦距。
        Args:
            focus: 焦距值，范围通常为 0.0 到 255.0，具体取决于摄像头型号。
        """
        if self.cap is None:
            raise RuntimeError("摄像头未打开，请先调用 open()")
        self.focus = focus
        self.cap.set(cv2.CAP_PROP_FOCUS, self.focus)
    
    def set_zoom(self, zoom: float):
        """设置摄像头变焦。
        Args:
            zoom: 变焦值，范围通常为 1.0 到 5.0，具体取决于摄像头型号。
        """
        if self.cap is None:
            raise RuntimeError("摄像头未打开，请先调用 open()")
        self.zoom = zoom
        self.cap.set(cv2.CAP_PROP_ZOOM, self.zoom)

    def read_frame(self):
        """读取一帧图像。
        Returns:
            tuple: (ret, frame)，其中 ret 为布尔值表示读取是否成功，frame 为图像数据。
        """
        if self.cap is None:
            raise RuntimeError("摄像头未打开，请先调用 open()")
        
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("无法读取帧")
        
        if self.flip_mode == 1:
            frame = cv2.flip(frame, 1)  # Horizontal flip
        elif self.flip_mode == 2:
            frame = cv2.flip(frame, 0)  # Vertical flip
        elif self.flip_mode == 3:
            frame = cv2.rotate(frame, cv2.ROTATE_180)  # 180° rotation

        return ret, frame

    def release(self):
        """释放摄像头资源。"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

if __name__ == '__main__':
    cam = Camera()
    if not cam.open():
        print("无法打开摄像头，程序退出")
        exit()
    while True:
        ret, frame = cam.read_frame()
        if not ret:
            print("错误：无法读取帧")
            break
        cv2.imshow('Real-time image', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()
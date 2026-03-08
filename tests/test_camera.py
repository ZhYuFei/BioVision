from cameraControl.camera import Camera
import logging

def test_camera_initialization():
    """测试摄像头对象的初始化"""
    logging.basicConfig(level=logging.INFO)
    camera = Camera(logger=logging.getLogger("CameraTest"))
    assert camera.index == 0
    assert camera.focus == 0.0
    assert camera.zoom == 1.0
    assert camera.flip_mode == 0

def test_camera_set_focus():
    """测试设置摄像头焦距"""
    logging.basicConfig(level=logging.INFO)
    camera = Camera(logger=logging.getLogger("CameraTest"))
    camera.open()
    camera.set_focus(5.0)
    assert camera.focus == 5.0

def test_camera_set_zoom():
    """测试设置摄像头缩放"""
    logging.basicConfig(level=logging.INFO)
    camera = Camera(logger=logging.getLogger("CameraTest"))
    camera.open()
    camera.set_zoom(2.0)
    assert camera.zoom == 2.0

def test_camera_read_frame():
    """测试读取摄像头帧"""
    logging.basicConfig(level=logging.INFO)
    camera = Camera(logger=logging.getLogger("CameraTest"))
    camera.open()
    ret, frame = camera.read_frame()
    assert ret is True
    assert frame is not None
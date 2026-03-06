from cameraControl.camera import Camera

def test_camera():
    cam = Camera()
    assert cam.open(), "无法打开摄像头"
    ret, frame = cam.read_frame()
    assert ret, "无法读取摄像头帧"
    assert frame is not None, "读取的帧为空"
    cam.release()
from common import setup_logger

def test_logger_setup():
    """测试日志记录器的设置"""
    logger = setup_logger(filename="test_log", with_console=False)
    assert logger is not None
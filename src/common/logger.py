import logging
import configparser
from datetime import datetime

def str_to_log_level(level_str):
    level_str = level_str.upper()
    if level_str == 'DEBUG':
        return logging.DEBUG
    elif level_str == 'INFO':
        return logging.INFO
    elif level_str == 'WARNING':
        return logging.WARNING
    elif level_str == 'ERROR':
        return logging.ERROR
    elif level_str == 'CRITICAL':
        return logging.CRITICAL
    else:
        raise ValueError(f"无效的日志级别: {level_str}")

def setup_logger(filename="", with_console=True):
    # 设置日志记录器
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(
        filename='./logs/'+filename+f'_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log',
        encoding='utf-8',
        mode='w'
    )

    formatter = logging.Formatter('%(asctime)s-[%(levelname)s]-%(message)s')
    if with_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    config = configparser.ConfigParser()
    if config.read('./config/default.ini'):
        log_level = config.get('logger', 'log_level', fallback='INFO')
        console_log_level = config.get('logger', 'console_log_level', fallback=log_level)
        logger.setLevel(str_to_log_level(log_level))
        if with_console:
            console_handler.setLevel(str_to_log_level(console_log_level))
        logger.info(f"日志级别已设置为: {log_level}，控制台日志级别: {console_log_level}")

    return logger
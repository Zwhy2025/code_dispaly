# coding=utf-8
import datetime
import logging
import subprocess
import sys
import time

import yaml

import genpy
import rospy

logger = logging.getLogger(__name__)


def get_dpkg_version(package_name):
    """
    获取dpkg版本
    :param package_name: 包名
    :return: 版本号
    """
    try:
        result = subprocess.check_output(['dpkg', '-s', package_name])
        result = result.decode('utf-8')
        lines = result.split('\n')
        for line in lines:
            if line.startswith('Version:'):
                version = line.split(' ')[1]
                return version
    except subprocess.CalledProcessError as e:
        logger.error(e)
        return "0.0.0"


def load_yaml(fileName):
    """
    加载yaml
    :param fileName: 文件名
    :return: 是否成功，配置文件内容
    """
    try:
        # 读取yaml
        with open(fileName, 'r') as f:
            config = yaml.safe_load(f)
        return True, config
    except Exception as e:
        logger.error("配置文件读取失败： " + str(e))
        return False, None


def log_to_file(file_name):
    """
    将标准输出重定向到文件
    :param file_name: 文件名
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 将标准输出重定向到文件
            with open(file_name, 'a') as f:
                sys.stdout = f
                result = func(*args, **kwargs)
                # 恢复标准输出
                sys.stdout = sys.__stdout__
                return result

        return wrapper

    return decorator


def log_exec_time(msg=""):
    """
    计算函数执行时间
    :param msg: 日志信息，默认为函数名
    """

    def calculate_time(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            if msg:
                logging.info(msg + ": " + str(end_time - start_time))
            else:
                logging.info(func.__name__ + ": " + str(end_time - start_time))
            return result

        return wrapper

    return calculate_time


def log_func_interval(msg="",level=1):
    """
    记录函数日志范围
    :param msg:
    :return:
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = msg
            if not log:
                log = func.__name__
            byte = "--------"
            logger.info(level * byte +" " + log + ":begin "+level * byte)
            result = func(*args, **kwargs)
            logger.info(level * byte +" " + log + ":end   "+level * byte)
            return result
        return wrapper

    return decorator


def genpyTime_to_datatime(genpy_time):
    """
    转换genpy.Time到datetime.datetime
    :param genpy_time:
    :return:
    """
    nsecs_convert_ratio = 1e-9
    secs = genpy_time.secs + genpy_time.nsecs * nsecs_convert_ratio
    rospy_time = rospy.Time.from_sec(secs)
    datetime_obj = datetime.datetime.fromtimestamp(rospy_time.to_time())
    return datetime_obj


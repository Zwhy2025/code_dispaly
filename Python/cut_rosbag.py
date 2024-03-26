#!/usr/bin/env python
# -- coding:utf-8
import logging

import os
import datetime
import shutil
import time

from rosbag import Bag

from common import tool
from common.tool import num_to_dtime, datatime_to_genpyTime
from plugin.reflex.cut.bag.lazy_bag import LazyBag

logger = logging.getLogger(__name__)


class CutRosbag():

    def __init__(self, _configs):
        # 读取配置
        self.configs = _configs.get('bag')

        # 从配置文件，直接初始化为属性，方便调用
        # 如果子类有自己的同名属性，则优先使用子类的
        for config in [self.configs, _configs]:
            for key, value in config.get('setattr', {}).items():
                setattr(self, key, value)


    @tool.log_exec_time("查找此时间段内的bag文件")
    def find_bag_files(self, start_datetime, end_datetime):
        """
         查找起止时间范围内的bag文件
        :param start_datetime:
        :param end_datetime:
        :return: select_bag  由于查找区间到可能介于两个bag之间，则分为两个文件
                             字典中bag的key为start和end，value为bag路径
        """
        select_bag = {'start': None, 'end': None}
        try:
            logger.info("左区间:{}, 右区间:{}".format(start_datetime, end_datetime))

            # 反向查找节省时间
            for file in reversed(os.listdir(self.bag_dir)):
                # 忽略非bag文件
                if not (file.endswith(".bag") or file.endswith(".active")):
                    continue
                # 从文件名中提取时间信息
                time = self.extract_timestamp(file)
                if time:
                    # 查找完毕直接退出。节省时间
                    if select_bag['start'] and select_bag['end']:
                        break
                    # 符合时间区间赋值到select_bag中
                    if time < start_datetime < time + datetime.timedelta(minutes=self.bag_duration):
                        select_bag['start'] = os.path.join(self.bag_dir, file)
                    if time < end_datetime < time + datetime.timedelta(minutes=self.bag_duration):
                        select_bag['end'] = os.path.join(self.bag_dir, file)

            logger.info("起止时间范围内的bag文件:{}".format(select_bag))
        except Exception as e:
            logger.error("find_bag_files except:{}".format(e))
            return False, select_bag
        return True, select_bag

    @staticmethod
    def extract_timestamp(filename):
        """
        从bag文件名中提取时间
        格式 iplus_bag_2024-03-21-20-23-22_1.bag
        切割完之后 "iplus" "bag" "2024-03-21-20-23-22" "1.bag"
        取第三个部分，转换为时间戳
        :param filename:
        :return:
        """
        try:
            parts = filename.split("_")
            if len(parts) > 2:
                str_time = parts[2]
                return datetime.datetime.strptime(str_time, "%Y-%m-%d-%H-%M-%S")
            else:
                return None
        except Exception as e:
            logger.error("extract_timestamp except: " + str(e))
            return None

    @tool.log_exec_time("执行切割bag操作总耗时")
    @tool.log_func_interval(level=2)
    def cut_bag_files(self, select_bag, output_file, start_datetime, end_datetime, is_limit=False):
        """
        :func  filter_rosbag: 由于目标裁切得到bag，肯呢个来自多个文件
                              所以需要根据mode判断是写入还是追加
                              耗时长，且有可能需要调用两次，来合并到同一个文件
        :param select_bag:
        :param start_datetime:
        :param end_datetime:
        :param is_limit: 是否开启cpu限制，
                         如果开启，后续所有调用耗时操作都会被限制cpu
                         注意如果瞬间调用，可能放任cpu全速运行
        :return:
        """
        try:

            # 执行过滤操作
            for part in select_bag:
                if select_bag[part]:
                    ok = self.filter_rosbag(select_bag[part],
                                            start_datetime,
                                            end_datetime,
                                            output_file,
                                            mode="w" if self.is_write(select_bag, part) else "a",
                                            is_limit=is_limit)
                    if not ok:
                        logger.error("过滤失败")
                        return False

                    # 如果两个文件都是写入模式，那写一次就行了，此时两个文件是同一份
                    if (select_bag["start"] and
                            select_bag["end"] and
                            self.is_write(select_bag, "start") and self.is_write(select_bag, "end")):
                        logger.info("切割区间处于同一个bag包，跳过下次截取")
                        break

        except Exception as e:
            logger.error("cut_bag_files except: " + str(e))
            return False
        return True

    @staticmethod
    def is_write(select_bag, part='start'):
        """
        如果bag文件字典中两个都不存在，则什么模式都无所谓，不会进入切割函数
        如果bag文件字典中有一个不存在，则肯定是写入模式
        如果两个文件相同，那也肯定是写入模式
        如果两个文件不相同，且都存在，则处理第一个文件是写入，第二个文件是追加
        :param select_bag: 
        :param part: 
        :return: 
        """
        if (select_bag.get('start') and
                select_bag.get('end') and
                select_bag['start'] != select_bag['end']):
            return part == 'start'
        else:
            return True

    @tool.log_exec_time("生成filted_rosbag.bag总时间")
    @tool.log_func_interval(level=1)
    def cut_rosbag(self, target_datetime, reason, is_limit=False):
        """
        :func  find_bag_files  基本不消耗cpu
        :func  cut_bag_files： 执行切割bag操作主函数，消耗巨量计算资源

        :param start_datetime：
        :param end_datetime:
        :param is_limit: 是否开启cpu限制，
                         如果开启，后续所有调用耗时操作都会被限制cpu
                         注意如果瞬间调用，可能放任cpu全速运行
        :return:
        """
        try:
            if not self.configs:
                logger.error("未正常读取到配置文件")
                return False

            output_file, start_datetime, end_datetime = self.get_edge_and_path(target_datetime, reason)

            if not output_file or not start_datetime or not end_datetime:
                logger.error("生成时间戳边界与文件路径失败")
                return False

            ok, select_bag = self.find_bag_files(start_datetime, end_datetime)
            if not ok:
                logger.error("查找bag文件失败")
                return False

            if not select_bag.get('start') and not select_bag.get('end'):
                logger.error("没有找到起止时间范围内的bag文件")
                return False

            ok = self.cut_bag_files(select_bag, output_file, start_datetime, end_datetime, is_limit=is_limit)
            if not ok:
                logger.error("切割bag文件失败")
                return False

        except Exception as e:
            logger.error("cut_bag except: " + str(e))
            return False
        return True

    @tool.log_exec_time("筛选数据包耗时")
    @tool.log_func_interval(level=3)
    def filter_rosbag(self, inbag_filename, start_datetime, end_datetime, outbag_filename='output.bag',
                      mode='w', is_limit=False):
        """
        :func  generat_inbag： 从文件中读取rosbag数据，也包括如果bag未索引需要重索引，耗时最高的地方
        :func  read_messages： 文件中数据的获取生成器接口，耗时也高

        :param inbag_filename:  数据来源bag
        :param outbag_filename: 裁切后的bag
        :param start_datetime:
        :param end_datetime:
        :param mode:            对于二次处理情况，首次为写入模式，后续为追加模式
        :param is_limit: 是否开启cpu限制，
                         如果开启，后续所有调用耗时操作都会被限制cpu
                         注意如果瞬间调用，可能放任cpu全速运行
        :return:
        """
        logger.info("开始裁切数据包文件:{}".format(inbag_filename))
        logger.info("裁切时间段：{} 到 {}".format(start_datetime, end_datetime))

        # 检查输入数据包文件是否存在
        if not os.path.isfile(inbag_filename):
            logger.warning('找不到输入数据包文件 [%s]' % inbag_filename)
            return False

        # 检查输入和输出文件名是否相同
        if os.path.realpath(inbag_filename) == os.path.realpath(outbag_filename):
            logger.warning('输入和输出文件不能相同 [%s]' % inbag_filename)
            return False

        # 打开输入和输出数据包文件
        out_bag = Bag(outbag_filename, mode)
        in_bag = self.generat_inbag(inbag_filename, is_limit)
        logger.info("此bag数据起止时间：{} 到 {}".format(num_to_dtime(in_bag.get_start_time()),
                                                        num_to_dtime(in_bag.get_end_time())))
        if in_bag:
            try:
                # 开始裁切
                begin = time.time()
                index = None
                logger.info("开始筛选数据时间戳,使用cpu优化：{}，优化超参：{}".format(is_limit, self.limit_LazyBag))
                for topic, raw_msg, t in in_bag.read_messages(start_time=datatime_to_genpyTime(start_datetime),
                                                              end_time=datatime_to_genpyTime(end_datetime),
                                                              raw=True,
                                                              sleep_time=self.limit_read):
                    # 打印从输入数据包文件中筛选出的消息
                    if not index:
                        index = "Zwhy2025"
                        logger.info("时间戳筛选用时:{}秒".format(time.time() - begin))
                        logger.info("开始写入数据包,使用cpu优化：{}，优化超参：{}".format(is_limit, self.limit_LazyBag))
                        begin = time.time()

                    # 降低cpu占用，如果是系统空闲可以选择不限制cpu
                    if is_limit:
                        time.sleep(self.limit_filter)

                    out_bag.write(topic, raw_msg, t, raw=True)

                logger.info("写入bag耗时:{}秒".format(time.time() - begin))
                if not index:
                    logger.error("裁切时间段不存在")
                    return False
            except Exception as e:
                logger.error("filter_rosbag except： " + str(e))
                return False
            finally:
                # 关闭输入和输出数据包文件
                in_bag.close()
                out_bag.close()
            return True

    @tool.log_exec_time("读取数据包总耗时（可能包含重建索引时间）")
    def generat_inbag(self, inbag_filename, is_limit=False):
        """
        生成LazyBag对象 如果是active文件，需要先重建索引
        :param inbag_filename:
        :param is_limit: 是否开启cpu限制，
                       如果开启，后续所有调用耗时操作都会被限制cpu
                       注意如果瞬间调用，可能放任cpu全速运行
        :return:
        """
        try:
            filename = inbag_filename

            if inbag_filename.endswith(".active"):
                logger.info("此bag正在录制，准备重新索引bag")

                # 拷贝备份文件
                backup_filename = os.path.expanduser(self.reindex_bag_file)
                shutil.copyfile(filename, backup_filename)

                # 重建索引
                self.rosbag_reindex(backup_filename, is_limit=is_limit)
                filename = backup_filename
                logger.info("后续使用备份文件进行裁切：{}".format(backup_filename))

            logger.info("开始读取数据包：{},使用cpu优化：{}，优化超参：{}".format(filename, is_limit, self.limit_LazyBag))
            in_bag = LazyBag(filename, "r",
                             sleep_time=self.limit_LazyBag if is_limit else 0,
                             limit_LazyBag_boundary=self.limit_LazyBag_boundary)
        except Exception as e:
            logger.error("generat_inbag except： " + str(e))
            return None
        return in_bag

    @tool.log_exec_time("重建索引耗时")
    def rosbag_reindex(self, inbag_filename, is_limit=True):
        """
        重建索引
        :param inbag_filename:
        :param is_limit: 是否开启cpu限制，
               如果开启，后续所有调用耗时操作都会被限制cpu
               注意如果瞬间调用，可能放任cpu全速运行
        :return:
        """
        try:
            logger.info("开始重建bag索引第一部分,使用cpu优化：{},优化超参2：{}".format(is_limit, self.limit_reindex_1, ))
            in_bag = LazyBag(inbag_filename, "a", allow_unindexed=True,
                             sleep_time=self.limit_reindex_1 if is_limit else 0)

            # 注意reindex内部也有耗时操作，是通过limit_reindex_1来控制，都属于reindex的耗时 所以没有分开
            index = None
            for _ in in_bag.reindex():
                if not index:
                    index = "Zwhy2025"
                    logger.info(
                        "开始重建bag索引第二部分,使用cpu优化：{},优化超参2：{}".format(is_limit, self.limit_reindex_2))

                if is_limit:
                    time.sleep(self.limit_reindex_2)
            in_bag.close()
        except Exception as e:
            logger.error("rosbag_reindex except： " + str(e))
            return False

    def get_edge_and_path(self, target_datetime, reason):
        try:
            # 构建目标目录路径
            filtered_dir = os.path.expanduser(self.filtered_dir)
            target_dir = os.path.join(filtered_dir,
                                      "{0}_{1}".format(target_datetime.strftime("%Y-%m-%d-%H-%M-%S"), reason))
            # 构建日志文件路径
            path = os.path.join(target_dir, self.filtered_bag_name)

            # 检查目录是否存在，如果不存在则创建
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            else:
                logger.info("目标目录已存在： " + target_dir)

            # 生成时间戳列表
            start_time = target_datetime - datetime.timedelta(minutes=self.time_range)
            end_time = target_datetime + datetime.timedelta(minutes=self.time_range)

        except Exception as e:
            logger.error("get_edge_and_path except: " + str(e))
            return None, None, None

        return path, start_time, end_time

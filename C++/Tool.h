/**
 * @file JTool.h
 * @brief 提供一些常用的工具函数
 * @version 1.0
 * @date 23-11-8
 * @todo 封装为通用工具类
 */
#include <string>
#include <cstring>
#include <vector>
#include <cmath>
#include <unistd.h>

namespace jjobs {
    namespace tool {

        /** 用于执行linux命令 */
        int exec(const std::string cmd, std::vector<std::string> &resvec);

        /** 获取系统中指定软件的dkpg版本号 */
        std::string GetVersion(std::string process_name);

        /** pwn模拟加速状态，用于键盘，按键等离散值 */
        double  PwmAcceleration(double data, int status, double step,double maxSpeed =1,double tolerance = 1e-5);

        /** 获取当前时间字符串 */
        std::string GetCurrTimeStr();

        /** 获取当前路径 */
        std::string getCurrentPath();

    }
}

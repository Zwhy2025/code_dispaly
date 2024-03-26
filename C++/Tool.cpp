//
// Created by zwhy2022 on 23-11-28.
//

#include "Tool.h"

namespace jjobs {
    namespace tool {

        /**
         * @brief 执行命令并获取输出结果
         *
         * 此函数通过执行给定的命令，并将命令的标准输出逐行存储到字符串向量中。
         *
         * @param cmd 要执行的命令
         * @param resvec 用于存储命令输出的字符串向量
         * @return 命令输出的行数，如果执行失败则返回 -1
         */
        int exec(const std::string cmd, std::vector<std::string> &resvec) {
            resvec.clear();  // 清空输出结果向量

            // 打开管道并执行命令
            FILE *pp = popen(cmd.c_str(), "r");
            if (!pp) {
                return -1;  // 打开管道失败，返回错误码
            }

            char tmp[1024];
            // 逐行读取命令输出
            while (fgets(tmp, sizeof(tmp), pp) != NULL) {
                // 去除行末尾的换行符
                if (tmp[strlen(tmp) - 1] == '\n') {
                    tmp[strlen(tmp) - 1] = '\0';
                }
                // 将当前行添加到输出结果向量
                resvec.push_back(tmp);
            }

            pclose(pp);  // 关闭管道
            return resvec.size();  // 返回命令输出的行数
        }


        /**
         * @brief 用dpkg命令获取系统中的软件版本
         * @param process_name 获取版本号的程序名
         * @return 返回版本号字符串
         */
        std::string GetVersion(std::string process_name) {
            std::vector<std::string> vect;
            std::string cmd = "dpkg -l | grep " + process_name + " | awk '{print $3}'";
            int status = exec(cmd, vect);
            if (status) {
                return vect[0];
            } else {
                return "0.0.0";
            }
        }

        /**
     * @brief 根据上一帧值和状态计算当前数值
     * @param data      传入上一帧的值
     * @param status    当前状态（1,0,-1 三种状态）
     * @param step      步长
     * @param maxData   最大值
     * @param tolerance 容差（用于逼近0）
     * @return 当前数值
     * @note #todo status 可用枚举类型增加代码可读性
     */
        double PwmAcceleration(double data, int status, double step, double maxData, double tolerance) {

            /** 用于处理浮点数逼近与零的情况，直接判定为0 */
            if (status == 0 && std::abs(data) < tolerance) {
                return 0.0;
            }

            /** 根据状态叠加步长 */
            if (status == 1 || (status == 0 && data < -tolerance)) {
                data += step;
                data = std::min(data, maxData);  // 使用 std::min 限制速度范围
            } else if (status == -1 || (status == 0 && data > tolerance)) {
                data -= step;
                data = std::max(data, -maxData); // 使用 std::max 限制速度范围
            }
            return data;
        }

        /**
         * 获取当前时间字符串
         */
        std::string GetCurrTimeStr() {
            time_t now = time(nullptr);
            tm *ltm = localtime(&now);
            char time_str[20];
            sprintf(time_str, "%04d-%02d-%02d %02d:%02d:%02d", ltm->tm_year + 1900, ltm->tm_mon + 1, ltm->tm_mday,
                    ltm->tm_hour, ltm->tm_min, ltm->tm_sec);
            return std::string(time_str);
        }

        /** 获取当前路径  */
        std::string getCurrentPath() {
            char buffer[FILENAME_MAX];
            if (getcwd(buffer, sizeof(buffer)) != NULL) {
                return std::string(buffer);
            } else {
                return "";
            }

        }
    }
}
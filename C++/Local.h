//
// Created by zwhy2022 on .
//
/**
 * @file Local.h
 * @brief 本地参数加载器，对管理器提供方法获取本地参数
 * @version 1.0
 * @date 23-12-5
 * @todo 暂无
 */
#ifndef JJOBS_LOCAL_H
#define JJOBS_LOCAL_H
#include "yaml-cpp/yaml.h"
#include "jjobs/log.h"

namespace jjobs {
    class Local {
    public:
        struct Global {
            bool debug = false;                                      ///< 是否开启调试模式
            int  log_level = 1;                                      ///< 日志等级
            bool enable_feedback = true;                             ///< 是否开启速度反馈回环控制

            bool from_yaml(const YAML::Node &node);
        };

        struct Interfaces {
            std::string jcar3_path = "/j3/jjobs/control";                ///< 三代机形路径
            std::string joystick = "/jzhw/joy";                          ///< 手柄数据话题
            std::string joy3_controller = "/jjobs/joy3/control";         ///< joy3外部接口，现内部使用
            std::string carly_keyboard =  "/carly/keyboard";             ///< 网页前端事件读取点
            std::string chassis_speed= "/jzhw/joy_ctrl";                 ///< 底盘速度下发接口
            std::string carrier_speed=  "/emb/carrier/speed/control";    ///< 载具速度下发接口
            std::string chassis_speed_feedback= "/emma_odom_vel";        ///< 底盘速度反馈接口
            std::string run_module=  "/jjobs/module/control";            ///< 运行模块控制接口
            std::string rotation = "/jzhw/rotation";                     ///< 反馈旋转角度
            std::string set_rotate = "/set_rotate_angle";                ///< 设置旋转角度

            bool from_yaml(const YAML::Node &node);
        };

        struct Variables {
            double tolerance = 1e-5;                                     ///< 误差容忍度
            double automatic_deceleration_threshold = 0.01;              ///< 自动减速阈值
            double automatic_deceleration_ratio = 0.5;                   ///< 自动减速比例
            double feedback_tolerance_velocity = 0.05;                    ///< 速度反馈回环控制误差容忍度
            int idle_time = 1800;                                      ///< 空闲时间
            bool from_yaml(const YAML::Node &node);
        };
    private:
        Local();

    public:
        /** 读取全局参数 */
        bool LoadParams();

        // 单例获取本地配置文件对象
        static std::shared_ptr<Local> &GetInstance();
    public:

        // 提供只读访问接口，不允许修改数据
         const Global& G_() const {
            return _g;    ///<全局参数
        }

        const Interfaces& I_() const {
            return _i;    ///<接口
        }

        const Variables& V_() const {
            return _v;    ///<可变参数
        }
    private:
        Global _g;                  ///< 全局参数
        Interfaces _i;              ///< 接口
        Variables _v;               ///< 可变参数
        static std::shared_ptr<Local> _instance;
    };

}

#endif //JJOBS_LOCAL_H

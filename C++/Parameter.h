/**
 * @file Parameter.h
 * @brief 参数管理器，提供静态方法获取不可变参数
 * @version 1.0
 * @date 23-12-5
 * @todo 暂无
 */
#ifndef JJOBS_PARAMETER_H
#define JJOBS_PARAMETER_H

#include "JCar3/JCar3.h"
#include "Local/Local.h"

namespace jjobs{
    class Parameter {
    private:
        Parameter();
    public:
        /** 初始化 */
        bool Init();

        static std::shared_ptr<Parameter> &GetInstance();

        /**  外界获取本地参数 */
        static  std::shared_ptr<Local> Local_() {
            return _ptLocal;
        }

        /**  外界获取机型 */
        static std::shared_ptr<JCar3> JCar3_() {
            return _ptJCar3;
        }

    private:
        static std::shared_ptr<Local> _ptLocal;                               ///< 本地参数集合
        static std::shared_ptr<JCar3> _ptJCar3;                               ///< 机型参数集合
        static std::shared_ptr<Parameter> _instance;
    };
}

#endif //JJOBS_PARAMETER_H

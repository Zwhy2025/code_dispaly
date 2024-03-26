//
// Created by zwhy2022 on 23-12-5.
//

#include "Parameter.h"

namespace jjobs {

    std::shared_ptr<Parameter> Parameter::_instance = nullptr;
    std::shared_ptr<JCar3> Parameter::_ptJCar3 = nullptr;
    std::shared_ptr<Local> Parameter::_ptLocal = nullptr;

    Parameter::Parameter() {

    }

    bool Parameter::Init() {

        /** 先加载本地参数，因为全局参数中有使用本地参数 */
        _ptLocal = Local::GetInstance();
        SPD_INFO << "加载本地参数...";
        if (!_ptLocal->LoadParams()) {
            SPD_ERROR << "加载本地参数失败";
            return false;
        }

        /** 加载机型参数 */
        _ptJCar3 = std::make_shared<JCar3>();
        SPD_INFO << "加载机型参数...";
        if (!_ptJCar3->LoadParams()) {
            SPD_ERROR << "加载机型参数失败";
            return false;
        }
        return true;
    }

    std::shared_ptr<Parameter> &Parameter::GetInstance() {
        if (!_instance) {
            _instance = std::shared_ptr<Parameter>(new Parameter());
        }
        return _instance;
    }

}
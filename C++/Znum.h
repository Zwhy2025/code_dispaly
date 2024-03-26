/**
 * @file Znum.h
 * @brief 用于生成带有ToString方法的枚举类的宏
 * @date 2023-12-1
 * @version 1.0
 * @note 本文件中的宏定义参考了以下文章：https://stackoverflow.com/questions/5093460/how-to-convert-an-enum-type-variable-to-a-string/42317427#42317427
 */

#include <boost/preprocessor.hpp>

// 辅助宏，用于创建带有额外括号的元组
#define HELPER1(...) ((__VA_ARGS__)) HELPER2
#define HELPER2(...) ((__VA_ARGS__)) HELPER1
#define HELPER1_END
#define HELPER2_END

// 将每个元组添加括号的宏
#define ADD_PARENTHESES_FOR_EACH_TUPLE_IN_SEQ(sequence) BOOST_PP_CAT(HELPER1 sequence,_END)

// 创建带有特定条件的枚举元素的宏
#define CREATE_ENUM_ELEMENT_IMPL(elementTuple)                                          \
BOOST_PP_IF(BOOST_PP_EQUAL(BOOST_PP_TUPLE_SIZE(elementTuple), 4),                       \
    BOOST_PP_TUPLE_ELEM(0, elementTuple) = BOOST_PP_TUPLE_ELEM(2, elementTuple),        \
    BOOST_PP_TUPLE_ELEM(0, elementTuple)                                                \
),

// 将元素推送到元组的宏
#define CREATE_ENUM_ELEMENT(r, data, elementTuple)                                      \
    CREATE_ENUM_ELEMENT_IMPL(BOOST_PP_TUPLE_PUSH_BACK(elementTuple, _))

// 为枚举元素定义switch语句的宏
#define DEFINE_CASE_HAVING_ONLY_ENUM_ELEMENT_NAME(enumName, element)                                        \
    case enumName::element : return BOOST_PP_STRINGIZE(element);

#define DEFINE_CASE_HAVING_STRING_REPRESENTATION_FOR_ENUM_ELEMENT(enumName, element, stringRepresentation)  \
    case enumName::element : return stringRepresentation;

// 生成每个枚举元素的switch语句的宏
#define GENERATE_CASE_FOR_SWITCH(r, enumName, elementTuple)                                                                                                 \
    BOOST_PP_IF(BOOST_PP_EQUAL(BOOST_PP_TUPLE_SIZE(elementTuple), 1),                                                                                       \
        DEFINE_CASE_HAVING_ONLY_ENUM_ELEMENT_NAME(enumName, BOOST_PP_TUPLE_ELEM(0, elementTuple)),                                                          \
        DEFINE_CASE_HAVING_STRING_REPRESENTATION_FOR_ENUM_ELEMENT(enumName, BOOST_PP_TUPLE_ELEM(0, elementTuple), BOOST_PP_TUPLE_ELEM(1, elementTuple))     \
    )

// 定义带有ToString方法的枚举类的最终宏
#define Znum(EnumName, enumElements)          \
enum class EnumName {                                                           \
    BOOST_PP_SEQ_FOR_EACH(                                                      \
        CREATE_ENUM_ELEMENT,                                                    \
        0,                                                                      \
        ADD_PARENTHESES_FOR_EACH_TUPLE_IN_SEQ(enumElements)                     \
    )                                                                           \
};                                                                              \
inline const char* ToString(const EnumName element) {                           \
        switch (element) {                                                      \
            BOOST_PP_SEQ_FOR_EACH(                                              \
                GENERATE_CASE_FOR_SWITCH,                                       \
                EnumName,                                                       \
                ADD_PARENTHESES_FOR_EACH_TUPLE_IN_SEQ(enumElements)             \
            )                                                                   \
            default: return "[Unknown " BOOST_PP_STRINGIZE(EnumName) "]";       \
        }                                                                       \
}

/////< demo
//#include <iostream>
//Znum(Elements,                 ///< 枚举类型名称
//    (Element1)                 ///< 枚举元素
//    (Element2)
//    (Element3,"Element3",1000) ///<支持自定义枚举值
//    (Element4)
//    (Element5)
//    (Element6, "Element6")     ///数值不存在则默认为上一个数值+1
//    (Element7))
//
//
//int main() {
//    /** 打印枚举字面值对应的字符串 */
//    std::cout << ToString(Elements::Element1) << std::endl;
//    std::cout << ToString(Elements::Element2) << std::endl;
//    std::cout << ToString(Elements::Element3) << std::endl;
//    std::cout << ToString(Elements::Element4) << std::endl;
//    std::cout << ToString(Elements::Element5) << std::endl;
//    std::cout << ToString(Elements::Element6) << std::endl;
//    std::cout << ToString(Elements::Element7) << std::endl;
//
//    ///** 不能隐式类型转换为int 需要强制转换  */
//    std::cout << (int)Elements::Element2<< std::endl;
//    std::cout << (int)Elements::Element3<< std::endl;
//    std::cout << (int)Elements::Element4<< std::endl;
//    std::cout << (int)Elements::Element5<< std::endl;
//    std::cout << (int)Elements::Element6<< std::endl;
//    std::cout << (int)Elements::Element7<< std::endl;
//
//    /** 可以从int 强制转换为对应枚举 */
//    if(Elements::Element1 ==static_cast<Elements>(0)){
//    std::cout <<"Element3 fine!"<< std::endl;
//    }
//
//    if(Elements::Element3 ==static_cast<Elements>(1000)){
//    std::cout <<"Element3 fine!"<< std::endl;
//    }
//
//    if(Elements::Element6 ==static_cast<Elements>(1003)){
//    std::cout <<"Element6 fine!"<< std::endl;
//    }
//}
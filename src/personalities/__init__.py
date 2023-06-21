# 这些模块定义了不同个性的内容，例如不同的聊天风格、回答方式等。
from .luna import luna
from .sacha import sacha
from .angele import angele

__all__ = [
    "sacha",
    "luna",
    "angele",
    "get_personality"
]


# get_personality函数接受一个参数name，根据传入的名称返回对应的个性模块。
def get_personality(name: str):
    # 它使用了一个字典来映射名称与个性模块之间的关系。如果传入的名称不在字典中，函数将引发一个异常，指示选择的个性不存在。
    try:
        return {
            "luna": luna,
            "sacha": sacha,
            "Angèle": angele
        }[name]
    except Exception:
        raise Exception("The personality you selected does not exist!")

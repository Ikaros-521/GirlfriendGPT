from __future__ import annotations

import json
from typing import Union, Any

from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish

from prompts import FORMAT_INSTRUCTIONS


# 定义了一个名为MultiModalOutputParser的类，它是AgentOutputParser类的子类。
class MultiModalOutputParser(AgentOutputParser):
    # 用于存储对AgentOutputParser类的实例的引用
    parser: AgentOutputParser

    # 接收一个parser参数和可变的关键字参数data。
    def __init__(self, parser, **data: Any):
        # 通过调用父类AgentOutputParser的构造方法super().__init__(**data, parser=parser)进行初始化
        super().__init__(**data, parser=parser)

    # 返回一个字符串，表示格式化指令的说明。具体的格式化指令内容可以在常量·FORMAT_INSTRUCTIONS中定义。
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    # 用于解析聊天输出文本，将其转换为AgentAction或AgentFinish对象。
    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        # 首先，将输入文本去除首尾的空白字符
        cleaned_output = text.strip()

        # 检查如果文本以"AI: "开头，则将开头部分删除，只保留后面的内容。
        if cleaned_output.startswith("AI: "):
            cleaned_output = cleaned_output[len("AI: ") :]

        # 通过调用self.parser.parse(cleaned_output)方法，将清理后的文本传递给存储在parser属性中的AgentOutputParser实例进行进一步的解析。将解析结果作为方法的返回值，可以是AgentAction或AgentFinish对象。
        return self.parser.parse(cleaned_output)

    @property
    #  返回一个字符串，表示解析器的类型。在这里，它返回字符串"conversational_chat"
    def _type(self) -> str:
        return "conversational_chat"

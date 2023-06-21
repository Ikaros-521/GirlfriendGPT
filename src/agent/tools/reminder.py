"""Tool for scheduling reminders."""
import logging
from typing import Callable

from langchain.agents import Tool
from pydantic import BaseModel, Field
from pytimeparse.timeparse import timeparse


# ToolRequest继承自BaseModel，用于定义工具请求的基本模型结构。它提供了一个类方法get_json，该方法返回一个字典，包含每个属性的描述信息。
class ToolRequest(BaseModel):
    @classmethod
    def get_json(cls):
        return {
            key: info["description"] for key, info in cls.schema()["properties"].items()
        }


# ReminderRequest继承自ToolRequest，并定义了after和reminder两个属性，用于表示提醒的时间差和提醒的消息内容。这两个属性都使用Field进行描述。
class ReminderRequest(ToolRequest):
    """Provide structure for tool invocation for the LLM."""

    after: str = Field(description="time delta")
    reminder: str = Field(description="reminder message to send to the user")


# 几个示例提醒请求的实例。
EXAMPLES = [
    ReminderRequest(after="15s", reminder="turn off the lights"),
    ReminderRequest(after="60m", reminder="file your taxes"),
    ReminderRequest(after="2h5m", reminder="send a message to your wife about dinner"),
]

# 工具的名称被设置为"REMIND"，描述了工具的用途和输入输出的说明。还定义了示例的字符串表示，其中包含了示例请求的JSON格式。
NAME: str = "REMIND"

EXAMPLES_STR = "\n".join([example.json() for example in EXAMPLES])
DESCRIPTION: str = f"""Used to schedule reminders for the user at a future point in time. Input: time time delata and the reminder. Please use the following JSON format as Input:  
{ReminderRequest.get_json()}.
            
Example(s):
{EXAMPLES_STR}""".replace(
    "{", "{{"
).replace(
    "}", "}}"
)


# RemindMe继承自Tool类，并定义了invoke_later和chat_id两个属性。在初始化方法中，调用父类的构造方法来设置工具的名称、功能描述和回调函数。
class RemindMe(Tool):
    """Tool used to schedule reminders via the Steamship Task system."""

    invoke_later: Callable
    chat_id: str

    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    def __init__(self, invoke_later: Callable, chat_id: str):
        super().__init__(
            name="REMIND",
            func=self.run,
            description=DESCRIPTION,
            invoke_later=invoke_later,
            chat_id=chat_id,
        )

    # 先根据输入的prompt判断其类型，如果是字典类型，则使用ReminderRequest.parse_obj方法解析为ReminderRequest对象；
    # 如果是字符串类型，则先替换单引号为双引号，然后使用ReminderRequest.parse_raw方法解析为ReminderRequest对象。
    # 如果无法处理输入，则返回错误消息
    # 然后，调用self._schedule方法来安排提醒事项，并返回固定的输出消息。
    def run(self, prompt, **kwargs) -> str:
        """Respond to LLM prompts."""
        logging.info(f"[remind-me] prompt: {prompt}")
        if isinstance(prompt, dict):
            req = ReminderRequest.parse_obj(prompt)
        elif isinstance(prompt, str):
            prompt = prompt.replace("'", '"')
            req = ReminderRequest.parse_raw(prompt)
        else:
            return "Tool failure. Could not handle request. Sorry."

        self._schedule(req)
        return "This is the output"

    # 这个方法用于根据提醒请求安排提醒事项。首先，将时间差字符串解析为秒数，并打印日志信息，记录提醒的延迟时间和提醒消息。
    # 然后，使用self.invoke_later回调函数来安排将来的提醒事项。该函数接受延迟时间（毫秒）、提醒消息和聊天ID作为参数。
    # 最后，再次打印日志信息，记录安排的延迟时间和提醒消息，并返回固定的成功消息。
    def _schedule(self, req: ReminderRequest) -> str:
        after_seconds = timeparse(req.after)
        logging.info(f"scheduling after {after_seconds}s, message {req.reminder}")

        self.invoke_later(
            delay_ms=after_seconds * 1_000,
            message=req.reminder,
            chat_id=self.chat_id,
        )

        logging.info(f"scheduling {after_seconds * 1_000}, message {req.reminder}")

        return "Your reminder has been scheduled."

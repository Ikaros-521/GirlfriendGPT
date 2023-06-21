"""Define your LangChain chatbot."""
import re
from abc import abstractmethod
from typing import List, Optional

from langchain.agents import AgentExecutor
from langchain.tools import Tool
from steamship import Block
from steamship.experimental.package_starters.telegram_bot import TelegramBot
from steamship.experimental.transports.chat import ChatMessage
from steamship.invocable import post

from agent.utils import is_valid_uuid, make_block_public, UUID_PATTERN

# 它提供了与Telegram进行交互的功能，并使用多模态代理生成聊天回复。
# 这里定义了一个名为LangChainAgentBot的类，它是TelegramBot类的子类，继承了TelegramBot类的属性和方法。
class LangChainAgentBot(TelegramBot):
    # 使用@abstractmethod装饰器定义了一个抽象方法get_agent()。
    @abstractmethod
    def get_agent(self, chat_id: str) -> AgentExecutor:
        raise NotImplementedError()

    # 这个方法返回一个可选的Tool对象，用于处理语音相关的工具。默认情况下返回None，表示没有语音工具可用。
    def voice_tool(self) -> Optional[Tool]:
        return None

    # 这个方法返回一个布尔值，表示是否启用详细日志记录。默认情况下返回True，表示启用详细日志记录。
    def is_verbose_logging_enabled(self):
        return True

    # 使用@post装饰器将它标记为一个HTTP POST请求的处理方法。它接收一个message和chat_id参数，用于发送消息到Telegram。
    # 在方法内部，通过self.telegram_transport.send()方法发送了一条ChatMessage对象的列表，该对象包含要发送的消息内容和聊天id。最后，方法返回字符串"ok"。
    @post("send_message")
    def send_message(self, message: str, chat_id: str) -> str:
        """Send a message to Telegram.

        Note: This is a private endpoint that requires authentication."""
        self.telegram_transport.send([ChatMessage(text=message, chat_id=chat_id)])
        return "ok"

    # 用于延迟一定时间后调用send_message()方法发送消息。它接收delay_ms、message和chat_id参数，其中delay_ms表示延迟的时间（以毫秒为单位）。
    # 在方法内部，它通过调用self.invoke_later()方法来设置延迟执行的任务，将任务名称设置为"send_message"，并传递延迟时间和消息参数。
    def _invoke_later(self, delay_ms: int, message: str, chat_id: str):
        self.invoke_later(
            "send_message",
            delay_ms=delay_ms,
            arguments={
                "message": message,
                "chat_id": chat_id,
            },
        )

    # 这个方法用于根据用户输入生成聊天机器人的回复。它接收一个ChatMessage对象作为输入，并返回一个包含多个ChatMessage对象的列表作为回复。
    def create_response(
        self, incoming_message: ChatMessage
    ) -> Optional[List[ChatMessage]]:
        """Use the LLM to prepare the next response by appending the user input to the file and then generating."""
        # 首先检查如果用户输入是"/start"，则返回一条初始回复消息。
        if incoming_message.text == "/start":
            return [
                ChatMessage(
                    text="New conversation started.",
                    chat_id=incoming_message.get_chat_id(),
                )
            ]

        # 否则，它通过调用self.get_agent()方法获取聊天机器人的执行者对象
        conversation = self.get_agent(
            chat_id=incoming_message.get_chat_id(),
        )
        # 使用conversation.run()方法传入用户输入来获取机器人的回复。
        response = conversation.run(input=incoming_message.text)
        response = UUID_PATTERN.split(response)
        # 对列表中的每个元素进行处理，去掉开头的非单词字符
        response = [re.sub(r"^\W+", "", el) for el in response]
        # 如果存在语音工具（voice_tool()方法返回非None），则对每个回复进行判断
        if audio_tool := self.voice_tool():
            response_messages = []
            for message in response:
                response_messages.append(message)
                # 如果不是有效的UUID（表示文本消息），则通过语音工具将文本转换为语音，并将语音的UUID添加到回复列表中。
                if not is_valid_uuid(message):
                    audio_uuid = audio_tool.run(message)
                    response_messages.append(audio_uuid)
        else:
            response_messages = response

        # 调用self.agent_output_to_chat_messages()方法将回复转换为ChatMessage对象的列表，并返回该列表作为方法的结果。
        return self.agent_output_to_chat_messages(
            chat_id=incoming_message.get_chat_id(), agent_output=response_messages
        )

    # 这个方法用于将多模态代理的输出转换为`ChatMessage`对象的列表。多模态代理的回复可能包含一个或多个可解析的UUID（表示包含二进制数据的块）或文本。
    # 在这个方法中，对每个字符串进行检查，并根据其类型创建相应类型的`ChatMessage`对象。
    def agent_output_to_chat_messages(
        self, chat_id: str, agent_output: List[str]
    ) -> List[ChatMessage]:
        """Transform the output of the Multi-Modal Agent into a list of ChatMessage objects.

        The response of a Multi-Modal Agent contains one or more:
        - parseable UUIDs, representing a block containing binary data, or:
        - Text

        This method inspects each string and creates a ChatMessage of the appropriate type.
        """
        ret = []
        for part_response in agent_output:
            # 如果字符串是有效的UUID，则通过`Block.get()`方法获取对应的块对象，并使用`ChatMessage.from_block()`方法创建一个基于该块的`ChatMessage`对象。
            if is_valid_uuid(part_response):
                block = Block.get(self.client, _id=part_response)
                message = ChatMessage.from_block(
                    block,
                    chat_id=chat_id,
                )
                # 通过`make_block_public()`方法将块设置为公开访问，并将其URL赋值给`message.url`属性。
                message.url = make_block_public(self.client, block)

            # 如果字符串不是有效的UUID，则创建一个普通文本消息的`ChatMessage`对象。
            else:
                message = ChatMessage(
                    client=self.client,
                    chat_id=chat_id,
                    text=part_response,
                )

            # 将创建的`ChatMessage`对象添加到结果列表中，并返回该列表作为方法的结果。
            ret.append(message)
        return ret

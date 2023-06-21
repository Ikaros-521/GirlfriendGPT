"""Scaffolding to host your LangChain Chatbot on Steamship and connect it to Telegram."""
from typing import List, Optional, Type

import langchain
from langchain.agents import Tool, initialize_agent, AgentType, AgentExecutor
from langchain.memory import ConversationBufferMemory
from pydantic import Field
from steamship.experimental.package_starters.telegram_bot import (
    TelegramBot,
    TelegramBotConfig,
)
from steamship.invocable import Config
from steamship_langchain.llms import OpenAIChat
from steamship_langchain.memory import ChatMessageHistory

from agent.base import LangChainAgentBot
from agent.tools.search import SearchTool
from agent.tools.selfie import SelfieTool
from agent.tools.speech import GenerateSpeechTool
from personalities import get_personality
from prompts import SUFFIX, FORMAT_INSTRUCTIONS, PERSONALITY_PROMPT

MODEL_NAME = "gpt-4"  # or "gpt-4"
TEMPERATURE = 0.7
VERBOSE = True
PERSONALITY = "sacha"

langchain.cache = None

# 定义了一个GirlFriendAIConfig类，继承自TelegramBotConfig，用于配置GirlfriendGPT类的参数。其中包括elevenlabs_api_key和elevenlabs_voice_id，用于ElevenLabs Voice Bot的API密钥和语音ID。
class GirlFriendAIConfig(TelegramBotConfig):
    elevenlabs_api_key: str = Field(
        default="", description="Optional API KEY for ElevenLabs Voice Bot"
    )
    elevenlabs_voice_id: str = Field(
        default="", description="Optional voice_id for ElevenLabs Voice Bot"
    )


class GirlfriendGPT(LangChainAgentBot, TelegramBot):
    """Deploy LangChain chatbots and connect them to Telegram."""

    config: GirlFriendAIConfig

    # 返回配置类GirlFriendAIConfig。
    @classmethod
    def config_cls(cls) -> Type[Config]:
        """Return the Configuration class."""
        return GirlFriendAIConfig

    # 根据给定的chat_id获取一个AgentExecutor对象。
    def get_agent(self, chat_id: str) -> AgentExecutor:
        # 创建一个OpenAIChat对象llm，使用指定的模型名称、温度和详细参数进行初始化。
        llm = OpenAIChat(
            client=self.client,
            model_name=MODEL_NAME,
            temperature=TEMPERATURE,
            verbose=VERBOSE,
        )

        # 然后通过self.get_tools(chat_id)获取工具列表。
        tools = self.get_tools(chat_id=chat_id)

        # 接下来，通过self.get_memory(chat_id)获取内存对象。
        memory = self.get_memory(chat_id)

        # 最后，调用initialize_agent方法初始化一个代理对象，并将工具、llm、内存和其他参数传递给该方法。
        return initialize_agent(
            tools,
            llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            agent_kwargs={
                # "output_parser": MultiModalOutputParser(ConvoOutputParser()),
                "prefix": PERSONALITY_PROMPT.format(personality=get_personality(PERSONALITY)),
                "suffix": SUFFIX,
                "format_instructions": FORMAT_INSTRUCTIONS,
            },
            verbose=VERBOSE,
            memory=memory,
        )

    # 返回一个工具对象，用于生成输出文本的语音版本。在这里，返回一个GenerateSpeechTool对象，使用指定的Steamship客户端、语音ID和Elevenlabs的API密钥进行初始化。
    def voice_tool(self) -> Optional[Tool]:
        """Return tool to generate spoken version of output text."""
        return GenerateSpeechTool(
            client=self.client,
            voice_id=self.config.elevenlabs_voice_id,
            elevenlabs_api_key=self.config.elevenlabs_api_key,
        )

    # 根据给定的chat_id返回一个内存对象。在这里，创建一个ConversationBufferMemory对象，使用ChatMessageHistory作为聊天历史记录，并返回内存对象。
    def get_memory(self, chat_id):
        if self.context and self.context.invocable_instance_handle:
            my_instance_handle = self.context.invocable_instance_handle
        else:
            my_instance_handle = "local-instance-handle"
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            chat_memory=ChatMessageHistory(
                client=self.client, key=f"history-{chat_id}-{my_instance_handle}"
            ),
            return_messages=True,
        )
        return memory

    # 返回一个工具列表。在这里，返回一个包含SearchTool和SelfieTool的工具列表。
    def get_tools(self, chat_id: str) -> List[Tool]:
        return [
            SearchTool(self.client),
            # MyTool(self.client),
            # GenerateImageTool(self.client),
            # GenerateAlbumArtTool(self.client)
            # RemindMe(invoke_later=self.invoke_later, chat_id=chat_id),
            SelfieTool(self.client),
        ]

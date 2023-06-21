"""Tool for generating speech."""
import json
import logging
from typing import Optional

from langchain.agents import Tool
from langchain.tools import BaseTool
from steamship import Steamship
from steamship.base.error import SteamshipError

NAME = "GenerateSpokenAudio"

DESCRIPTION = (
    "Used to generate spoken audio from text prompts. Only use if the user has asked directly for a "
    "an audio version of output. When using this tool, the input should be a plain text string containing the "
    "content to be spoken."
)

PLUGIN_HANDLE = "elevenlabs"


class GenerateSpeechTool(Tool):
    """Tool used to generate images from a text-prompt."""

    client: Steamship
    voice_id: Optional[
        str
    ] = "21m00Tcm4TlvDq8ikWAM"  # Voice ID to use. Defaults to Rachel
    elevenlabs_api_key: Optional[str] = ""  # API key to use for Elevenlabs.
    name: Optional[str] = NAME
    description: Optional[str] = DESCRIPTION

    # 类的构造函数，接受Steamship客户端对象、语音ID和Elevenlabs的API密钥作为参数，并调用父类Tool的构造函数来初始化工具的名称、描述和函数。
    def __init__(
        self,
        client: Steamship,
        voice_id: Optional[str] = "21m00Tcm4TlvDq8ikWAM",
        elevenlabs_api_key: Optional[str] = "",
    ):
        super().__init__(
            name=NAME,
            func=self.run,
            description=DESCRIPTION,
            client=client,
            voice_id=voice_id,
            elevenlabs_api_key=elevenlabs_api_key,
        )

    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    # 实现了父类Tool中的run方法，用于处理LLM提示。
    def run(self, prompt: str, **kwargs) -> str:
        """Respond to LLM prompt."""
        logging.info(f"[{self.name}] {prompt}")
        # 首先创建了一个elevenlabs插件的实例voice_generator，使用客户端对象和配置参数进行初始化。
        voice_generator = self.client.use_plugin(
            plugin_handle=PLUGIN_HANDLE,
            config={
                "voice_id": self.voice_id,
                "elevenlabs_api_key": self.elevenlabs_api_key,
            },
        )

        # 将输入的提示转换为字符串形式
        if not isinstance(prompt, str):
            prompt = json.dumps(prompt)

        # 调用voice_generator的generate方法，传入转换后的提示作为文本输入，并设置append_output_to_file参数为True，以便将输出附加到文件中。
        task = voice_generator.generate(text=prompt, append_output_to_file=True)
        task.wait()
        # 并获取输出的blocks列表。
        blocks = task.output.blocks
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        # 如果blocks列表不为空，则返回第一个块的UUID作为生成的音频的标识符。
        if len(blocks) > 0:
            logging.info(f"[{self.name}] audio size: {len(blocks[0].raw())}")
            return blocks[0].id
        # 如果无法生成音频，则抛出SteamshipError异常。
        raise SteamshipError(f"[{self.name}] Tool unable to generate audio!")

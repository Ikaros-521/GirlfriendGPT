"""Tool for generating images."""
import json
import logging

from langchain.agents import Tool
from steamship import Steamship
from steamship.base.error import SteamshipError
from steamship.data.plugin.plugin_instance import PluginInstance

NAME = "GenerateImage"

DESCRIPTION = """
Useful for when you need to generate an image. 
Input: A detailed dall-e prompt describing an image 
Output: the UUID of a generated image
"""

PLUGIN_HANDLE = "stable-diffusion"


# GenerateImageTool类继承自Tool类。它包含了一个client属性，表示Steamship客户端。
class GenerateImageTool(Tool):
    """Tool used to generate images from a text-prompt."""

    client: Steamship

    # 构造函数__init__接收一个client参数，并通过调用父类的构造函数来初始化工具的名称、运行函数和描述。同时，将传入的client作为属性赋值给client。
    def __init__(self, client: Steamship):
        super().__init__(
            name=NAME, func=self.run, description=DESCRIPTION, client=client
        )

    # 是否只接受单个输入
    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    # 响应LLM提示并生成图像
    def run(self, prompt: str, **kwargs) -> str:
        """Respond to LLM prompt."""

        # 使用client.use_plugin方法创建了一个与DALL-E插件的实例image_generator。通过指定插件句柄PLUGIN_HANDLE和配置参数config来初始化插件实例。在这里，配置参数设置生成单个图像，尺寸为768x768。
        # Use the Steamship DALL-E plugin.
        image_generator = self.client.use_plugin(
            plugin_handle=PLUGIN_HANDLE, config={"n": 1, "size": "768x768"}
        )

        logging.info(f"[{self.name}] {prompt}")
        # 检查输入提示的类型，如果不是字符串，则将其转换为JSON格式的字符串。
        if not isinstance(prompt, str):
            prompt = json.dumps(prompt)

        # 调用image_generator.generate方法执行图像生成任务，传入输入提示作为文本参数，并设置append_output_to_file=True以将生成的图像结果附加到文件中。最后，使用task.wait()等待任务完成。
        task = image_generator.generate(text=prompt, append_output_to_file=True)
        task.wait()
        # 获取任务的输出结果blocks，这是生成的图像数据块的列表。
        blocks = task.output.blocks
        # 记录日志以显示返回的数据块数量和图像大小。
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        # 如果存在至少一个数据块，则返回第一个数据块的UUID作为生成的图像的结果。否则，抛出SteamshipError异常表示工具无法生成图像。
        if len(blocks) > 0:
            logging.info(f"[{self.name}] image size: {len(blocks[0].raw())}")
            return blocks[0].id
        raise SteamshipError(f"[{self.name}] Tool unable to generate image!")

"""Tool for generating album art.

The purpose of this tool is to illustrate how to wrap the GenerateImageTool
with a custom tool description & some prompt engineering to steer the image
one way or another.

The GenerateImageTool leaves the user + LLM in complete control of the image
generation prompt... but what if you wanted to make sure the prompt was:

- A particular style?
- A particular mood?
- Something else entirely, involving web scraping and other operations?

You can do that by wrapping the GenerateImageTool, as you see here, and then
sending in your own custom prompt.
"""
import json
import logging

from langchain.agents import Tool
from steamship import Steamship
from steamship.base.error import SteamshipError
from steamship.data.plugin.plugin_instance import PluginInstance
from .image import GenerateImageTool

NAME = "GenerateAlbumArt"

DESCRIPTION = """
Useful for when you need to generate album art. 
Input: A description of the album that needs art
Output: the UUID of a generated image
"""


# GenerateAlbumArtTool类继承自Tool类。它包含了一个client属性和一个tool属性，分别表示Steamship客户端和用于生成图像的GenerateImageTool工具。
class GenerateAlbumArtTool(Tool):
    """Tool used to generate album art from a album description."""

    client: Steamship
    tool: GenerateImageTool

    # 构造函数__init__接收一个client参数，并通过调用父类的构造函数来初始化工具的名称、运行函数和描述。同时，将传入的client和GenerateImageTool(client)作为属性赋值给client和tool。
    def __init__(self, client: Steamship):
        super().__init__(
            name=NAME,
            func=self.run,
            description=DESCRIPTION,
            client=client,
            tool=GenerateImageTool(client),
        )

    # 这个属性指示工具是否只接受单个输入。在这种情况下，返回True。
    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    # 响应LLM提示词并生成图片。
    def run(self, prompt: str, **kwargs) -> str:
        """Respond to LLM prompt."""

        # 根据传入的prompt创建一个新的提示image_gen_prompt，该提示基于提供给工具的原始提示，并包含了额外的术语，如"album art"、"4k"、"high def"、"pop art"等。这样可以确保生成的图像与专辑封面相关。
        # Here we create a NEW prompt, which is based on the prompt provided
        # to this tool, but including extra terms.
        image_gen_prompt = f"album art, 4k, high def, pop art, professional, high quality, award winning, grammy, platinum, {prompt}"

        # 使用self.tool.run(image_gen_prompt)调用内部的GenerateImageTool工具的run方法来生成图像。
        # GenerateImageTool是用于生成图像的具体工具类。通过传入新创建的提示image_gen_prompt，将生成的图像的UUID作为结果返回。
        # Then we just return the results of the wrapped GenerateImageTool,
        # passing it the new prompt that we created.
        return self.tool.run(image_gen_prompt)

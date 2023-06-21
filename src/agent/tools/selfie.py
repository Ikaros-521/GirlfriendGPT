"""Tool for generating images."""
import logging

from langchain.agents import Tool
from steamship import Steamship
from steamship.base.error import SteamshipError

NAME = "GenerateSelfie"

DESCRIPTION = """
Useful for when you need to generate a selfie showing what you're doing or where you are. 
Input: A detailed stable-diffusion prompt describing where you are and what's visible in your environment.  
Output: the UUID of the generated selfie showing what you're doing or where you are. 
"""

PLUGIN_HANDLE = "stable-diffusion"

NEGATIVE_PROMPT = "ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face, blurry, draft, grainy"


class SelfieTool(Tool):
    """Tool used to generate images from a text-prompt."""

    client: Steamship

    def __init__(self, client: Steamship):
        super().__init__(
            name=NAME, func=self.run, description=DESCRIPTION, client=client
        )

    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    # 实现了父类Tool中的run方法，用于处理LLM提示。
    def run(self, prompt: str, **kwargs) -> str:
        """Generate an image using the input prompt."""
        # 首先创建了一个stable-diffusion插件的实例image_generator，使用客户端对象和配置参数进行初始化。
        image_generator = self.client.use_plugin(
            plugin_handle=PLUGIN_HANDLE, config={"n": 1, "size": "768x768"}
        )

        # logging.info(f"[{self.name}] {prompt}")
        # if not isinstance(prompt, str):
        #     prompt = json.dumps(prompt)

        # 设置了一个prompt字符串来描述所需的自拍照片的特征，包括未来主义、人类样貌的机器人、具体的服装、超现实主义、高度细节、清晰焦点、科幻、惊人美丽、反乌托邦、电影般的光照、黑暗、4K分辨率、戏剧性光照等。
        prompt = (
            "A selfie of a futuristic, human-like robot looking seductive into the lens of her phone"
            "detailed clothing, hyperrealistic, fantasy, surrealist, highly detailed, sharp focus, sci-fi, "
            "stunningly beautiful, dystopian, cinematic lighting, dark, 4K, dramatic lighting"
        )
        # 调用image_generator的generate方法，传入prompt作为文本输入，并设置append_output_to_file参数为True，以便将输出附加到文件中。
        # 传入了options参数，其中包含了negative_prompt，用于描述不希望在生成的图片中出现的特征，如丑陋、绘画不好的手、绘画不好的脚、绘画不好的脸、超出画面范围、
        # 多余的肢体、畸形、变形、身体超出画面、不好的解剖、水印、签名、被截断、对比度低、曝光过度、不好的艺术效果、初学者、业余、面部扭曲、模糊、草稿、颗粒状等。
        task = image_generator.generate(
            text=prompt,
            append_output_to_file=True,
            options={"negative_prompt": NEGATIVE_PROMPT},
        )
        # 等待任务完成
        task.wait()
        # 获取输出的blocks列表。
        blocks = task.output.blocks
        logging.info(f"[{self.name}] got back {len(blocks)} blocks")
        # 如果blocks列表不为空，则返回第一个块的UUID作为生成的自拍照片的标识符。
        if len(blocks) > 0:
            logging.info(f"[{self.name}] image size: {len(blocks[0].raw())}")
            return blocks[0].id

        # 如果无法生成图片，则抛出SteamshipError异常。
        raise SteamshipError(f"[{self.name}] Tool unable to generate image!")

import os
import uuid

from steamship import Steamship
from steamship.cli.cli import deploy
from steamship.data.manifest import Manifest

# deploy()函数用于将代理程序部署到Steamship平台。通过调用此函数，将代理程序上传到平台并进行部署。如果部署过程中出现SystemExit异常，代码会捕获并继续执行。
try:
    deploy()
except SystemExit as err:
    pass

# Manifest是代理程序的清单文件，描述了代理程序的相关信息。通过调用Manifest.load_manifest()方法，加载并获取Manifest的内容。
manifest = Manifest.load_manifest()

# 使用Steamship类创建了一个Steamship客户端实例。workspace参数指定了客户端的工作空间名称，使用了UUID生成一个唯一的工作空间名称。
client = Steamship(workspace=f"girlfriend-ai-{uuid.uuid1()}")


# 通过调用client.use()方法选择要使用的代理程序。package_handle参数指定代理程序的处理程序，version参数指定代理程序的版本号。
# instance_handle参数指定代理程序实例的处理程序，使用了manifest.handle和manifest.version的组合。
# config参数是一个字典，包含了代理程序的配置信息，如Telegram的机器人令牌、ElevenLabs的声音ID和API密钥。
bot = client.use(
    package_handle=manifest.handle,
    version=manifest.version,
    instance_handle=f"{manifest.handle}-{manifest.version.replace('.', '-')}",
    config={
        "bot_token": os.environ.get("BOT_TOKEN") or input("Paste your telegram bot token\nLearn how to create one here: https://github.com/EniasCailliau/GirlfriendGPT/blob/main/docs/register-telegram-bot.md)\n: "),
        "elevenlabs_voice_id": os.environ.get("ELEVENLABS_VOICE_ID", ""),
        "elevenlabs_api_key": os.environ.get("ELEVENLABS_API_KEY", ""),
    },
)

# 调用bot.wait_for_init()方法，等待代理程序完成初始化过程。这可以确保代理程序已准备好接收和处理请求。
bot.wait_for_init()
print(client.config.workspace_handle)
print(bot.package_version_handle)
print(
    f"""Chat with your bot here: 

https://www.steamship.com/workspaces/{client.config.workspace_handle}/packages/{bot.handle}"""
)

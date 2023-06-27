import logging
import os
import sys

sys.path.insert(0, "src")
from functools import partial
from typing import List

from steamship.experimental.transports.chat import ChatMessage
from steamship import Steamship, SteamshipError
from steamship.cli.ship_spinner import ship_spinner
from termcolor import colored
from api import GirlfriendGPT


# 这个函数接受一个response_messages参数（类型为List[ChatMessage]），并打印结果。它遍历response_messages列表中的每个消息对象，如果消息对象包含mime_type属性，则打印其URL；否则，打印消息的文本内容。
def show_results(response_messages: List[ChatMessage]):
    print(colored("\nResults: ", "blue", attrs=["bold"]))
    for message in response_messages:
        if message.mime_type:
            print(message.url, end="\n\n")
        else:
            print(message.text, end="\n\n")


# 这是一个上下文管理器（Context Manager），用于在特定的代码块中禁用日志记录。在__enter__方法中，它禁用了所有日志记录；在__exit__方法中，它恢复了日志记录的设置。
class LoggingDisabled:
    """Context manager that turns off logging within context."""

    def __enter__(self):
        logging.disable(logging.CRITICAL)

    def __exit__(self, exit_type, exit_value, exit_traceback):
        logging.disable(logging.NOTSET)


def main():
    # 首先创建了一个Steamship实例。
    Steamship()

    # 然后，使用Steamship.temporary_workspace()上下文管理器创建了一个临时的Steamship客户端实例，并通过partial函数创建了一个部分应用的run函数。
    with Steamship.temporary_workspace() as client:
        run = partial(
            run_agent,
            agent=GirlfriendGPT(
                client=client,
                config={
                    "bot_token": "test",
                    "elevenlabs_voice_id": os.environ.get("ELEVENLABS_VOICE_ID"),
                    "elevenlabs_api_key": os.environ.get("ELEVENLABS_API_KEY"),
                },
            ),
        )
        print(f"Starting Agent...")

        print(
            f"If you make code changes, you will need to restart this client. Press CTRL+C to exit at any time.\n"
        )

        count = 1

        # 接下来，进入一个无限循环，循环体内获取用户输入的提示信息，并调用run函数来处理该提示。循环执行的次数通过计数器count来记录。
        while True:
            print(f"----- Agent Run {count} -----")
            prompt = input(colored(f"Prompt: ", "blue"))
            run(
                # client,
                prompt=prompt,
            )
            count += 1


# 这个函数是用来运行代理程序的。它接受一个代理对象agent、一个提示字符串prompt和一个布尔值as_api（默认为False）。
# 在函数内部，根据agent的设置，输出一些调试信息。然后，调用agent.create_response方法来生成回复，并调用show_results函数来显示回复结果。
def run_agent(agent, prompt: str, as_api: bool = False) -> None:
    # For Debugging
    if not agent.is_verbose_logging_enabled():  # display progress when verbose is False
        print("Running: ", end="")
        with ship_spinner():
            response = agent.create_response(
                incoming_message=ChatMessage(text=prompt, chat_id="123")
            )
    else:
        response = agent.create_response(
            incoming_message=ChatMessage(text=prompt, chat_id="123")
        )

    show_results(response)


# 代码的最后部分使用__name__ == "__main__"条件来检查脚本是否被直接运行。如果是直接运行，它会禁用Python的日志记录，然后调用main函数。如果在执行过程中遇到SteamshipError异常，它会捕获该异常并打印错误信息。
if __name__ == "__main__":
    # when running locally, we can use print statements to capture logs / info.
    # as a result, we will disable python logging to run. this will keep the output cleaner.
    with LoggingDisabled():
        try:
            main()
        except SteamshipError as e:
            print(colored("Aborting! ", "red"), end="")
            print(f"There was an error encountered when running: {e}")

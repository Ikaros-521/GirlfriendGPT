"""Tool for searching the web."""

from langchain.agents import Tool
from steamship import Steamship
from steamship_langchain.tools import SteamshipSERP

NAME = "Search"

DESCRIPTION = """
Useful for when you need to answer questions about current events
"""


class SearchTool(Tool):
    """Tool used to search for information using SERP API."""

    # 用于与Steamship服务进行通信的客户端对象
    client: Steamship

    def __init__(self, client: Steamship):
        super().__init__(
            name=NAME, func=self.run, description=DESCRIPTION, client=client
        )

    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    # 实现了父类Tool中的run方法，用于处理LLM提示。在这个方法中，首先创建了一个SteamshipSERP对象，传入了客户端对象。然后调用search方法，将提示作为参数进行搜索，并返回搜索结果。
    def run(self, prompt: str, **kwargs) -> str:
        """Respond to LLM prompts."""
        search = SteamshipSERP(client=self.client)
        return search.search(prompt)


if __name__ == "__main__":
    # 使用Steamship.temporary_workspace()创建了一个临时的Steamship工作空间，并将其作为参数实例化了SearchTool对象。然后调用了run方法，将"What's the weather today?"作为提示进行搜索，并将结果打印输出。
    with Steamship.temporary_workspace() as client:
        my_tool = SearchTool(client)
        result = my_tool.run("What's the weather today?")
        print(result)

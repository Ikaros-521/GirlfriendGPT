"""Use this file to create your own tool."""
import logging

from langchain import LLMChain, PromptTemplate
from langchain.agents import Tool
from steamship import Steamship
from steamship_langchain.llms.openai import OpenAI

NAME = "MyTool"

DESCRIPTION = """
Useful for when you need to come up with todo lists. 
Input: an objective to create a todo list for. 
Output: a todo list for that objective. Please be very clear what the objective is!
"""

# 这个提示模板是用于向语言模型提供生成待办事项列表的任务描述。其中的{objective}是一个占位符，将在实际生成任务时替换为具体的目标描述。
PROMPT = """
You are a planner who is an expert at coming up with a todo list for a given objective. 
Come up with a todo list for this objective: {objective}"
"""


# MyTool继承自Tool类，并定义了一个client属性。在初始化方法中，调用父类的构造方法来设置工具的名称、功能描述和客户端。
class MyTool(Tool):
    """Tool used to manage to-do lists."""

    client: Steamship

    def __init__(self, client: Steamship):
        super().__init__(
            name=NAME, func=self.run, description=DESCRIPTION, client=client
        )

    # 创建一个LLMChain实例，该实例将使用OpenAI语言模型进行语言生成任务。
    def _get_chain(self, client):
        # 方法首先基于定义的提示模板PROMPT创建一个PromptTemplate对象todo_prompt
        todo_prompt = PromptTemplate.from_template(PROMPT)
        # 然后使用客户端和提示模板来初始化LLMChain实例，并将其返回。
        return LLMChain(llm=OpenAI(client=client, temperature=0), prompt=todo_prompt)

    @property
    def is_single_input(self) -> bool:
        """Whether the tool only accepts a single input."""
        return True

    def run(self, prompt: str, **kwargs) -> str:
        """Respond to LLM prompts."""
        # 通过调用_get_chain方法获取LLMChain实例chain。
        chain = self._get_chain(self.client)
        # 使用输入的目标描述作为参数调用chain.predict方法来生成待办事项列表。最后，将生成的列表作为字符串结果返回。
        return chain.predict(objective=prompt)

# PERSONALITY_PROMPT是一个格式化字符串，用于向用户展示聊天机器人的个性特点和可用的工具列表。其中的{personality}占位符将被替换为具体的个性描述。示例中的格式为：
PERSONALITY_PROMPT = """{personality}

TOOLS:
------

You have access to the following tools:

"""

# FORMAT_INSTRUCTIONS是一个格式化字符串，提供了使用工具的指导说明。它描述了如何使用工具以及使用工具时应遵循的格式。示例中的格式为：
# 其中，`Thought`表示用户思考的问题或判断，`Action`表示要执行的操作，应该是工具列表中的一个选项，`Action Input`表示操作的输入，`Observation`表示操作的结果。
# 同时，如果用户没有使用工具或者已经得到了最终的回答，需要使用特定的格式。在最终的回答中，需要包含生成图像的UUID。
FORMAT_INSTRUCTIONS = """To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a final response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
{ai_prefix}: [your final response here which ALWAYS includes UUID of generated images]

Make sure to use all observations to come up with your final response. 
ALWAYS copy the UUID of images into your final response!
ALWAYS come up with a final response after generating an image and make sure to include the UUID of that image.
```"""

# `SUFFIX`是一个格式化字符串，用于在每个对话的结尾添加一些附加信息。它显示了之前的对话历史记录、新的输入内容以及代理的工作区信息。示例中的格式为：
# 其中，`{chat_history}`将被替换为之前对话的历史记录，`{input}`将被替换为新的输入内容，`{agent_scratchpad}`将被替换为代理的工作区信息。
# 这些常量和格式化字符串在代码中用于构建对话和用户界面，提供了一致的交互体验和指导。
SUFFIX = """Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}"""

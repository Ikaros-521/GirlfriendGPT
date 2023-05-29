# GirlfriendGPT - Your personal AI companion

Welcome to the GirlfriendGPT repository. This is a starter project to help you build your personalized AI companion with a unique personality, voice, and even SELFIES!

## Demo
Click the image below for a demo:

[![Demo Video](http://img.youtube.com/vi/LiN3D1QZGQw/0.jpg)](http://www.youtube.com/watch?v=LiN3D1QZGQw "Video Title")

## Subscribe to updates here: https://twitter.com/eniascailliau

## Features

* Custom Voice: Utilize EleventLabs to create a unique voice for your AI model.
* Connected to Telegram: Directly send and receive messages from your AI companion via Telegram.
* Personality: Customize the AI's personality according to your preferences.
* Selfies: AI is capable of generating SELFIES when asked.

## Getting started 

安装环境，启动main.py可以测试steamship的功能。To run your companion locally:
```
pip install -r requirements.txt
python main.py 
```

To deploy your companion & connect it to Telegram:
运行后会提示相关的配置，需要注意的是handle的配置需要是steamship没被使用过的一个字符串，可以自行编造。跑完后就直接和你的bot关联了，没项目啥事了，给力。  
```
python deploy.py 
```

You will need to fetch a Telegram key to connect your companion to Telegram. [This guide](/docs/register-telegram-bot.md) will show you how.

需要注意的是，如果你第一次配置handle失败后，配置会写入本地的`steamship.json`配置文件，你可以手动修改配置文件。  

## Roadmap
* Memories: Soon, the AI will have the capability to remember past interactions, improving conversational context and depth.
* Photorealistic selfies

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

<details>
  <summary>👀 Add a personality!</summary>
  <br>
Do you have a unique personality in mind for our AI model, GirlfriendGPT? Great! Here's a step-by-step guide on how to add it.

## Step 1: 定义你的个性 / Define Your Personality
首先，你需要定义你的个性。这是通过在“src/personalities”目录中创建一个新的Python文件来完成的。
First, you'll need to define your personality. This is done by creating a new Python file in the `src/personalities` directory.

例如，如果你的个性被命名为"lucas"，你会创建一个名为"lucas.py"的文件。在这个文件中，你会定义体现"lucas"的特征和行为。这可能包括她的说话风格、对某些输入的反应，或者你设想的任何其他定义特征。  
For example, if your personality is named "lucas", you would create a file called `lucas.py`. Inside this file, you would define the characteristics and behaviors that embody "lucas". This could include her speaking style, responses to certain inputs, or any other defining features you envision.


## Step 2: Update __init__.py
Once you've created and fleshed out your personality file, it's time to make our codebase aware of it. Open __init__.py in the `src/personalities` directory.

Import your new personality at the top of the file and add your personality to the __all__ list:


```python
from .luna import luna
from .sacha import sacha
from .lucas import lucas  # 导入你的人格文件 This is your new personality

__all__ = [
    "sacha",
    "luna",
    "lucas",  # 添加你的人格名 Add your personality here
    "get_personality"
]
```

最后，将您的个性添加到get_personality()函数中：
Lastly, add your personality to the get_personality() function:

```python
def get_personality(name: str):
    try:
        return {
            "luna": luna,
            "sacha": sacha,
            "lucas": lucas  #  添加你的人格名 Add your personality here
        }[name]
    except Exception:
        raise Exception("The personality you selected does not exist!")
```

And that's it! Now, whenever the `get_personality` function is called with the name of your personality, it will return the behaviors and characteristics defined in your personality file.

修改`api.py`的PERSONALITY为你get_personality()函数中设置的name字符串。  
```
PERSONALITY = "lucas"
```
  
## Step 3: Test and Submit

最后，老规矩deploy.py提交代码，即可。  
  
Before you submit your new personality, please test it to ensure everything works as expected. If all is well, submit a Pull Request with your changes, and be sure to include the title "{name} - {description}" where {name} is your personality's name, and {description} is a brief explanation of the personality.

Good luck, and we can't wait to meet your new GirlfriendGPT personality!
</details>





## License
This project is licensed under the MIT License. 

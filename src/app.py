import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Final

import discord
import requests
from discord import app_commands
from openai import OpenAI, BadRequestError


# 定数クラス
class Constants:
    # AI が回答中のメッセージ
    answering_message: Final[str] = "回答中です..."

    # Github Issue 作成のエンドポイント
    create_issue_url: Final[str] = "https://api.github.com/repos/telneko/TelGPT-DiscordBot/issues"


# OpenAI ChatGPT の Chat モデルデータ
class ChatGPTChatModel(Enum):
    GPT_4_O = "gpt-4o"
    GPT_4_O_MINI = "gpt-4o-mini"
    GPT_O1_PREVIEW = "o1-preview"


# OpenAI ChatGPT の DALL-E モデルデータ
class ChatGPTDALLEModel(Enum):
    DALL_E_3 = "dall-e-3"


@dataclass
class Message:
    role: str
    content: str


@dataclass
class BotConfig:
    discord_assistant_name: str
    discord_token: str
    openai_api_key: str
    deepl_api_key: str
    chat_model: ChatGPTChatModel
    dalle_model: ChatGPTDALLEModel

    def __init__(self):
        self.discord_assistant_name = 'TelGPT'
        self.discord_token = os.getenv("TEL_GPT_DISCORD_TOKEN")
        self.openai_api_key = os.getenv("TEL_GPT_OPEN_AI_TOKEN")
        self.deepl_api_key = os.getenv("TEL_GPT_DEEPL_TOKEN")
        self.chat_model = ChatGPTChatModel.GPT_O1_PREVIEW
        self.dalle_model = ChatGPTDALLEModel.DALL_E_3


@dataclass
class CachedError:
    message: str
    translated_message: str


botConfig: Final[BotConfig] = BotConfig()

openAIClient: Final[OpenAI] = OpenAI(api_key=botConfig.openai_api_key)

discordIntents = discord.Intents.default()
discordIntents.message_content = True
discordClient: Final[discord.Client] = discord.Client(intents=discordIntents)
discordCommand: Final[app_commands.CommandTree] = app_commands.CommandTree(discordClient)


def create_issue(author: str, title: str, message: str) -> dict:
    try:
        data = {
            "title": f"{title} by {author}",
            "body": message
        }
        response = requests.post(
            Constants.create_issue_url,
            headers={
                'Authorization': f'token {os.getenv("GITHUB_ISSUE_PAT")} ',
                'Content-Type': 'application/json',
            },
            data=json.dumps(data)
        )
        return {
            "response": response.json()['html_url']
        }
    except Exception as e:
        return {
            "error": {
                "code": 1,
                "message": f"Unknown Error {e}"
            }
        }


# OpenAIのエラーハンドリング. エラーコードによってメッセージを変更
def handle_bad_request_error(e: BadRequestError):
    if e.code == "content_policy_violation":
        message = "コンテンツポリシー違反です. 他の質問をしてください."
    else:
        message = "エラーが発生しました. Error Code: " + e.code

    return {
        "error": {
            "code": e.code,
            "message": message
        }
    }


# 英語をDeepLで日本語に翻訳
def translate_text(text: str) -> str:
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": botConfig.deepl_api_key,
        "text": text,
        "source_lang": "EN",
        "target_lang": "JA",
    }
    response = requests.post(url, data=params)
    result = response.json()
    return result['translations'][0]['text']


# noinspection PyBroadException
def query_gpt_conversation(model: ChatGPTChatModel, prompts: list[Message]) -> dict:
    try:
        messages = []
        for message in prompts:
            messages.append(
                {
                    "role": message.role,
                    "content": message.content,
                }
            )
        # noinspection PyTypeChecker
        response = openAIClient.chat.completions.create(
            model=model.value,
            messages=messages,
        )
        return {
            "response": response.choices[0].message.content.strip()
        }
    except BadRequestError as e:
        return handle_bad_request_error(e)
    except Exception as e:
        return {
            "error": {
                "code": 1,
                "message": f"Unknown Error {e}"
            }
        }


# noinspection PyBroadException
def query_gpt_chat(model: ChatGPTChatModel, prompt: str, system_setting: str) -> dict:
    try:
        response = openAIClient.chat.completions.create(
            model=model.value,
            messages=[
                {
                    "role": "system",
                    "content": system_setting,
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        return {
            "response": response.choices[0].message.content.strip()
        }
    except BadRequestError as e:
        return handle_bad_request_error(e)
    except Exception as e:
        return {
            "error": {
                "code": 1,
                "message": f"Unknown Error {e}"
            }
        }


# noinspection PyBroadException
def query_gpt_image(model: ChatGPTDALLEModel, prompt: str) -> dict:
    try:
        response = openAIClient.images.generate(
            model=model.value,
            prompt=prompt,
            response_format="url"
        )
        return {
            "response": {
                "url": response.data[0].url,
                "prompt": response.data[0].revised_prompt
            }
        }
    except BadRequestError as e:
        return handle_bad_request_error(e)
    except Exception as e:
        return {
            "error": {
                "code": 1,
                "message": f"Unknown Error {e}"
            }
        }


async def send_message_async(interaction: discord.Interaction, message: str):
    # message が 2000 文字以上だったら 1800 文字ごとに分割して送信
    if len(message) > 2000:
        is_first = True
        for i in range(0, len(message), 1800):
            if is_first:
                await interaction.followup.send(content=message[i:i + 1800])
                is_first = False
            else:
                await interaction.channel.send(content=message[i:i + 1800])
    else:
        await interaction.followup.send(content=message)


@discordClient.event
async def on_ready():
    await discordCommand.sync()


# TelGPTがオーナーのスレッド内でのメッセージ受信は会話となる
async def on_receive_message_in_bot_thread(message: discord.Message):
    channel = message.channel
    # スレッドの中でTelGPTがオーナーの場合は会話セッション

    # 直前のメッセージが回答中のメッセージだったら質問できない
    async for channelMessage in channel.history(limit=1):
        if channelMessage.author == discordClient.user and channelMessage.content == Constants.answering_message:
            await channel.send("回答中は質問できません。しばらくお待ちください。")
            return

    temporary_message = await channel.send(Constants.answering_message)

    # スレッド内のメッセージを取得
    prompts = []
    async for channelMessage in channel.history(limit=10):
        if channelMessage.author == discordClient.user:
            prompts.append(Message(role="assistant", content=channelMessage.content))
        else:
            prompts.append(Message(role="user", content=channelMessage.content))
    prompts.reverse()

    # スレッド内のメッセージを使ってAIに質問
    result = query_gpt_conversation(botConfig.chat_model, prompts=prompts)
    if "error" in result:
        await temporary_message.edit(content=f"{result['error']['message']}")
    else:
        await temporary_message.edit(content=result['response'])
    return


# TelBOTへのメンションを受け取った場合の処理
async def on_receive_mention_from_user(message: discord.Message):
    channel = message.channel
    if message.content.startswith("画像を加工して") or message.content.startswith("画像を再生成して"):
        # 直前のメッセージが回答中のメッセージだったら質問できない
        async for channelMessage in channel.history(limit=1):
            if channelMessage.author == discordClient.user and channelMessage.content == Constants.answering_message:
                await channel.send("回答中は質問できません。しばらくお待ちください。")
                return

        temporary_message = await channel.send(Constants.answering_message)

        if len(message.attachments) == 0:
            await temporary_message.edit(content="画像が添付されていません")
            return
        attachment = message.attachments[0]
        if attachment.content_type != "image/png" and attachment.content_type != "image/jpeg":
            await temporary_message.edit(content="画像の形式が正しくありません")
            return
        save_file_path = "image.png"
        try:
            download_image(attachment.url, save_file_path)
        except Exception as e:
            await temporary_message.edit(content=str(e))
            return
        response = openAIClient.images.create_variation(
            model=BotConfig.dalle_model.value,
            image=open(save_file_path, "rb"),
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        embed = discord.Embed()
        embed.set_image(url=image_url)
        await temporary_message.edit(content="投稿された画像を元に再生成しました", embed=embed)
        return  # 画像再生成の処理が終わったので終了


def generate_revise_image_prompt(old_prompts: list[str], new_prompt: str) -> str:
    first_prompt = old_prompts[0]
    if len(old_prompts) == 1 or len(old_prompts) == 2:
        return f"""
        Initially, the image was requested with the theme "{first_prompt}". 
        Now, we would like to update and refine this concept with a new request: "{new_prompt}". 
        Please regenerate the image incorporating these insights.
        """
    else:
        revised_prompts = old_prompts[2:]
        revised_prompts.reverse()
        revised_worlds = f"\",\"".join(revised_prompts)
        revised_worlds = f"\"{revised_worlds}\""
        return f"""
        First request: "{first_prompt}".
        revised requests ordered by time: {revised_worlds}.
        Latest revise request: "{new_prompt}".
        """


@discordClient.event
async def on_message(message: discord.Message):
    if message.author == discordClient.user:
        return
    channel = message.channel

    is_in_thread = (channel.type == discord.ChannelType.private_thread
                    or channel.type == discord.ChannelType.public_thread)
    to_bot_mention = len(message.mentions) == 1 and message.mentions.__contains__(discordClient.user)
    # メンション先がBotでいて、そのメンション元のメッセージにAttachmentが含まれている場合
    if to_bot_mention:
        # 直前のメッセージが回答中のメッセージだったら質問できない
        async for channelMessage in channel.history(limit=1):
            if channelMessage.author == discordClient.user and channelMessage.content == Constants.answering_message:
                await channel.send("回答中は質問できません。しばらくお待ちください。")
                return

        temporary_message = await channel.send(Constants.answering_message)

        base_message = message.reference.resolved
        if base_message is None:
            return
        if base_message.author == discordClient.user and len(base_message.embeds) > 0:
            # Botが生成した画像に対するユーザの要望
            request_prompt: list[str] = []
            new_prompt = message.content
            if is_in_thread:
                # スレッド内部なので依頼ログを漁ってプロンプトを生成
                # スレッドタイトルが一番最初の質問
                request_prompt.append(message.channel.name)
                # スレッドの過去ログを数件遡り追加質問を取得
                async for first_message in channel.history(limit=10):
                    if first_message.author != discordClient.user:
                        request_prompt.append(first_message.content)
                response = query_gpt_image(botConfig.dalle_model, prompt=generate_revise_image_prompt(request_prompt,
                                                                                                      new_prompt))
                if "error" in response:
                    await temporary_message.edit(content=f"{response['error']['message']}")
                else:
                    response = response['response']
                    embed = discord.Embed()
                    embed.set_image(url=response['url'])
                    await temporary_message.edit(content=f"```{translate_text(response['prompt'])}```", embed=embed)
            else:
                before_prompt = base_message.content.split("\n")[0].replace("Q:", "")
                request_prompt.append(before_prompt)
                response = query_gpt_image(botConfig.dalle_model, prompt=generate_revise_image_prompt(request_prompt,
                                                                                                      new_prompt))
                if "error" in response:
                    await temporary_message.edit(content=f"{response['error']['message']}")
                else:
                    # スレッドの生成
                    thread = await message.channel.create_thread(name=before_prompt, auto_archive_duration=60,
                                                                 type=discord.ChannelType.public_thread)
                    response = response['response']
                    embed = discord.Embed()
                    embed.set_image(url=response['url'])
                    await thread.send(content=f"```{translate_text(response['prompt'])}```", embed=embed)
                    await temporary_message.edit(content=f"スレッドで返信しました {thread.mention}")
            return  # 画像生成への再支持の処理が終わったので終了

        if is_in_thread:
            if channel.owner == discordClient.user:
                await on_receive_message_in_bot_thread(message)
            else:
                # スレッドの中でTelGPTがオーナーでない場合は会話セッション
                return
        else:
            if to_bot_mention:
                await on_receive_mention_from_user(message)
            else:
                # botへのメンションがない場合は何もしない
                return


# noinspection PyUnresolvedReferences
@discordCommand.command(name="ai-question", description=f"{botConfig.discord_assistant_name}に質問します")
async def gpt_chat(interaction: discord.Interaction, prompt: str):
    result_message = f"Q:{prompt}\n"
    await interaction.response.defer()
    result = query_gpt_chat(botConfig.chat_model, prompt=prompt, system_setting="You are a helpful assistant.")
    if "error" in result:
        result_message += f"{result['error']['message']}"
    else:
        result_message += result['response']
    await send_message_async(interaction, result_message)


# noinspection PyUnresolvedReferences
@discordCommand.command(name="ai-question-udon",
                        description=f"{botConfig.discord_assistant_name}にUdonについて質問します")
async def gpt_question_udon(interaction: discord.Interaction, prompt: str):
    result_message = f"Q:{prompt}\n"
    await interaction.response.defer()
    system_setting = """
    You are an AI assistant specialized in VRChat development, focusing on UdonSharp programming, shader creation, and particle effects. Your role is to provide precise and practical answers tailored to the following domains:

    1. **UdonSharp**:
       - Writing, debugging, and optimizing UdonSharp scripts.
       - Implementing networking, interactions, and event-driven systems.
       - Best practices for improving performance in VRChat worlds.

    2. **Shaders**:
       - Developing shaders using Unity’s ShaderLab and HLSL.
       - Creating and optimizing PBR shaders and custom visual effects.
       - Troubleshooting shader performance and visual fidelity.

    3. **Particles**:
       - Setting up and customizing Unity’s Particle System.
       - Using VFX Graph for advanced particle effects.
       - Optimizing particle systems for VRChat environments.

    When answering, include detailed code examples, Unity Editor walkthroughs, and actionable advice. Provide best practices and refer to official documentation or reputable resources as needed. Aim to assist users in solving real-world development challenges effectively.
    """
    result = query_gpt_chat(botConfig.chat_model, prompt=prompt, system_setting=system_setting)
    if "error" in result:
        result_message += f"{result['error']['message']}"
    else:
        result_message += result['response']
    await send_message_async(interaction, result_message)


# noinspection PyUnresolvedReferences
@discordCommand.command(name="ai-image", description=f"{botConfig.discord_assistant_name}が画像を生成します")
async def gpt_image(interaction: discord.Interaction, prompt: str):
    result_message = f"Q:{prompt}\n"
    await interaction.response.defer()
    result = query_gpt_image(botConfig.dalle_model, prompt=prompt)
    if "error" in result:
        result_message += f"{result['error']['message']}"
        await interaction.followup.send(content=result_message)
    else:
        response = result['response']
        embed = discord.Embed()
        embed.set_image(url=response['url'])
        translated_prompt = translate_text(response['prompt'])
        result_message += f"```{translated_prompt}```"
        await interaction.followup.send(content=result_message, embed=embed)


# noinspection PyUnresolvedReferences
@discordCommand.command(name="ai-conversation", description=f"{botConfig.discord_assistant_name}とお話しします")
async def gpt_conversation(interaction: discord.Interaction, prompt: str):
    result_message = f"Q:{prompt}\n"
    is_in_thread = (interaction.channel.type == discord.ChannelType.private_thread
                    or interaction.channel.type == discord.ChannelType.public_thread)
    if is_in_thread:
        await interaction.channel.send("このコマンドはスレッド内では使用できません。", mention_author=True)
    else:
        await interaction.response.defer()

        result = query_gpt_chat(botConfig.chat_model, prompt=prompt, system_setting="You are a helpful assistant.")
        if "error" in result:
            result_message += f"{result['error']['message']}"
            await interaction.channel.send(result_message, mention_author=True)
        else:
            thread = await interaction.channel.create_thread(name=prompt, auto_archive_duration=60,
                                                             type=discord.ChannelType.public_thread)
            link = thread.mention
            await interaction.followup.send(content="スレッドを生成しました: " + link)
            result_message += result['response']
            await thread.send(result_message)


# noinspection PyUnresolvedReferences
@discordCommand.command(name="gpt-issue", description=f"TelGPTに意見要望を出します")
async def bot_create_issue(interaction: discord.Interaction, title: str, message: str):
    result_message = f"```{title}\n{message}```\n"
    await interaction.response.defer()

    # ユーザネームの先頭2文字だけ表示
    author = interaction.user.name[:2] + "***"
    result = create_issue(author, title, message)
    if "error" in result:
        result_message += f"{result['error']['message']}"
        await interaction.followup.send(content=result_message)
    else:
        response = result['response']
        result_message += f"Issueを作成しました: {response}"
        await send_message_async(interaction, result_message)


def download_image(url: str, save_file_path: str):
    response = requests.get(url)
    with open(save_file_path, 'wb') as file:
        file.write(response.content)


# noinspection PyUnresolvedReferences
@discordCommand.command(name="ai-recreate-image",
                        description=f"{botConfig.discord_assistant_name}が画像を再生成します")
async def bot_create_issue(interaction: discord.Interaction):
    await interaction.response.defer()

    # discordで投稿された画像をダウンロード
    message = interaction.message
    if len(message.attachments) == 0:
        await interaction.followup.send(content="画像が添付されていません")
        return
    attachment = message.attachments[0]
    if attachment.content_type != "image/png" and attachment.content_type != "image/jpeg":
        await interaction.followup.send(content="画像の形式が正しくありません")
        return
    save_file_path = "image.png"
    download_image(attachment.url, save_file_path)
    response = openAIClient.images.create_variation(
        model=BotConfig.dalle_model.value,
        image=open(save_file_path, "rb"),
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    embed = discord.Embed()
    embed.set_image(url=image_url)
    await interaction.followup.send(content="投稿された画像を元に再生成しました", embed=embed)


if __name__ == "__main__":
    discordClient.run(botConfig.discord_token)

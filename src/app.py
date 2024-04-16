import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

import discord
import requests
from discord import app_commands
from openai import OpenAI, BadRequestError

# AI が回答中のメッセージ
answering_message: Final[str] = "回答中です..."


# OpenAI ChatGPT の Chat モデルデータ
class ChatGPTChatModel(Enum):
    GPT_3_5 = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"


# OpenAI ChatGPT の Text to Speech モデルデータ
class ChatGPTTTSModel(Enum):
    TTS_1 = "tts-1"
    TTS_1_HD = "tts-1-hd"


# OpenAI ChatGPT の DALL-E モデルデータ
class ChatGPTDALLEModel(Enum):
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"


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
    audio_model: ChatGPTTTSModel
    dalle_model: ChatGPTDALLEModel

    def __init__(self):
        self.discord_assistant_name = 'TelGPT'
        self.discord_token = os.getenv("TEL_GPT_DISCORD_TOKEN")
        self.openai_api_key = os.getenv("TEL_GPT_OPEN_AI_TOKEN")
        self.deepl_api_key = os.getenv("TEL_GPT_DEEPL_TOKEN")
        self.chat_model = ChatGPTChatModel.GPT_4_TURBO
        self.audio_model = ChatGPTTTSModel.TTS_1
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


# OpenAIのエラーハンドリング. エラーコードによってメッセージを変更
def handle_bad_request_error(e: BadRequestError):
    if e.code == "content_policy_violation":
        message = "コンテンツポリシー違反です. 他の質問をしてください."
    else:
        message = "エラーが発生しました."

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
def query_gpt_audio(model: ChatGPTTTSModel, prompt: str, sound_file_path: Path) -> dict:
    try:
        response = openAIClient.audio.speech.create(
            model=model.value,
            voice="alloy",
            input=prompt
        )
        response.stream_to_file(sound_file_path)
        return {
            "response": "OK"
        }
    except BadRequestError as e:
        return handle_bad_request_error(e)
    except Exception:
        return {
            "error": {
                "code": 1,
                "message": "Unknown Error"
            }
        }


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
    except Exception:
        return {
            "error": {
                "code": 1,
                "message": "Unknown Error"
            }
        }


# noinspection PyBroadException
def query_gpt_chat(model: ChatGPTChatModel, prompt: str) -> dict:
    try:
        response = openAIClient.chat.completions.create(
            model=model.value,
            messages=[
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
    except Exception:
        return {
            "error": {
                "code": 1,
                "message": "Unknown Error"
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
    except Exception:
        return {
            "error": {
                "code": 1,
                "message": "Unknown Error"
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


@discordClient.event
async def on_message(message: discord.Message):
    if message.author == discordClient.user:
        return
    channel = message.channel
    is_in_thread = (channel.type == discord.ChannelType.private_thread
                    or channel.type == discord.ChannelType.public_thread)
    if is_in_thread and channel.owner == discordClient.user:
        # スレッドの中でTelGPTがオーナーの場合は会話セッション

        # 直前のメッセージが回答中のメッセージだったら質問できない
        async for channelMessage in channel.history(limit=1):
            if channelMessage.author == discordClient.user and channelMessage.content == answering_message:
                await channel.send("回答中は質問できません。しばらくお待ちください。")
                return

        temporary_message = await channel.send(answering_message)

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


# noinspection PyUnresolvedReferences
@discordCommand.command(name="ai-question", description=f"{botConfig.discord_assistant_name}に質問します")
async def gpt_chat(interaction: discord.Interaction, prompt: str):
    result_message = f"Q:{prompt}\n"
    await interaction.response.defer()
    result = query_gpt_chat(botConfig.chat_model, prompt=prompt)
    if "error" in result:
        result_message += f"{result['error']['message']}"
    else:
        result_message += result['response']
    await send_message_async(interaction, result_message)


# noinspection PyUnresolvedReferences
@discordCommand.command(name="ai-audio", description=f"{botConfig.discord_assistant_name}が文字を音声にします")
async def gpt_audio(interaction: discord.Interaction, prompt: str):
    result_message = f"Q:{prompt}\n"
    await interaction.response.defer()
    sound_file_path = Path(__file__).parent / "output.mp3"
    result = query_gpt_audio(botConfig.audio_model, prompt=prompt, sound_file_path=sound_file_path)
    if "error" in result:
        result_message += f"{result['error']['message']}"
        await send_message_async(interaction, result_message)
    else:
        await interaction.followup.send(content="generated", file=discord.File(sound_file_path))
    sound_file_path.unlink()


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

        result = query_gpt_chat(botConfig.chat_model, prompt=prompt)
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


discordClient.run(botConfig.discord_token)

from typing import Final, Optional

import discord
from discord import app_commands

from .configs import botConfig
from .tel_discord_command import TelDiscordCommand
from .entities.constants import Constants

# Discord Bot の設定
discordIntents = discord.Intents.default()
discordIntents.message_content = True
discordClient: Final[discord.Client] = discord.Client(intents=discordIntents)
discordCommand: Final[app_commands.CommandTree] = app_commands.CommandTree(discordClient)

telDiscordCommand: Final[TelDiscordCommand] = TelDiscordCommand(
    discord_client=discordClient,
)

# ステータス通知用の変数
status_channel: Optional[discord.TextChannel] = None

@discordClient.event
async def on_ready():
    global status_channel
    
    # # ステータス通知チャンネルの取得
    if botConfig.status_channel_id:
        try:
            channel_id = int(botConfig.status_channel_id)
            status_channel = discordClient.get_channel(channel_id)
            # 起動通知の送信
            if status_channel:
                await status_channel.send(Constants.bot_started_message)
            else:
                print(f"Warning: Could not find status channel with ID {channel_id}")
        except ValueError:
            print(f"Error: Invalid status channel ID format: {botConfig.status_channel_id}")
        except Exception as e:
            print(f"Error sending status notification: {str(e)}")
    await discordCommand.sync()


@discordClient.event
async def on_message(message: discord.Message):
    await telDiscordCommand.on_message(message)


@discordClient.event
async def on_disconnect():
    """切断された時のイベントハンドラ"""
    if status_channel:
        try:
            # 非同期関数を使用しているためループがないとエラーになる可能性がある
            # discordClientがまだアクティブな場合のみ実行
            if not discordClient.is_closed():
                await status_channel.send(Constants.bot_reconnecting_message)
        except Exception as e:
            print(f"Error sending disconnect notification: {str(e)}")


@discordClient.event
async def on_resumed():
    """再接続した時のイベントハンドラ"""
    if status_channel:
        try:
            await status_channel.send(Constants.bot_resumed_message)
        except Exception as e:
            print(f"Error sending resume notification: {str(e)}")


# # 管理用コマンド - ステータス通知の手動送信
# @discordCommand.command(
#     name="bot-status",
#     description="ボットの現在のステータスを確認または通知します"
# )
# async def bot_status(interaction: discord.Interaction, action: str = "check"):
#     """ボットの状態を確認または通知する管理コマンド
#
#     Args:
#         interaction: Discordのインタラクション
#         action: 実行するアクション（"check": 状態確認、"notify": 通知送信）
#     """
#     global status_channel
#
#     # 権限チェック（サーバ管理者のみ許可）
#     if not interaction.user.guild_permissions.administrator:
#         await interaction.response.send_message("このコマンドはサーバ管理者のみ使用できます。", ephemeral=True)
#         return
#
#     # ステータスチャンネル設定確認
#     if not status_channel and botConfig.status_channel_id:
#         try:
#             channel_id = int(botConfig.status_channel_id)
#             status_channel = discordClient.get_channel(channel_id)
#             if not status_channel:
#                 await interaction.response.send_message(
#                     f"ステータスチャンネル(ID: {channel_id})が見つかりませんでした。",
#                     ephemeral=True
#                 )
#                 return
#         except ValueError:
#             await interaction.response.send_message(
#                 f"ステータスチャンネルIDの形式が無効です: {botConfig.status_channel_id}",
#                 ephemeral=True
#             )
#             return
#         except Exception as e:
#             await interaction.response.send_message(
#                 f"ステータスチャンネルの設定に問題があります: {str(e)}",
#                 ephemeral=True
#             )
#             return
#
#     if action.lower() == "check":
#         # ボットの状態を確認して返却
#         latency = round(discordClient.latency * 1000)  # ミリ秒に変換
#         status_info = (
#             f"**ボットステータス状況**\n"
#             f"- ステータス: オンライン\n"
#             f"- レイテンシ: {latency}ms\n"
#             f"- ステータスチャンネル: {status_channel.mention if status_channel else '未設定'}"
#         )
#         await interaction.response.send_message(status_info, ephemeral=True)
#
#     elif action.lower() == "notify":
#         # 現在の状態を手動で通知
#         if status_channel:
#             await status_channel.send(Constants.bot_started_message)
#             await interaction.response.send_message("ステータス通知を送信しました。", ephemeral=True)
#         else:
#             await interaction.response.send_message(
#                 "ステータスチャンネルが設定されていないため通知を送信できません。",
#                 ephemeral=True
#             )
#     else:
#         await interaction.response.send_message(
#             "無効なアクションです。'check'または'notify'を指定してください。",
#             ephemeral=True
#         )


@discordCommand.command(
    name="ai-question-gemini",
    description=f"{botConfig.discord_assistant_name} (Gemini) に質問します"
)
async def gemini_question(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.gemini_question(interaction, prompt)


@discordCommand.command(
    name="ai-question-dev-vrc-gemini",
    description=f"{botConfig.discord_assistant_name} (Gemini) にVRChatでの開発に関して質問します"
)
async def gemini_question_udon(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.gemini_question_udon(interaction, prompt)


# @discordCommand.command(
#     name="ai-image-gemini",
#     description=f"{botConfig.discord_assistant_name} (Gemini) で画像生成します"
# )
# async def openai_generate_image(interaction: discord.Interaction, prompt: str):
#     await telDiscordCommand.gemini_generate_image(interaction, prompt)


@discordCommand.command(
    name="ai-question-claude",
    description=f"{botConfig.discord_assistant_name} (Claude) に質問します"
)
async def claude_question(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.claude_question(interaction, prompt)


@discordCommand.command(
    name="ai-question-dev-vrc-claude",
    description=f"{botConfig.discord_assistant_name} (Claude) にVRChatでの開発に関して質問します"
)
async def claude_question_udon(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.claude_question_udon(interaction, prompt)


@discordCommand.command(
    name="ai-question",
    description=f"{botConfig.discord_assistant_name} に質問します"
)
async def openai_question(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.openai_question(interaction, prompt)


@discordCommand.command(
    name="ai-question-dev-vrc",
    description=f"{botConfig.discord_assistant_name} にVRChatでの開発に関して質問します"
)
async def openai_question_udon(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.openai_question_udon(interaction, prompt)


@discordCommand.command(
    name="ai-image",
    description=f"{botConfig.discord_assistant_name} で画像生成します"
)
async def openai_generate_image(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.openai_generate_image(interaction, prompt)


# Stable Diffusion用の画像生成コマンドを追加
@discordCommand.command(
    name="ai-image-stable",
    description=f"{botConfig.discord_assistant_name} (Stable Diffusion) で画像生成します"
)
async def stablediffusion_generate_image(interaction: discord.Interaction, prompt: str, negative_prompt: str = None):
    """Stable Diffusionで画像を生成するコマンドハンドラ
    
    Args:
        interaction: Discordのインタラクション
        prompt: 画像生成のためのプロンプト
        negative_prompt: 生成から除外する要素を指定するネガティブプロンプト（省略可）
    """
    await telDiscordCommand.stablediffusion_generate_image(interaction, prompt, negative_prompt)


# @discordCommand.command(
#     name="ai-image-recreate",
#     description=f"{botConfig.discord_assistant_name} で画像を再生成します"
# )
# async def openai_recreate_image(interaction: discord.Interaction):
#     await telDiscordCommand.openai_recreate_image(interaction)


@discordCommand.command(
    name="ai-conversation",
    description=f"{botConfig.discord_assistant_name} と会話します"
)
async def openai_conversation(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.openai_conversation(interaction, prompt)


@discordCommand.command(
    name="ai-create-issue",
    description=f"{botConfig.discord_assistant_name} に関する要望を送信します"
)
async def git_create_issue(interaction: discord.Interaction, title: str, message: str):
    await telDiscordCommand.git_create_issue(interaction, title, message)

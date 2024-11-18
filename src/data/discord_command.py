from typing import Final

import discord
from discord import app_commands

from src.data.configs import botConfig
from src.data.tel_discord_command import TelDiscordCommand

# Discord Bot の設定
discordIntents = discord.Intents.default()
discordIntents.message_content = True
discordClient: Final[discord.Client] = discord.Client(intents=discordIntents)
discordCommand: Final[app_commands.CommandTree] = app_commands.CommandTree(discordClient)

telDiscordCommand: Final[TelDiscordCommand] = TelDiscordCommand(
    discord_client=discordClient,
)


@discordClient.event
async def on_ready():
    await discordCommand.sync()


@discordClient.event
async def on_message(message: discord.Message):
    await telDiscordCommand.on_message(message)


@discordCommand.command(
    name="ai-question-gemini",
    description=f"{botConfig.discord_assistant_name} (Gemini) に質問します"
)
async def gemini_question(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.gemini_question(interaction, prompt)


@discordCommand.command(
    name="ai-question-gemini-udon",
    description=f"{botConfig.discord_assistant_name} (Gemini) にUdonに関して質問します"
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
    name="ai-question-openai",
    description=f"{botConfig.discord_assistant_name} に質問します"
)
async def openai_question(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.openai_question(interaction, prompt)


@discordCommand.command(
    name="ai-question-openai-udon",
    description=f"{botConfig.discord_assistant_name} にUdonに関して質問します"
)
async def openai_question_udon(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.openai_question_udon(interaction, prompt)


@discordCommand.command(
    name="ai-image-openai",
    description=f"{botConfig.discord_assistant_name} で画像生成します"
)
async def openai_generate_image(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.openai_generate_image(interaction, prompt)


# @discordCommand.command(
#     name="ai-image-recreate",
#     description=f"{botConfig.discord_assistant_name} で画像を再生成します"
# )
# async def openai_recreate_image(interaction: discord.Interaction):
#     await telDiscordCommand.openai_recreate_image(interaction)


@discordCommand.command(
    name="ai-conversation-openai",
    description=f"{botConfig.discord_assistant_name} と会話します"
)
async def openai_conversation(interaction: discord.Interaction, prompt: str):
    await telDiscordCommand.openai_conversation(interaction, prompt)


@discordCommand.command(
    name="ai-create-issue",
    description=f"{botConfig.discord_assistant_name} に対する要望を投稿します"
)
async def git_create_issue(interaction: discord.Interaction, title: str, message: str):
    await telDiscordCommand.git_create_issue(interaction, title, message)

from abc import ABCMeta, abstractmethod

import discord


# noinspection PyMethodParameters
class TelGPTCommand(metaclass=ABCMeta):
    @abstractmethod
    async def gemini_question(interaction: discord.Interaction, prompt: str):
        """
        Gemini を使って質問に答える
        :param interaction: Discord の Interaction オブジェクト
        :param prompt: 質問の内容
        :return: None
        """
        pass

    @abstractmethod
    async def gemini_question_udon(interaction: discord.Interaction, prompt: str):
        """
        Gemini を使って Udon の質問に答える
        :param interaction: Discord の Interaction オブジェクト
        :param prompt: 質問の内容
        :return: None
        """
        pass

    @abstractmethod
    async def openai_question(interaction: discord.Interaction, prompt: str):
        """
        OpenAI を使って質問に答える
        :param interaction: Discord の Interaction オブジェクト
        :param prompt: 質問の内容
        :return: None
        """
        pass

    @abstractmethod
    async def openai_question_udon(interaction: discord.Interaction, prompt: str):
        """
        OpenAI を使って Udon の質問に答える
        :param interaction: Discord の Interaction オブジェクト
        :param prompt: 質問の内容
        :return: None
        """
        pass

    @abstractmethod
    async def openai_generate_image(interaction: discord.Interaction, prompt: str):
        """
        OpenAI を使って画像を生成する
        :param interaction: Discord の Interaction オブジェクト
        :param prompt: 画像の内容
        :return: None
        """
        pass

    @abstractmethod
    async def openai_conversation(interaction: discord.Interaction, prompt: str):
        """
        OpenAI を使って会話をする
        :param interaction: Discord の Interaction オブジェクト
        :param prompt:  会話の内容
        :return: None
        """
        pass

    @abstractmethod
    async def git_create_issue(interaction: discord.Interaction, title: str, message: str):
        """
        GitHub に Issue を作成する
        :param interaction: Discord の Interaction オブジェクト
        :param title: Issue のタイトル
        :param message: Issue の内容
        :return: None
        """
        pass

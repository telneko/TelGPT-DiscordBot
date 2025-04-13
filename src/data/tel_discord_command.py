import discord
import os
import logging

from .common_method import download_image, translate_text
from .configs import botConfig
from .entities.constants import Constants
from .entities.entity import Message
from .entities.telgpt_command import TelGPTCommand
from .gemini_api import GeminiAPI
from .github_api import GithubAPI
from .openai_api import OpenAIAPI
from .langchain_claude_api import LangchainClaudeAPI  # 追加
from .stability_api import StabilityAPI  # 追加

# ロガー設定
logger = logging.getLogger('discord')

# noinspection PyMethodMayBeStatic,DuplicatedCode,PyUnresolvedReferences,PyMethodOverriding
class TelDiscordCommand(TelGPTCommand):
    discord_client: discord.Client
    openAIApi: OpenAIAPI
    geminiApi: GeminiAPI
    githubApi: GithubAPI
    langchainClaudeApi: LangchainClaudeAPI  # 追加
    stabilityApi: StabilityAPI  # 追加: Stability API クライアント

    def __init__(self, discord_client: discord.Client):
        self.discord_client = discord_client
        self.openAIApi = OpenAIAPI()
        self.geminiApi = GeminiAPI()
        self.githubApi = GithubAPI()
        self.langchainClaudeApi = LangchainClaudeAPI()  # 追加
        self.stabilityApi = StabilityAPI()  # 追加: Stability API クライアントの初期化

    async def send_message_async(self, interaction: discord.Interaction, message: str):
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

    # TelGPTがオーナーのスレッド内でのメッセージ受信は会話となる
    async def on_receive_message_in_bot_thread(self, message: discord.Message):
        channel = message.channel
        # スレッドの中でTelGPTがオーナーの場合は会話セッション

        # 現在のメッセージが回答中のメッセージだったら回答できない
        async for channelMessage in channel.history(limit=1):
            if channelMessage.author == self.discord_client.user and channelMessage.content == Constants.answering_message:
                await channel.send("回答中は質問できません。しばらくお待ちください。")
                return

        temporary_message = await channel.send(Constants.answering_message)

        # スレッド内のメッセージを取得
        prompts = []
        async for channelMessage in channel.history(limit=10):
            if channelMessage.author == self.discord_client.user:
                prompts.append(Message(role="assistant", content=channelMessage.content))
            else:
                prompts.append(Message(role="user", content=channelMessage.content))
        prompts.reverse()

        # スレッド内のメッセージを使ってAIに質問
        result = self.openAIApi.conversation(botConfig.openai_chat_model, prompts=prompts)
        if "error" in result:
            await temporary_message.edit(content=f"{result['error']['message']}")
        else:
            await temporary_message.edit(content=result['response'])
        return

    # TelBOTへのメンションを受け取った場合の処理
    async def on_receive_mention_from_user(self, message: discord.Message):
        channel = message.channel
        if message.content.startswith("画像を加工して") or message.content.startswith("画像を再生成して"):
            # 現在のメッセージが回答中のメッセージだったら質問できない
            async for channelMessage in channel.history(limit=1):
                if channelMessage.author == self.discord_client.user and channelMessage.content == Constants.answering_message:
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
            response = self.openAIApi.create_image_variation(
                model=botConfig.openai_image_model,
                image_path=save_file_path
            )
            image_url = response['response'].url
            embed = discord.Embed()
            embed.set_image(url=image_url)
            await temporary_message.edit(content="生成された画像を元に再生成しました", embed=embed)
            return  # 画像再生成の処理が終わったので終了

    def generate_revise_image_prompt(self, old_prompts: list[str], new_prompt: str) -> str:
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

    async def on_message(self, message: discord.Message):
        if message.author == self.discord_client.user:
            return
        channel = message.channel

        is_in_thread = (channel.type == discord.ChannelType.private_thread
                    or channel.type == discord.ChannelType.public_thread)
        to_bot_mention = len(message.mentions) == 1 and message.mentions.__contains__(self.discord_client.user)
        # メンション先がBotであて、そのメンション内のメッセージにAttachmentが含まれている場合
        if to_bot_mention:
            # 現在のメッセージが回答中のメッセージだったら質問できない
            async for channelMessage in channel.history(limit=1):
                if channelMessage.author == self.discord_client.user and channelMessage.content == Constants.answering_message:
                    await channel.send("回答中は質問できません。しばらくお待ちください。")
                    return

            temporary_message = await channel.send(Constants.answering_message)

            base_message = message.reference.resolved
            if base_message is None:
                return
            if base_message.author == self.discord_client.user and len(base_message.embeds) > 0:
                # Botが生成した画像に関するユーザの要求
                request_prompt: list[str] = []
                new_prompt = message.content
                if is_in_thread:
                    # スレッド内部なのでチャット履歴を持ってプロンプトを生成
                    # スレッドタイトルが一番最初の質問
                    request_prompt.append(message.channel.name)
                    # スレッドの最初ログを数取得質問を取得
                    async for first_message in channel.history(limit=10):
                        if first_message.author != self.discord_client.user:
                            request_prompt.append(first_message.content)
                    response = self.openAIApi.generate_image(
                        botConfig.openai_image_model,
                        prompt=self.generate_revise_image_prompt(
                            request_prompt,
                            new_prompt
                        )
                    )
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
                    response = self.openAIApi.generate_image(
                        botConfig.openai_image_model,
                        prompt=self.generate_revise_image_prompt(
                            request_prompt,
                            new_prompt
                        )
                    )
                    if "error" in response:
                        await temporary_message.edit(content=f"{response['error']['message']}")
                    else:
                        # スレッドの生成
                        thread = await message.channel.create_thread(
                            name=before_prompt,
                            auto_archive_duration=60,
                            type=discord.ChannelType.public_thread
                        )
                        response = response['response']
                        embed = discord.Embed()
                        embed.set_image(url=response['url'])
                        await thread.send(content=f"```{translate_text(response['prompt'])}```", embed=embed)
                        await temporary_message.edit(content=f"スレッドで送信しました {thread.mention}")
                return  # 画像生成への返答の処理が終わったので終了

            if is_in_thread:
                if channel.owner == self.discord_client.user:
                    await self.on_receive_message_in_bot_thread(message)
                else:
                    # スレッドの中でTelGPTがオーナーでない場合は会話セッション
                    return
            else:
                if to_bot_mention:
                    await self.on_receive_mention_from_user(message)
                else:
                    # botへのメンションがない場合は何もしない
                    return

    async def gemini_question(self, interaction: discord.Interaction, prompt: str):
        result_message = f"Q:{prompt}\n"
        await interaction.response.defer()
        result = self.geminiApi.question(
            model=botConfig.gemini_chat_model,
            prompt=prompt,
            system_setting="You are a helpful assistant."
        )
        if "error" in result:
            result_message += f"{result['error']['message']}"
        else:
            result_message += result['response']
        await self.send_message_async(interaction, result_message)

    async def gemini_question_udon(self, interaction: discord.Interaction, prompt: str):
        result_message = f"Q:{prompt}\n"
        await interaction.response.defer()
        system_setting = """
            You are an AI assistant specialized in VRChat development, focusing on UdonSharp programming, shader creation, and particle effects. Your role is to provide precise and practical answers tailored to the following domains:

            1. **UdonSharp**:
               - Writing, debugging, and optimizing UdonSharp scripts.
               - Implementing networking, interactions, and event-driven systems.
               - Best practices for improving performance in VRChat worlds.

            2. **Shaders**:
               - Developing shaders using Unity's ShaderLab and HLSL.
               - Creating and optimizing PBR shaders and custom visual effects.
               - Troubleshooting shader performance and visual fidelity.

            3. **Particles**:
               - Setting up and customizing Unity's Particle System.
               - Using VFX Graph for advanced particle effects.
               - Optimizing particle systems for VRChat environments.

            When answering, include detailed code examples, Unity Editor walkthroughs, and actionable advice. Provide best practices and refer to official documentation or reputable resources as needed. Aim to assist users in solving real-world development challenges effectively.
            """
        result = self.geminiApi.question(
            model=botConfig.gemini_chat_model,
            prompt=prompt,
            system_setting=system_setting
        )
        if "error" in result:
            result_message += f"{result['error']['message']}"
        else:
            result_message += result['response']
        await self.send_message_async(interaction, result_message)

    async def claude_question(self, interaction: discord.Interaction, prompt: str):
        """
        Claude に質問を送信し、回答を返すコマンド処理
        
        Args:
            interaction: Discord のインタラクション
            prompt: ユーザーの質問内容
        """
        result_message = f"Q:{prompt}\n"
        await interaction.response.defer()
        result = self.langchainClaudeApi.question(
            model=botConfig.claude_model,
            prompt=prompt,
            system_setting="You are a helpful assistant."
        )
        if "error" in result:
            result_message += f"{result['error']['message']}"
        else:
            result_message += result['response']
        await self.send_message_async(interaction, result_message)

    async def claude_question_udon(self, interaction: discord.Interaction, prompt: str):
        """
        VRChat 開発に特化した Claude 質問コマンド処理
        
        Args:
            interaction: Discord のインタラクション
            prompt: ユーザーの質問内容
        """
        result_message = f"Q:{prompt}\n"
        await interaction.response.defer()
        system_setting = """
            You are an AI assistant specialized in VRChat development, focusing on UdonSharp programming, shader creation, and particle effects. Your role is to provide precise and practical answers tailored to the following domains:

            1. **UdonSharp**:
               - Writing, debugging, and optimizing UdonSharp scripts.
               - Implementing networking, interactions, and event-driven systems.
               - Best practices for improving performance in VRChat worlds.

            2. **Shaders**:
               - Developing shaders using Unity's ShaderLab and HLSL.
               - Creating and optimizing PBR shaders and custom visual effects.
               - Troubleshooting shader performance and visual fidelity.

            3. **Particles**:
               - Setting up and customizing Unity's Particle System.
               - Using VFX Graph for advanced particle effects.
               - Optimizing particle systems for VRChat environments.

            When answering, include detailed code examples, Unity Editor walkthroughs, and actionable advice. Provide best practices and refer to official documentation or reputable resources as needed. Aim to assist users in solving real-world development challenges effectively.
            """
        result = self.langchainClaudeApi.question(
            model=botConfig.claude_model,
            prompt=prompt,
            system_setting=system_setting
        )
        if "error" in result:
            result_message += f"{result['error']['message']}"
        else:
            result_message += result['response']
        await self.send_message_async(interaction, result_message)

    async def openai_question(self, interaction: discord.Interaction, prompt: str):
        result_message = f"Q:{prompt}\n"
        await interaction.response.defer()
        result = self.openAIApi.question(
            model=botConfig.openai_chat_model,
            prompt=prompt,
            system_setting="You are a helpful assistant."
        )
        if "error" in result:
            result_message += f"{result['error']['message']}"
        else:
            result_message += result['response']
        await self.send_message_async(interaction, result_message)

    async def openai_question_udon(self, interaction: discord.Interaction, prompt: str):
        result_message = f"Q:{prompt}\n"
        await interaction.response.defer()
        system_setting = """
            You are an AI assistant specialized in VRChat development, focusing on UdonSharp programming, shader creation, and particle effects. Your role is to provide precise and practical answers tailored to the following domains:

            1. **UdonSharp**:
               - Writing, debugging, and optimizing UdonSharp scripts.
               - Implementing networking, interactions, and event-driven systems.
               - Best practices for improving performance in VRChat worlds.

            2. **Shaders**:
               - Developing shaders using Unity's ShaderLab and HLSL.
               - Creating and optimizing PBR shaders and custom visual effects.
               - Troubleshooting shader performance and visual fidelity.

            3. **Particles**:
               - Setting up and customizing Unity's Particle System.
               - Using VFX Graph for advanced particle effects.
               - Optimizing particle systems for VRChat environments.

            When answering, include detailed code examples, Unity Editor walkthroughs, and actionable advice. Provide best practices and refer to official documentation or reputable resources as needed. Aim to assist users in solving real-world development challenges effectively.
            """
        result = self.openAIApi.question(
            model=botConfig.openai_chat_model,
            prompt=prompt,
            system_setting=system_setting
        )
        if "error" in result:
            result_message += f"{result['error']['message']}"
        else:
            result_message += result['response']
        await self.send_message_async(interaction, result_message)

    # async def gemini_generate_image(self, interaction: discord.Interaction, prompt: str):
    #     result_message = f"Q:{prompt}\n"
    #     await interaction.response.defer()
    #     result = self.geminiApi.generate_image(
    #         model=botConfig.gemini_image_model,
    #         prompt=prompt
    #     )
    #     if "error" in result:
    #         result_message += f"{result['error']['message']}"
    #         await interaction.followup.send(content=result_message)
    #     else:
    #         response = result['response']
    #         embed = discord.Embed()
    #         embed.set_image(url=response['url'])
    #         translated_prompt = translate_text(response['prompt'])
    #         result_message += f"```{translated_prompt}```"
    #         await interaction.followup.send(content=result_message, embed=embed)

    async def openai_generate_image(self, interaction: discord.Interaction, prompt: str):
        result_message = f"Q:{prompt}\n"
        await interaction.response.defer()
        result = self.openAIApi.generate_image(
            model=botConfig.openai_image_model,
            prompt=prompt
        )
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

    # 追加: Stable Diffusion で画像生成を行うメソッド
    async def stablediffusion_generate_image(self, interaction: discord.Interaction, prompt: str, negative_prompt: str = None):
        """
        Stable Diffusion APIを使用して画像を生成する

        Args:
            interaction: Discord インタラクション
            prompt: 画像生成のプロンプト
            negative_prompt: ネガティブプロンプト（生成から除外したい要素）
        """
        result_message = f"Q:{prompt}\n"
        if negative_prompt:
            result_message += f"Negative: {negative_prompt}\n"
        
        await interaction.response.defer()
        
        try:
            # Prompt を OpenAI で StableDiffusion 用の英語プロンプトに変換
            # OpenAI API を使用してプロンプトを翻訳
            # こちらのプロンプトを
            gen_translated_prompt = self.openAIApi.question(
                model=botConfig.openai_chat_model,
                prompt=prompt,
                system_setting="You are a bot that simply responds to the user's input prompts with English prompts for StableDiffusion. You do not need to respond with “Yes, sir” or “OK”, just simply respond with the prompt for SD."
            )
            if "error" in gen_translated_prompt:
                result_message += f"{gen_translated_prompt['error']['message']}"
                await interaction.channel.send(result_message, mention_author=True)
            else:
                # Stability API を使って画像生成
                request_message = gen_translated_prompt['response']
                result = self.stabilityApi.generate_image(
                    model=botConfig.stable_diffusion_model,
                    prompt=request_message,
                    negative_prompt=negative_prompt
                )

                if "error" in result:
                    # エラーがあった場合はログ出力してからユーザーに通知
                    logger.error(f"Stability API Error: {result['error']['message']}")
                    result_message += f"画像生成エラー: {result['error']['message']}"
                    await interaction.followup.send(content=result_message)
                    return

                response = result['response']

                # ファイルが存在し、読み込み可能か確認
                file_path = response['url']
                if not os.path.exists(file_path) or not os.path.isfile(file_path):
                    logger.error(f"Generated image file not found: {file_path}")
                    await interaction.followup.send(content=f"画像ファイルが見つかりません。生成処理は成功しましたが、ファイルの保存に問題が発生した可能性があります。")
                    return

                # Discord用のFileオブジェクトを作成して送信
                discord_file = discord.File(file_path, filename="generated_image.png")

                # シード情報の追加
                seed_info = ""
                if response.get('seed'):
                    seed_info = f" (Seed: {response['seed']})"

                result_message += f"```{request_message}```"

                # ファイルと一緒にメッセージを送信
                await interaction.followup.send(content=result_message, file=discord_file)
            
        except Exception as e:
            # 予期しないエラーの場合も詳細を記録して通知
            logger.exception(f"Unexpected error in stablediffusion_generate_image: {str(e)}")
            await interaction.followup.send(content=f"画像生成中に予期しないエラーが発生しました: {str(e)}")

    # async def openai_recreate_image(self, interaction: discord.Interaction):
    #     await interaction.response.defer()
    #
    #     # discordで送信された画像をダウンロード
    #     message = interaction.message
    #     if message == None or len(message.attachments) == 0:
    #         await interaction.followup.send(content="画像が添付されていません")
    #         return
    #     attachment = message.attachments[0]
    #     if attachment.content_type != "image/png" and attachment.content_type != "image/jpeg":
    #         await interaction.followup.send(content="画像の形式が正しくありません")
    #         return
    #     save_file_path = "image.png"
    #     download_image(attachment.url, save_file_path)
    #     response = self.openAIApi.create_image_variation(
    #         model=BotConfig.openai_image_model,
    #         image_path=save_file_path
    #     )
    #     image_url = response.data[0].url
    #     embed = discord.Embed()
    #     embed.set_image(url=image_url)
    #     await interaction.followup.send(content="送信された画像を元に再生成しました", embed=embed)

    async def openai_conversation(self, interaction: discord.Interaction, prompt: str):
        result_message = f"Q:{prompt}\n"
        is_in_thread = (interaction.channel.type == discord.ChannelType.private_thread
                   or interaction.channel.type == discord.ChannelType.public_thread)
        if is_in_thread:
            await interaction.channel.send("このコマンドはスレッド内では使用できません。", mention_author=True)
        else:
            await interaction.response.defer()

            result = self.openAIApi.question(
                model=botConfig.openai_chat_model,
                prompt=prompt,
                system_setting="You are a helpful assistant."
            )
            if "error" in result:
                result_message += f"{result['error']['message']}"
                await interaction.channel.send(result_message, mention_author=True)
            else:
                thread = await interaction.channel.create_thread(
                    name=prompt,
                    auto_archive_duration=60,
                    type=discord.ChannelType.public_thread
                )
                link = thread.mention
                await interaction.followup.send(content="スレッドを生成しました: " + link)
                result_message += result['response']
                await thread.send(result_message)

    async def git_create_issue(self, interaction: discord.Interaction, title: str, message: str):
        result_message = f"```{title}\n{message}```\n"
        await interaction.response.defer()

        # ユーザーネームの先頭2文字だけ表示
        author = interaction.user.name[:2] + "***"
        result = self.githubApi.create_issue(author, title, message)
        if "error" in result:
            result_message += f"{result['error']['message']}"
            await interaction.followup.send(content=result_message)
        else:
            response = result['response']
            result_message += f"Issueを作成しました: {response}"
            await self.send_message_async(interaction, result_message)

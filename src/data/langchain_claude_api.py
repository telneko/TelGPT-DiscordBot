from typing import Dict, List

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from .configs import botConfig
from .entities.claude_model import ClaudeModel
from .entities.entity import Message


class LangchainClaudeAPI:
    """
    Langchain を使用した Claude API のラッパークラス
    """
    
    def __init__(self):
        """
        Claude API の設定を初期化
        """
        self.api_key = botConfig.claude_api_key

    def _create_chat_model(self, model: ClaudeModel):
        """
        Claude の Langchain モデルを作成
        
        Args:
            model: 使用する Claude モデル
            
        Returns:
            ChatAnthropic: 設定済みの Claude モデル
        """
        return ChatAnthropic(
            anthropic_api_key=self.api_key,
            model_name=model.value,
            temperature=0.7,
        )

    def question(self, model: ClaudeModel, prompt: str, system_setting: str) -> Dict:
        """
        Claude に質問を投げる
        
        Args:
            model: 使用する Claude モデル
            prompt: ユーザーの質問内容
            system_setting: システムプロンプト
        
        Returns:
            dict: レスポンスまたはエラー情報
        """
        try:
            # システムプロンプトを設定
            japanese_system = "Your response should be in Japanese."
            combined_system = f"{japanese_system}\n\n{system_setting}"
            
            # チャットモデルとプロンプトテンプレートを作成
            chat_model = self._create_chat_model(model)
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", combined_system),
                ("human", "{input}")
            ])
            
            # Langchain チェーンを構築
            chain = prompt_template | chat_model | StrOutputParser()
            
            # 実行
            response = chain.invoke({"input": prompt})
            
            return {
                "response": response
            }
        except Exception as e:
            return {
                "error": {
                    "code": 1,
                    "message": f"Claude API Error: {str(e)}"
                }
            }

    def conversation(self, model: ClaudeModel, prompts: List[Message]) -> Dict:
        """
        会話履歴を使用して Claude と会話
        
        Args:
            model: 使用する Claude モデル
            prompts: 会話履歴のメッセージリスト
        
        Returns:
            dict: レスポンスまたはエラー情報
        """
        try:
            # チャットモデル作成
            chat_model = self._create_chat_model(model)
            
            # メッセージを Langchain フォーマットに変換
            messages = []
            
            # システムメッセージを先頭に追加
            messages.append(SystemMessage(content="Your response should be in Japanese."))
            
            # ユーザーとアシスタントのメッセージを追加
            for msg in prompts:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(SystemMessage(content=f"You previously responded: {msg.content}"))
            
            # 応答を生成
            response = chat_model.invoke(messages)
            
            return {
                "response": response.content
            }
        except Exception as e:
            return {
                "error": {
                    "code": 1,
                    "message": f"Claude API Error: {str(e)}"
                }
            }

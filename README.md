# TelGPT-DiscordBot

discord server で利用している bot です

## Env

| 環境変数名                | 説明                  |
|-------------------------|-----------------------|
| TEL_GPT_DISCORD_TOKEN   | Discord Bot のトークン |
| TEL_GPT_OPEN_AI_TOKEN  | OpenAI の API キー    |
| TEL_GPT_DEEPL_TOKEN     | DeepL の API キー     |
| TEL_GPT_GEMINI_TOKEN    | Gemini の API キー    |
| TEL_GPT_CLAUDE_TOKEN    | Claude の API キー    |
| TEL_GPT_STABILITY_TOKEN | Stability AI の API キー |
| TEL_GPT_STATUS_CHANNEL_ID | ステータス通知用チャンネルID |

## 機能

### ステータス通知機能

ボットは以下のタイミングでステータス通知を送信します:

- 起動時
- 終了時
- 接続が切断された時
- 再接続した時

ステータス通知を利用するには:

1. ボットからの通知を受け取るためのテキストチャンネルを作成します
2. そのチャンネルのIDを取得します(チャンネル名を右クリック→IDをコピー)
3. `TEL_GPT_STATUS_CHANNEL_ID` 環境変数に取得したIDを設定します

管理者は `/bot-status` コマンドを使って:
- 現在のボット状態を確認 (`/bot-status action:check`)
- 手動でステータス通知を送信 (`/bot-status action:notify`)

ができます。

### AI質問・画像生成機能

以下のコマンドでAIを利用することができます:

| コマンド | 説明 |
|---------|------|
| `/ai-question` | OpenAI (GPT) に質問します |
| `/ai-question-gemini` | Google Gemini に質問します |
| `/ai-question-claude` | Anthropic Claude に質問します |
| `/ai-image` | OpenAI DALL-E で画像を生成します |
| `/ai-image-stable` | Stable Diffusion で画像を生成します |
| `/ai-conversation` | スレッドを作成して AI と会話します |

VRChat開発に特化した質問コマンドも用意されています:
- `/ai-question-dev-vrc` (OpenAI)
- `/ai-question-dev-vrc-gemini` (Gemini)
- `/ai-question-dev-vrc-claude` (Claude)

### 画像生成機能の詳細

#### DALL-E による画像生成
`/ai-image` コマンドでは、OpenAI の DALL-E モデルを使用して画像を生成します。
プロンプトを入力するだけで、AIが解釈して画像を生成します。

#### Stable Diffusion による画像生成
`/ai-image-stable` コマンドでは、Stability AI の Stable Diffusion モデルを使用して画像を生成します。
このコマンドには以下のオプションがあります:

- `prompt`: 生成したい画像の説明（必須）
- `negative_prompt`: 生成から除外したい要素の説明（オプション）

例: `/ai-image-stable prompt:美しい山の風景と湖 negative_prompt:人物,建物,テキスト`

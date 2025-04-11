# TelGPT-DiscordBot

discord server で利用している bot です

## Env

| 環境変数名                 | 説明                   |
|----------------------------|------------------------|
| TEL_GPT_DISCORD_TOKEN    | Discord Bot のトークン |
| TEL_GPT_OPEN_AI_TOKEN    | OpenAI の API キー    |
| TEL_GPT_DEEPL_TOKEN      | DeepL の API キー     |
| TEL_GPT_GEMINI_TOKEN     | Gemini の API キー    |
| TEL_GPT_CLAUDE_TOKEN     | Claude の API キー    |
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
2. そのチャンネルのIDを取得します（チャンネル名を右クリック→IDをコピー）
3. `TEL_GPT_STATUS_CHANNEL_ID` 環境変数に取得したIDを設定します

管理者は `/bot-status` コマンドを使って:
- 現在のボット状態を確認 (`/bot-status action:check`)
- 手動でステータス通知を送信 (`/bot-status action:notify`)

ができます。

#!/usr/bin/env python3
"""
masa-agent Discord Bot
「claude-code」チャンネルでメッセージを受け取り、Groq APIで返答する
"""

import os
import discord
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TARGET_CHANNEL = os.getenv("DISCORD_CHANNEL", "claude-code")

groq_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

SYSTEM_PROMPT = """あなたはX投稿生成の専門AIエージェント。
オペレーター：X8 GROUP 人事部・まさ（@sfre_x8_00）
歌舞伎町のホストクラブ・ボーイズバー・メンズコンセプトカフェ 計7店舗の人事担当。
元プレイヤー（ホスト・キャスト経験あり）、中高社会科教員免許保持。

【使い方】
- 「長文」と言えば600〜1200字のX投稿文を生成
- 「短文」と言えば150〜250字のX投稿文を生成
- URLや記事を貼れば内容を分析して投稿ネタを提案
- 何でも日本語で質問してください

【投稿文のルール】
- 断言調ベース（〜だ。〜だった。）
- 心理学用語・現場エピソード・「売れる子vs売れない子」の対比を入れる
- 店名・グループ名は出さない
- 本文のみ出力（説明・前置き不要）
"""

@client.event
async def on_ready():
    print(f"✅ {client.user} として起動しました")
    print(f"📢 監視チャンネル: #{TARGET_CHANNEL}")

@client.event
async def on_message(message):
    # 自分自身のメッセージは無視
    if message.author == client.user:
        return

    # 対象チャンネル以外は無視
    if message.channel.name != TARGET_CHANNEL:
        return

    # 「thinking...」を表示
    async with message.channel.typing():
        try:
            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message.content}
                ],
                max_tokens=2000,
                temperature=0.7,
            )
            reply = response.choices[0].message.content

            # 2000字以上は分割して送信
            if len(reply) > 2000:
                for i in range(0, len(reply), 2000):
                    await message.channel.send(reply[i:i+2000])
            else:
                await message.channel.send(reply)

        except Exception as e:
            await message.channel.send(f"エラーが発生しました: {str(e)}")

client.run(DISCORD_TOKEN)

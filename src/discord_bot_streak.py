import os
import discord
from discord.ext import tasks
import psycopg2
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

DISCORD_TOKEN_STREAK = os.getenv('DISCORD_TOKEN_STREAK')
DISCORD_CHANNEL_ID_STREAK = int(os.getenv('DISCORD_CHANNEL_ID_STREAK'))
DATABASE_URL = os.getenv('DATABASE_URL')

intents = discord.Intents.default()
intents.messages = True  # Ensure the bot can read message history
client = discord.Client(intents=intents)

async def delete_previous_messages(channel):
    async for message in channel.history(limit=100):
        if message.author == client.user:
            await message.delete()

@tasks.loop(hours=24)
async def send_streak_leaderboard():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        cur = conn.cursor()

        cur.execute('''
            SELECT u.username, s.highest_streak
            FROM user_scores s
            JOIN users u ON s.user_id = u.user_id
            ORDER BY s.highest_streak DESC
            LIMIT 10
        ''')
        leaderboard = cur.fetchall()
        leaderboard_df = pd.DataFrame(leaderboard, columns=["Username", "Highest Streak"])
        leaderboard_df["Rank"] = leaderboard_df.index + 1

        message = "**Highest Streak Leaderboard!** \n\n"
        
        message += "**A user has increased their highest streak:** \n\n"

        for index, row in leaderboard_df.iterrows():
            rank_emoji = "🥇" if row['Rank'] == 1 else "🥈" if row['Rank'] == 2 else "🥉" if row['Rank'] == 3 else f"{row['Rank']}:"
            message += f"{rank_emoji} {row['Username']} {row['Highest Streak']}\n"
            message += "=============================================\n"

        channel = client.get_channel(DISCORD_CHANNEL_ID_STREAK)
        await delete_previous_messages(channel)
        await channel.send(message)
    finally:
        cur.close()
        conn.close()
        await client.close()

@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')
    send_streak_leaderboard.start()

client.run(DISCORD_TOKEN_STREAK)

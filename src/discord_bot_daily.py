import os
import discord
from discord.ext import tasks
import psycopg2
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

DISCORD_TOKEN_DAILY = os.getenv('DISCORD_TOKEN_DAILY')
DISCORD_CHANNEL_ID_DAILY = int(os.getenv('DISCORD_CHANNEL_ID_DAILY'))
DATABASE_URL = os.getenv('DATABASE_URL')

intents = discord.Intents.default()
intents.messages = True  # Ensure the bot can read message history
client = discord.Client(intents=intents)

async def delete_previous_messages(channel):
    async for message in channel.history(limit=100):
        if message.author == client.user:
            await message.delete()

@tasks.loop(hours=24)
async def send_daily_leaderboard():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        cur = conn.cursor()

        # Check if there is any user who did the daily challenge today
        cur.execute('''
            SELECT EXISTS (
                SELECT 1
                FROM user_daily_scores
                WHERE score_date = CURRENT_DATE
            )
        ''')
        user_did_challenge = cur.fetchone()[0]

        cur.execute('''
            SELECT u.username, ds.daily_score
            FROM user_daily_scores ds
            JOIN users u ON ds.user_id = u.user_id
            WHERE ds.score_date = CURRENT_DATE
            ORDER BY ds.daily_score DESC
            LIMIT 10
        ''')
        leaderboard = cur.fetchall()
        leaderboard_df = pd.DataFrame(leaderboard, columns=["Username", "Daily Score"])
        leaderboard_df["Rank"] = leaderboard_df.index + 1

        message = "**Daily Leaderboard!** \n\n"
        if user_did_challenge:
            message += "**A user has done the daily challenge:** \n\n"

        for index, row in leaderboard_df.iterrows():
            rank_emoji = "🥇" if row['Rank'] == 1 else "🥈" if row['Rank'] == 2 else "🥉" if row['Rank'] == 3 else f"{row['Rank']}️:"
            message += f"{rank_emoji} {row['Username']} {row['Daily Score']}/30\n"
            message += "=============================================\n"

        channel = client.get_channel(DISCORD_CHANNEL_ID_DAILY)
        await delete_previous_messages(channel)
        await channel.send(message)
    finally:
        cur.close()
        conn.close()
        await client.close()

@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')
    send_daily_leaderboard.start()

client.run(DISCORD_TOKEN_DAILY)

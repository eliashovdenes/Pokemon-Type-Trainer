import os
import discord
from discord.ext import tasks
import psycopg2
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))
DATABASE_URL = os.getenv('DATABASE_URL')

client = discord.Client(intents=discord.Intents.default())

@tasks.loop(hours=24)
async def send_daily_leaderboard():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        cur = conn.cursor()
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

        message = "🎉 **Daily Leaderboard** 🎉\n\n"

        for index, row in leaderboard_df.iterrows():
            rank_emoji = "🥇" if row['Rank'] == 1 else "🥈" if row['Rank'] == 2 else "🥉" if row['Rank'] == 3 else f"{row['Rank']}️⃣"
            message += f"{rank_emoji} **Rank {row['Rank']}**\n"
            message += f"👤 **Username:** {row['Username']}\n"
            message += f"🏆 **Score:** {row['Daily Score']} 🏅\n"
            message += f"───────────── \n\n\n"

        channel = client.get_channel(DISCORD_CHANNEL_ID)
        await channel.send(message)
    finally:
        cur.close()
        conn.close()
        await client.close()  # Disconnect the bot after sending the message

@client.event
async def on_ready():
    send_daily_leaderboard.start()
    print(f'Bot connected as {client.user}')

client.run(DISCORD_TOKEN)

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot Online: {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

bot.run(MTU0NjcyNjk3MjA1MzM5MzUwOA.G1nwIu.U2qvrBurwetJ4wSiql5Frr5BkceKhQoHV6a4pk)

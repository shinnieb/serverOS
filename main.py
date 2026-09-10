import os
import discord
from discord.ext import commands
import config

class ServerOSBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        # تحميل الملفات مباشرة من مجلد المشروع الأساسي
        for filename in os.listdir("."):
            if filename.endswith(".py") and filename != "main.py" and filename != "config.py":
                await self.load_extension(filename[:-3])

        if hasattr(config, 'TARGET_GUILD_ID') and config.TARGET_GUILD_ID:
            guild = discord.Object(id=config.TARGET_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"تمت مزامنة الأوامر بنجاح مع السيرفر: {config.TARGET_GUILD_ID}")
        else:
            await self.tree.sync()
            print("تمت مزامنة الأوامر عاماً مع جميع السيرفرات")

    async def on_ready(self):
        print(f"البوت جاهز ويعمل باسم : {self.user}")

bot = ServerOSBot()
bot.run(config.DISCORD_TOKEN)

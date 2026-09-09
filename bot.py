import os
import discord
from discord.ext import commands
import config

class ServerOSBot(commands.Bot):
    def __init__(self):
        # تفعيل جميع الصلاحيات اللازمة
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!",
            intents=intents
        )

    async def setup_hook(self):
        # تحميل جميع ملفات الأوامر (Cogs) تلقائياً من مجلد cogs
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")

        # مزامنة الأوامر مع السيرفر المحدد المكتوب في config.py
        if hasattr(config, 'TARGET_GUILD_ID') and config.TARGET_GUILD_ID:
            guild = discord.Object(id=config.TARGET_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"تمت مزامنة الأوامر بنجاح مع السيرفر: {config.TARGET_GUILD_ID}")
        else:
            # مزامنة عامة في حال عدم تحديد سيرفر
            await self.tree.sync()
            print("تمت مزامنة الأوامر عاماً مع جميع السيرفرات")

    async def on_ready(self):
        print(f"البوت جاهز ويعمل باسم : {self.user}")

bot = ServerOSBot()
bot.run(config.DISCORD_TOKEN)
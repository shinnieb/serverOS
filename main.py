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
        # تحميل الملفات من الجذر تلقائياً
        for filename in os.listdir("."):
            if filename.endswith(".py") and filename not in ["main.py", "config.py"]:
                cog_name = filename[:-3]
                try:
                    if cog_name not in self.extensions:
                        await self.load_extension(cog_name)
                        print(f"تم تحميل الملف بنجاح: {cog_name}")
                except Exception as e:
                    print(f"فشل تحميل الملف {cog_name}: {e}")

        # مزامنة عامة أولية للبوت
        try:
            await self.tree.sync()
            print("تمت مزامنة الأوامر العامة بنجاح!")
        except Exception as e:
            print(f"فشل في المزامنة: {e}")

    # هذي الدالة هي سر سرعة ProBot: أول ما يدخل البوت أي سيرفر، يفرز الأوامر فيه فوراً
    async def on_guild_join(self, guild):
        try:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"تمت مزامنة الأوامر فوراً للسيرفر الجديد: {guild.name}")
        except Exception as e:
            print(f"فشل مزامنة السيرفر الجديد: {e}")

    async def on_ready(self):
        print(f"البوت جاهز ويعمل باسم : {self.user}")

bot = ServerOSBot()
bot.run(config.DISCORD_TOKEN)

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
        # البحث وتحميل جميع ملفات الأوامر المنفصلة في المجلد الحالي مباشرة
        for filename in os.listdir("."):
            if filename.endswith(".py") and filename not in ["main.py", "config.py"]:
                cog_name = filename[:-3]
                try:
                    # التحقق لمنع تكرار التحميل
                    if cog_name not in self.extensions:
                        await self.load_extension(cog_name)
                        print(f"تم تحميل الملف بنجاح: {cog_name}")
                except Exception as e:
                    print(f"فشل تحميل الملف {cog_name}: {e}")

        # مزامنة عامة تلقائية لجميع السيرفرات بدون الحاجة لـ ID محدد
        try:
            await self.tree.sync()
            print("تمت مزامنة الأوامر عاماً مع جميع السيرفرات بنجاح!")
        except Exception as e:
            print(f"فشل في مزامنة الأوامر: {e}")

    async def on_ready(self):
        print(f"البوت جاهز ويعمل باسم : {self.user}")

bot = ServerOSBot()
bot.run(config.DISCORD_TOKEN)

import discord
from discord.ext import commands
from discord import app_commands

class SettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.select(
        placeholder="اختر النظام الذي تريد إعداده...",
        options=[
            discord.SelectOption(label="إعداد اللوق", value="logs", description="تحديد قناة سجل الأحداث", emoji="📋"),
            discord.SelectOption(label="إعداد الترحيب", value="welcome", description="تحديد رسالة وقناة الترحيب", emoji="👋"),
            discord.SelectOption(label="إعداد التذاكر", value="tickets", description="تحديد قسم التذاكر والدعم الفني", emoji="🎫"),
            discord.SelectOption(label="إعداد الاقتراحات", value="suggestions", description="تحديد قناة الاقتراحات", emoji="💡")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        val = select.values[0]
        if val == "logs":
            await interaction.response.send_message("⚙️ لإعداد اللوق، انتقل إلى ملف اللوق أو استخدم الأمر الخاص به.", ephemeral=True)
        elif val == "welcome":
            await interaction.response.send_message("⚙️ لإعداد الترحيب، انتقل إلى ملف الترحيب أو استخدم الأمر الخاص به.", ephemeral=True)
        elif val == "tickets":
            await interaction.response.send_message("⚙️ لإعداد التذاكر، استخدم نظام التذاكر المخصص.", ephemeral=True)
        elif val == "suggestions":
            await interaction.response.send_message("⚙️ لإعداد الاقتراحات، حدد قناة الاقتراحات من قسمها.", ephemeral=True)

class General(commands.Cog):
    def __init__(self, bot_client):
        self.bot_client = bot_client

    @app_commands.command(name="ping", description="فحص سرعة استجابة البوت")
    async def ping_cmd(self, interaction: discord.Interaction):
        latency = round(self.bot_client.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! سرعة استجابة البوت: `{latency}ms`", ephemeral=True)

    @app_commands.command(name="help", description="عرض قائمة المساعدة والأوامر المتاحة في نظام ServerOS")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 مركز المساعدة - ServerOS",
            description="نظام إدارة السيرفرات المتكامل والمتوافق مع اللغة العربية.\nاستخدم أوامر السلاش (/) لتصفح الأقسام:",
            color=discord.Color.blue()
        )
        embed.add_field(name="⚙️ الأساسية", value="`/help`, `/setup`, `/ping`, `/about`", inline=False)
        embed.add_field(name="📋 باقي الأنظمة", value="يمكنك التحكم بالترحيب، اللوق، والتذاكر عبر ملفاتها المخصصة.", inline=False)
        embed.set_footer(text="ServerOS - جميع الحقوق محفوظة")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="setup", description="إعداد النظام الأولي للسيرفر عبر اللوحة التفاعلية")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="لوحة إعداد ServerOS التفاعلية",
            description="اختر من القائمة أدناه النظام الذي تود إعداده وتخصيصه لسيرفرك:",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, view=SettingsView(), ephemeral=True)

    @app_commands.command(name="about", description="عرض معلومات تفصيلية عن بوت ServerOS")
    async def about_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 معلومات بوت ServerOS",
            description="بوت عربي متكامل لإدارة وحماية السيرفرات بكفاءة عالية.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="لغة البرمجة", value="Python 3.10+", inline=True)
        embed.add_field(name="المكتبة", value="Discord.py", inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(General(bot))
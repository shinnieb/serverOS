import discord
from discord.ext import commands
from discord import app_commands

class SettingsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.select(
        placeholder="✨ اختر النظام الذي تريد إعداده وتخصيصه...",
        options=[
            discord.SelectOption(label="إعداد اللوق", value="logs", description="تحديد قناة سجل الأحداث والمراقبة", emoji="📋"),
            discord.SelectOption(label="إعداد الترحيب والخاص", value="welcome", description="تحديد روم الترحيب ورسالة الـ DM", emoji="👋"),
            discord.SelectOption(label="إعداد التذاكر السرية", value="tickets", description="تحديد روم الإدارة لاستلام التذاكر", emoji="🎫"),
            discord.SelectOption(label="إعداد الاقتراحات", value="suggestions", description="تحديد قناة الاقتراحات والتصويت", emoji="💡")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        val = select.values[0]
        if val == "logs":
            await interaction.response.send_message("⚙️ لإعداد نظام اللوق والمراقبة، استخدم الأمر المخصص للإدارة في ملف اللوق.", ephemeral=True)
        elif val == "welcome":
            await interaction.response.send_message("⚙️ لإعداد الترحيب استخدم `/إعداد_الترحيب`، ولتخصيص رسالة الخاص استخدم `/إعداد_رسالة_الخاص`.", ephemeral=True)
        elif val == "tickets":
            await interaction.response.send_message("⚙️ لإعداد التذاكر السرية، استخدم أمر `/تحديد_روم_الإدارة` في روم الإدارة الخاصة.", ephemeral=True)
        elif val == "suggestions":
            await interaction.response.send_message("⚙️ لإعداد الاقتراحات، حدد القناة المخصصة عبر الأمر البرمجي للاقتراحات.", ephemeral=True)

class General(commands.Cog):
    def __init__(self, bot_client):
        self.bot_client = bot_client

    @app_commands.command(name="ping", description="[فني] فحص سرعة استجابة وسرعة سيرفرات بوت ServerOS")
    async def ping_cmd(self, interaction: discord.Interaction):
        latency = round(self.bot_client.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 نظام قياس السرعة - ServerOS",
            description=f"سرعة استجابة البوت الحالية: ` {latency}ms ` ⚡",
            color=0x2b2d31
        )
        embed.set_footer(text=f"Developed by i5z_w")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="help", description="عرض لوحة المساعدة المركزية وقائمة الأوامر المتاحة في ServerOS")
    async def help_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 لوحة التحكم والمساعدة المركزية - ServerOS",
            description="نظام إداري أمني متكامل وخاص لإدارة السيرفرات باحترافية وسرية تامة.\nاستخدم أوامر السلاش (`/`) أدناه للتنقل:",
            color=0x2b2d31
        )
        embed.add_field(
            name="🛡️ الأوامر الإدارية والسيادية", 
            value="• `/setup` - فتح لوحة الإعدادات التفاعلية الشاملة.\n• `/إعداد_الترحيب` - لتحديد روم ترحيب الأعضاء.\n• `/إعداد_رسالة_الخاص` - لتخصيص رسالة الـ DM الفورية.\n• `/إعلان_خاص` - لإرسال إعلان لجميع أعضاء السيرفر بالخاص.\n• `/تحديد_روم_الإدارة` - لتحديد روم التذاكر السرية.", 
            inline=False
        )
        embed.add_field(
            name="📊 الأوامر العامة والأعضاء", 
            value="• `/server` - عرض تقرير فخم وشامل عن معلومات السيرفر.\n• `/تذكرة` - فتح تذكرة دعم فني سرية مع الإدارة.\n• `/ping` - فحص سرعة استجابة البوت.", 
            inline=False
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url if interaction.client.user else None)
        embed.set_footer(text=f"ServerOS Pro • Developed by i5z_w", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="setup", description="[خاص بالإداريين] فتح لوحة الإعدادات والربط الشاملة للسيرفر")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⚙️ لوحة الإعداد والتحكم المركزي - ServerOS",
            description="مرحباً بك في مركز العمليات الإداري.\nاختر النظام أو القسم الذي تود إعداده وتفعيله في سيرفرك بكل سهولة من القائمة أدناه:",
            color=0x2b2d31
        )
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text=f"ServerOS Pro • Developed by i5z_w")
        
        await interaction.response.send_message(embed=embed, view=SettingsView(), ephemeral=True)

    @app_commands.command(name="about", description="عرض بطاقة المعلومات والتعريف بنظام ServerOS والمطور")
    async def about_cmd(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🤖 بطاقة تعريف بوت ServerOS",
            description="نظام ذكي متطور ومخصص لإدارة وحماية السيرفرات بسرية واحترافية عالية.",
            color=0x2b2d31
        )
        embed.add_field(name="👑 المطور والمبتكر", value="`i5z_w`", inline=True)
        embed.add_field(name="💻 لغة البرمجة", value="Python 3.10+", inline=True)
        embed.add_field(name="📚 المكتبة المستخدمة", value="Discord.py", inline=True)
        embed.add_field(name="🔐 مستوى الحماية والأمان", value="نظام أمني متكامل مع قواعد بيانات SQLite وإخفاء العمليات عن العامة.", inline=False)
        
        if interaction.client.user.avatar:
            embed.set_thumbnail(url=interaction.client.user.avatar.url)
        embed.set_footer(text=f"جميع الحقوق محفوظة © ServerOS • Dev: i5z_w")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(General(bot))

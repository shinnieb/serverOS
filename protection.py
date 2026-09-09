import discord
from discord import app_commands
from discord.ext import commands

class Protection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="نظام_الحماية", description="عرض لوحة وحالة أنظمة الحماية في السيرفر")
    @app_commands.checks.has_permissions(administrator=True)
    async def protection(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🛡️ لوحة نظام الحماية - ServerOS",
            description="حالة أنظمة الحماية الحالية في السيرفر:",
            color=discord.Color.red()
        )
        embed.add_field(name="حماية من الغارات (Antiraid)", value="🟢 مفعل", inline=True)
        embed.add_field(name="مكافحة السبام (Antispam)", value="🟢 مفعل", inline=True)
        embed.add_field(name="حماية المنشنات (Antimention)", value="🟢 مفعل", inline=True)
        embed.add_field(name="حماية دخول البوتات (Antibot)", value="🟢 مفعل", inline=True)
        embed.set_footer(text="يمكنك استخدام الأوامر الفرعية لتعديل إعدادات كل نظام.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="مكافحة_السبام", description="تفعيل أو تعطيل نظام مكافحة السبام")
    @app_commands.describe(status="اختر حالة النظام")
    @app_commands.choices(status=[
        app_commands.Choice(name="تفعيل", value="on"),
        app_commands.Choice(name="تعطيل", value="off")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def antispam(self, interaction: discord.Interaction, status: app_commands.Choice[str]):
        state = "مفعل" if status.value == "on" else "معطل"
        await interaction.response.send_message(f"تم تغيير حالة نظام مكافحة السبام إلى: **{state}**", ephemeral=True)

    @app_commands.command(name="حماية_دخول_البوتات", description="التحكم في نظام حماية دخول البوتات غير المصرح بها")
    @app_commands.describe(status="اختر حالة النظام")
    @app_commands.choices(status=[
        app_commands.Choice(name="تفعيل", value="on"),
        app_commands.Choice(name="تعطيل", value="off")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def antibot(self, interaction: discord.Interaction, status: app_commands.Choice[str]):
        state = "مفعل" if status.value == "on" else "معطل"
        await interaction.response.send_message(f"تم تغيير حالة حماية دخول البوتات إلى: **{state}**", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Protection(bot))
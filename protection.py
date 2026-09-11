import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

class Protection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS server_protection (
                guild_id INTEGER PRIMARY KEY,
                antiraid TEXT DEFAULT 'مفعل',
                antispam TEXT DEFAULT 'مفعل',
                antimention TEXT DEFAULT 'مفعل',
                antibot TEXT DEFAULT 'مفعل'
            )
        """)
        conn.commit()
        conn.close()

    def get_protection_status(self, guild_id):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("SELECT antiraid, antispam, antimention, antibot FROM server_protection WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("INSERT INTO server_protection (guild_id) VALUES (?)", (guild_id,))
            conn.commit()
            row = ('مفعل', 'مفعل', 'مفعل', 'مفعل')
        conn.close()
        return row

    def update_protection_status(self, guild_id, column, status):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("SELECT guild_id FROM server_protection WHERE guild_id = ?", (guild_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO server_protection (guild_id) VALUES (?)", (guild_id,))
        
        query = f"UPDATE server_protection SET {column} = ? WHERE guild_id = ?"
        cursor.execute(query, (status, guild_id))
        conn.commit()
        conn.close()

    @app_commands.command(name="نظام_الحماية", description="عرض لوحة وحالة أنظمة الحماية في السيرفر")
    @app_commands.checks.has_permissions(administrator=True)
    async def protection(self, interaction: discord.Interaction):
        antiraid, antispam, antimention, antibot = self.get_protection_status(interaction.guild_id)
        
        def format_status(val):
            return "🟢 مفعل" if val == "مفعل" else "🔴 معطل"

        embed = discord.Embed(
            title="🛡️ لوحة نظام الحماية - ServerOS",
            description="حالة أنظمة الحماية الحالية في السيرفر:",
            color=discord.Color.red()
        )
        embed.add_field(name="حماية من الغارات (Antiraid)", value=format_status(antiraid), inline=True)
        embed.add_field(name="مكافحة السبام (Antispam)", value=format_status(antispam), inline=True)
        embed.add_field(name="حماية المنشنات (Antimention)", value=format_status(antimention), inline=True)
        embed.add_field(name="حماية دخول البوتات (Antibot)", value=format_status(antibot), inline=True)
        embed.set_footer(text="يمكنك استخدام الأوامر المخصصة لتعديل وتغيير حالة كل نظام.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="حماية_الغارات", description="تفعيل أو تعطيل نظام الحماية من الغارات (Antiraid)")
    @app_commands.describe(status="اختر حالة النظام")
    @app_commands.choices(status=[
        app_commands.Choice(name="تفعيل", value="مفعل"),
        app_commands.Choice(name="تعطيل", value="معطل")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def antiraid(self, interaction: discord.Interaction, status: app_commands.Choice[str]):
        self.update_protection_status(interaction.guild_id, "antiraid", status.value)
        state_icon = "🟢 مفعل" if status.value == "مفعل" else "🔴 معطل"
        await interaction.response.send_message(f"تم تغيير حالة الحماية من الغارات (Antiraid) إلى: **{state_icon}**", ephemeral=True)

    @app_commands.command(name="مكافحة_السبام", description="تفعيل أو تعطيل نظام مكافحة السبام (Antispam)")
    @app_commands.describe(status="اختر حالة النظام")
    @app_commands.choices(status=[
        app_commands.Choice(name="تفعيل", value="مفعل"),
        app_commands.Choice(name="تعطيل", value="معطل")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def antispam(self, interaction: discord.Interaction, status: app_commands.Choice[str]):
        self.update_protection_status(interaction.guild_id, "antispam", status.value)
        state_icon = "🟢 مفعل" if status.value == "مفعل" else "🔴 معطل"
        await interaction.response.send_message(f"تم تغيير حالة نظام مكافحة السبام (Antispam) إلى: **{state_icon}**", ephemeral=True)

    @app_commands.command(name="حماية_المنشنات", description="تفعيل أو تعطيل نظام حماية المنشنات المزعجة (Antimention)")
    @app_commands.describe(status="اختر حالة النظام")
    @app_commands.choices(status=[
        app_commands.Choice(name="تفعيل", value="مفعل"),
        app_commands.Choice(name="تعطيل", value="معطل")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def antimention(self, interaction: discord.Interaction, status: app_commands.Choice[str]):
        self.update_protection_status(interaction.guild_id, "antimention", status.value)
        state_icon = "🟢 مفعل" if status.value == "مفعل" else "🔴 معطل"
        await interaction.response.send_message(f"تم تغيير حالة حماية المنشنات (Antimention) إلى: **{state_icon}**", ephemeral=True)

    @app_commands.command(name="حماية_دخول_البوتات", description="التحكم في نظام حماية دخول البوتات غير المصرح بها (Antibot)")
    @app_commands.describe(status="اختر حالة النظام")
    @app_commands.choices(status=[
        app_commands.Choice(name="تفعيل", value="مفعل"),
        app_commands.Choice(name="تعطيل", value="معطل")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def antibot(self, interaction: discord.Interaction, status: app_commands.Choice[str]):
        self.update_protection_status(interaction.guild_id, "antibot", status.value)
        state_icon = "🟢 مفعل" if status.value == "مفعل" else "🔴 معطل"
        await interaction.response.send_message(f"تم تغيير حالة حماية دخول البوتات (Antibot) إلى: **{state_icon}**", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Protection(bot))

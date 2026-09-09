import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3
from datetime import datetime, timedelta

class Activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()
        self.check_inactivity.start()

    def init_db(self):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS activity_settings (guild_id INTEGER PRIMARY KEY, channel_id INTEGER, role_id INTEGER, max_days INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS user_activity (guild_id INTEGER, user_id INTEGER, last_post TEXT, PRIMARY KEY (guild_id, user_id))")
        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT channel_id FROM activity_settings WHERE guild_id = ?", (message.guild.id,))
        row = cursor.fetchone()
        if row and row[0] == message.channel.id:
            now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO user_activity (guild_id, user_id, last_post) VALUES (?, ?, ?) ON CONFLICT(guild_id, user_id) DO UPDATE SET last_post = excluded.last_post", (message.guild.id, message.author.id, now_str))
            conn.commit()
        conn.close()

    @app_commands.command(name="set_activity", description="تفعيل وإعداد نظام سحب الرتبة من الأعضاء الخاملين")
    @app_commands.describe(channel="الروم المراد مراقبة النشر فيه", role="الرتبة التي ستُسحب من الخاملين", days="عدد الأيام المسموحة للغياب")
    async def set_activity(self, interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role, days: int):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activity_settings (guild_id, channel_id, role_id, max_days) VALUES (?, ?, ?, ?) ON CONFLICT(guild_id) DO UPDATE SET channel_id = excluded.channel_id, role_id = excluded.role_id, max_days = excluded.max_days", (interaction.guild_id, channel.id, role.id, days))
        conn.commit()
        conn.close()
        embed = discord.Embed(title="⚙️ تم تفعيل نظام مراقبة النشاط", description=f"📌 **روم المراقبة:** {channel.mention}\n🎭 **الرتبة:** {role.mention}\n⏱️ **مهلة الخمول:** {days} أيام", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="stop_activity", description="إيقاف نظام مراقبة النشاط وسحب الرتب")
    async def stop_activity(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activity_settings WHERE guild_id = ?", (interaction.guild_id,))
        conn.commit()
        conn.close()
        embed = discord.Embed(title="🛑 تم إيقاف النظام", description="تم تعطيل مراقبة النشاط وسحب الرتب بنجاح.", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @tasks.loop(hours=1)
    async def check_inactivity(self):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT guild_id, role_id, max_days FROM activity_settings")
        settings = cursor.fetchall()
        for guild_id, role_id, max_days in settings:
            guild = self.bot.get_guild(guild_id)
            if not guild: continue
            role = guild.get_role(role_id)
            if not role: continue
            cursor.execute("SELECT user_id, last_post FROM user_activity WHERE guild_id = ?", (guild_id,))
            users = cursor.fetchall()
            for user_id, last_post_str in users:
                member = guild.get_member(user_id)
                if not member or role not in member.roles: continue
                last_post = datetime.strptime(last_post_str, "%Y-%m-%d %H:%M:%S")
                if datetime.utcnow() - last_post > timedelta(days=max_days):
                    try:
                        await member.remove_roles(role, reason="Inactivity")
                    except discord.Forbidden:
                        pass
        conn.close()

    @check_inactivity.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Activity(bot))
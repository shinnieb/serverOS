import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

def get_welcome_channel(guild_id: int):
    conn = sqlite3.connect("serveros.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS welcome_settings (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)")
    cursor.execute("SELECT channel_id FROM welcome_settings WHERE guild_id = ?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="إعداد_الترحيب", description="تحديد الروم المخصصة لرسائل الترحيب والمغادرة")
    @app_commands.describe(channel="اختر روم الترحيب")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS welcome_settings (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)")
        cursor.execute("REPLACE INTO welcome_settings (guild_id, channel_id) VALUES (?, ?)", (interaction.guild.id, channel.id))
        conn.commit()
        conn.close()
        
        await interaction.response.send_message(f"✅ تم ضبط روم الترحيب بنجاح إلى: {channel.mention}", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel_id = get_welcome_channel(member.guild.id)
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="👋 عضو جديد انضم إلينا!",
                    description=f"مرحباً بك {member.mention} في سيرفر **{member.guild.name}**!\nنتمنى لك وقتاً ممتعاً معنا.",
                    color=discord.Color.green()
                )
                if member.avatar:
                    embed.set_thumbnail(url=member.avatar.url)
                embed.set_footer(text=f"رقم العضو: {member.id}")
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel_id = get_welcome_channel(member.guild.id)
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="🚪 مغادرة عضو",
                    description=f"غادر العضو **{member.name}** السيرفر.",
                    color=discord.Color.red()
                )
                await channel.send(embed=embed)

    @app_commands.command(name="اختبار_الترحيب", description="تجربة رسالة الترحيب الحالية")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_test(self, interaction: discord.Interaction):
        member = interaction.user
        embed = discord.Embed(
            title="👋 عضو جديد انضم إلينا! (تجريبي)",
            description=f"مرحباً بك {member.mention} في سيرفر **{interaction.guild.name}**!\nنتمنى لك وقتاً ممتعاً معنا.",
            color=discord.Color.green()
        )
        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
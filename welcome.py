import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

def get_db_connection():
    conn = sqlite3.connect("serveros.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS welcome_settings (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            dm_message TEXT
        )
    """)
    conn.commit()
    return conn

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="إعداد_الترحيب", description="[خاص بالإداريين] تحديد الروم المخصصة لرسائل الترحيب والمغادرة في السيرفر")
    @app_commands.describe(channel="اختر روم الترحيب العام")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO welcome_settings (guild_id, channel_id) VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET channel_id = ?
        """, (interaction.guild.id, channel.id, channel.id))
        conn.commit()
        conn.close()
        
        await interaction.response.send_message(f"✅ تم ضبط روم الترحيب العام بنجاح إلى: {channel.mention}", ephemeral=True)

    @app_commands.command(name="إعداد_رسالة_الخاص", description="[خاص بالإداريين] تخصيص رسالة ترحيبية ترسل للعضو الجديد في الخاص (DM) عند دخوله")
    @app_commands.describe(الرسالة="اكتب محتوى رسالة الترحيب التي ستصل العضو في الخاص")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_welcome_dm(self, interaction: discord.Interaction, الرسالة: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO welcome_settings (guild_id, dm_message) VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET dm_message = ?
        """, (interaction.guild.id, الرسالة, الرسالة))
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"✅ تم حفظ وتحديث رسالة الترحيب الخاصة (DM) لهذا السيرفر بنجاح!", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT channel_id, dm_message FROM welcome_settings WHERE guild_id = ?", (guild.id,))
        row = cursor.fetchone()
        conn.close()

        channel_id = row[0] if row else None
        custom_dm = row[1] if row else None

        # 1. إرسال رسالة الترحيب العامة في روم السيرفر
        if channel_id:
            channel = guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="✨ انضم إلينا بطل جديد!",
                    description=f"أهلاً بك يا {member.mention} في سيرفر **{guild.name}**.\n\n🎯 نتمنى لك قضاء أوقات ممتعة معنا، وتأكد من قراءة القوانين!",
                    color=0x2b2d31
                )
                if member.avatar:
                    embed.set_thumbnail(url=member.avatar.url)
                embed.add_field(name="👥 ترتيب العضو", value=f"#{guild.member_count}", inline=True)
                embed.set_footer(text=f"ID: {member.id}", icon_url=guild.icon.url if guild.icon else None)
                await channel.send(embed=embed)

        # 2. إرسال رسالة الخاص المخصصة لهذا السيرفر تلقائياً للعضو الجديد
        if custom_dm:
            try:
                dm_embed = discord.Embed(
                    title=f"🌟 مرحباً بك في {guild.name}",
                    description=custom_dm,
                    color=0x2b2d31
                )
                if guild.icon:
                    dm_embed.set_thumbnail(url=guild.icon.url)
                dm_embed.set_footer(text=f"نتمنى لك رحلة ممتعة في {guild.name}")
                
                await member.send(embed=dm_embed)
            except discord.Forbidden:
                pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT channel_id FROM welcome_settings WHERE guild_id = ?", (member.guild.id,))
        row = cursor.fetchone()
        conn.close()

        channel_id = row[0] if row else None
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="🚪 غادرنا عضو",
                    description=f"نودع العضو **{member.name}**، نتمنى له التوفيق.",
                    color=discord.Color.red()
                )
                await channel.send(embed=embed)

    @app_commands.command(name="اختبار_الترحيب", description="[خاص بالإداريين] تجربة شكل رسالة الترحيب العامة والخاصة الحالية")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_test(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT dm_message FROM welcome_settings WHERE guild.id = ? if 0 else SELECT dm_message FROM welcome_settings WHERE guild_id = ?", (guild.id, guild.id))
        row = cursor.fetchone()
        conn.close()
        
        custom_dm = row[0] if row and row[0] else "لم يتم ضبط رسالة خاصة لهذا السيرفر بعد عبر الأمر /إعداد_رسالة_الخاص"

        await interaction.response.send_message(f"💬 **رسالة الخاص المسجلة حالياً لسيرفرك هي:**\n\n{custom_dm}", ephemeral=True)

    @app_commands.command(name="إعلان_خاص", description="[خاص بالإداريين] إرسال إعلان رسمي لجميع أعضاء السيرفر عبر الرسائل الخاصة (DM)")
    @app_commands.describe(الرسالة="اكتب نص الإعلان أو التحديث المراد إرساله للأعضاء")
    @app_commands.checks.has_permissions(administrator=True)
    async def send_announcement(self, interaction: discord.Interaction, الرسالة: str):
        await interaction.response.send_message("🚀 جاري إرسال الإعلان لجميع أعضاء السيرفر في الخاص، قد يستغرق ذلك بعض الوقت...", ephemeral=True)
        
        guild = interaction.guild
        success_count = 0
        fail_count = 0

        embed = discord.Embed(
            title=f"📢 إعلان رسمي من إدارة {guild.name}",
            description=الرسالة,
            color=0x2b2d31
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=f"تم إرسال هذا الإعلان بواسطة الإدارة.")

        for member in guild.members:
            if member.bot:
                continue
            try:
                await member.send(embed=embed)
                success_count += 1
            except discord.Forbidden:
                fail_count += 1

        try:
            await interaction.followup.send(f"✅ تم الانتهاء من الإرسال بنجاح!\n- تم الإرسال بنجاح إلى: `{success_count}` عضو\n- تعذر الإرسال لهم (خاص مغلق): `{fail_count}` عضو", ephemeral=True)
        except discord.HTTPException:
            pass

async def setup(bot):
    await bot.add_cog(Welcome(bot))

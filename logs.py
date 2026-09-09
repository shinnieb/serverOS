import sqlite3
import discord
from discord import app_commands
from discord.ext import commands

def get_log_channel(guild_id: int):
    conn = sqlite3.connect("serveros.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS log_settings (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)")
    cursor.execute("SELECT channel_id FROM log_settings WHERE guild_id = ?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="إعداد_اللوق", description="تحديد الروم الخاصة بسجل الأحداث والنشاطات في السيرفر")
    @app_commands.describe(channel="اختر روم السجلات")
    @app_commands.checks.has_permissions(administrator=True)
    async def logs_setup(self, interaction: discord.Interaction, channel: discord.TextChannel):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS log_settings (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)")
        cursor.execute("REPLACE INTO log_settings (guild_id, channel_id) VALUES (?, ?)", (interaction.guild.id, channel.id))
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="📋 إعداد سجل الأحداث",
            description=f"✅ تم بنجاح ربط روم السجلات بـ: {channel.mention}\nسيتم إرسال كافة التنبيهات والأحداث إليها.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="تعطيل_اللوق", description="إيقاف وتعطيل نظام سجل الأحداث")
    @app_commands.checks.has_permissions(administrator=True)
    async def logs_disable(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM log_settings WHERE guild_id = ?", (interaction.guild.id,))
        conn.commit()
        conn.close()
        
        await interaction.response.send_message("🛑 تم تعطيل نظام سجل الأحداث وإزالة الربط بنجاح.", ephemeral=True)

    @app_commands.command(name="اختبار_اللوق", description="إرسال رسالة تجريبية إلى روم السجلات للتأكد من العمل")
    @app_commands.checks.has_permissions(administrator=True)
    async def logs_test(self, interaction: discord.Interaction):
        channel_id = get_log_channel(interaction.guild.id)
        if not channel_id:
            await interaction.response.send_message("❌ لم يتم تحديد روم السجلات بعد! استخدم أمر /إعداد_اللوق أولاً.", ephemeral=True)
            return
            
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="🔍 اختبار نظام سجل الأحداث (Logs)",
                description="هذه رسالة تجريبية للتأكد من أن روم اللوق تعمل وتستقبل التنبيهات بكفاءة.",
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"بواسطة المشرف: {interaction.user.name}")
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ تم إرسال رسالة الاختبار بنجاح إلى روم السجلات.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ روم السجلات المحددة غير موجودة أو تم حذفها.", ephemeral=True)
            # 1. مراقبة حذف الرسائل
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        channel_id = get_log_channel(message.guild.id)
        if channel_id:
            channel = message.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(title="🗑️ تم حذف رسالة", color=discord.Color.orange())
                embed.add_field(name="الكاتب", value=message.author.mention, inline=True)
                embed.add_field(name="القناة", value=message.channel.mention, inline=True)
                embed.add_field(name="المحتوى", value=message.content or "*[رسالة فارغة أو وسائط]*", inline=False)
                embed.set_footer(text=f"معرف المستخدم: {message.author.id}")
                await channel.send(embed=embed)

    # 2. مراقبة تعديل الرسائل
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        channel_id = get_log_channel(before.guild.id)
        if channel_id:
            channel = before.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(title="✏️ تم تعديل رسالة", color=discord.Color.gold())
                embed.add_field(name="الكاتب", value=before.author.mention, inline=True)
                embed.add_field(name="القناة", value=before.channel.mention, inline=True)
                embed.add_field(name="قبل التعديل", value=before.content or "*[فارغ]*", inline=False)
                embed.add_field(name="بعد التعديل", value=after.content or "*[فارغ]*", inline=False)
                embed.set_footer(text=f"معرف المستخدم: {before.author.id}")
                await channel.send(embed=embed)

    # 3. مراقبة دخول عضو جديد
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel_id = get_log_channel(member.guild.id)
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="📥 انضمام عضو جديد",
                    description=f"العضو {member.mention} (`{member.name}`) انضم إلى السيرفر.",
                    color=discord.Color.green()
                )
                if member.avatar:
                    embed.set_thumbnail(url=member.avatar.url)
                embed.set_footer(text=f"عدد الأعضاء الآن: {member.guild.member_count}")
                await channel.send(embed=embed)

    # 4. مراقبة مغادرة عضو
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel_id = get_log_channel(member.guild.id)
        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="📤 مغادرة عضو",
                    description=f"العضو **{member.name}** غادر السيرفر.",
                    color=discord.Color.red()
                )
                embed.set_footer(text=f"معرف العضو: {member.id}")
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logs(bot))
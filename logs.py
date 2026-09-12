import sqlite3
import discord
from discord import app_commands
from discord.ext import commands
import datetime

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
            title="📋 إعداد سجل الأحداث المتقدم",
            description=f"✅ تم بنجاح ربط روم السجلات الشاملة بـ: {channel.mention}\nسيتم رصد كافة العمليات والمسؤولين عنها بدقة.",
            color=discord.Color.from_rgb(46, 204, 113)
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
                title="🔍 اختبار النظام الشامل (مع معرفة المسؤولين)",
                description="النظام جاهز الآن لرصد كل شاردة وواردة وتحديد هوية المشرف أو الفاعل في كل إجراء.",
                color=discord.Color.from_rgb(52, 152, 219),
                timestamp=datetime.datetime.utcnow()
            )
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ تم إرسال رسالة الاختبار بنجاح.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ روم السجلات المحددة غير موجودة.", ephemeral=True)

    # 1. رصد حذف الرسائل (ومعرفة من حذفها إن وجدت في السجل)
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild:
            return
        channel_id = get_log_channel(message.guild.id)
        if not channel_id:
            return
        channel = message.guild.get_channel(channel_id)
        if not channel:
            return

        deleter = "غير معروف (حذفها صاحبها أو السجل غير متاح)"
        try:
            async for entry in message.guild.audit_logs(limit=5, action=discord.AuditLogAction.message_delete):
                if entry.target.id == message.author.id and (datetime.datetime.utcnow() - entry.created_at).total_seconds() < 10:
                    deleter = f"{entry.user.mention} (`{entry.user}`)"
                    break
        except Exception:
            pass

        content = message.content or "*[محتوى فارغ أو مرفقات وسائط]*"
        if len(content) > 1500:
            content = content[:1497] + "..."

        embed = discord.Embed(
            title="🗑️ رصد حذف رسالة",
            color=discord.Color.from_rgb(231, 76, 60),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="👤 صاحب الرسالة", value=f"{message.author.mention} (`{message.author}`)", inline=False)
        embed.add_field(name="🛠️ من قام بالحذف", value=deleter, inline=False)
        embed.add_field(name="📍 القناة", value=message.channel.mention, inline=False)
        embed.add_field(name="📝 المحتوى المحذوف", value=f"```ansi\n\u001b[31m{content}\u001b[0m\n```", inline=False)
        embed.set_footer(text=f"User ID: {message.author.id}")
        await channel.send(embed=embed)

    # 2. تعديل الرسائل
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or not before.guild or before.content == after.content:
            return
        channel_id = get_log_channel(before.guild.id)
        if not channel_id:
            return
        channel = before.guild.get_channel(channel_id)
        if not channel:
            return

        old_c = before.content or "*[فارغ]*"
        new_c = after.content or "*[فارغ]*"
        if len(old_c) > 1000: old_c = old_c[:997] + "..."
        if len(new_c) > 1000: new_c = new_c[:997] + "..."

        embed = discord.Embed(
            title="✏️ تعديل رسالة",
            color=discord.Color.from_rgb(241, 196, 15),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="👤 صاحب الرسالة", value=f"{before.author.mention} (`{before.author}`)", inline=False)
        embed.add_field(name="📍 القناة", value=before.channel.mention, inline=False)
        embed.add_field(name="📜 قبل التعديل", value=f"```ansi\n\u001b[33m{old_c}\u001b[0m\n```", inline=False)
        embed.add_field(name="✨ بعد التعديل", value=f"```ansi\n\u001b[32m{new_c}\u001b[0m\n```", inline=False)
        embed.set_footer(text=f"User ID: {before.author.id}")
        await channel.send(embed=embed)

    # 3. دخول عضو
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel_id = get_log_channel(member.guild.id)
        if not channel_id: return
        channel = member.guild.get_channel(channel_id)
        if not channel: return

        created_ts = int(member.created_at.timestamp())
        embed = discord.Embed(
            title="📥 انضمام عضو جديد",
            color=discord.Color.from_rgb(46, 204, 113),
            timestamp=datetime.datetime.utcnow()
        )
        if member.avatar: embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="👤 العضو", value=f"{member.mention} (`{member}`)", inline=False)
        embed.add_field(name="🆔 المعرف", value=f"`{member.id}`", inline=False)
        embed.add_field(name="📅 إنشاء الحساب", value=f"<t:{created_ts}:F> (<t:{created_ts}:R>)", inline=False)
        embed.set_footer(text=f"إجمالي الأعضاء: {member.guild.member_count}")
        await channel.send(embed=embed)

    # 4. مغادرة عضو
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel_id = get_log_channel(member.guild.id)
        if not channel_id: return
        channel = member.guild.get_channel(channel_id)
        if not channel: return

        embed = discord.Embed(
            title="📤 مغادرة عضو",
            color=discord.Color.from_rgb(231, 76, 60),
            timestamp=datetime.datetime.utcnow()
        )
        if member.avatar: embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="👤 العضو", value=f"{member.mention} (`{member}`)", inline=False)
        embed.add_field(name="🆔 المعرف", value=f"`{member.id}`", inline=False)
        embed.set_footer(text=f"إجمالي الأعضاء: {member.guild.member_count}")
        await channel.send(embed=embed)

    # 5. رصد الطرد (Kick) والحظر (Ban) والتايم أوت (Timeout) عبر سجل التدقيق
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        channel_id = get_log_channel(after.guild.id)
        if not channel_id: return
        channel = after.guild.get_channel(channel_id)
        if not channel: return

        # مراقبة التايم أوت
        if before.timed_out_until != after.timed_out_until:
            if after.timed_out_until:
                moderator = "مشرف غير معروف"
                reason = "لا يوجد سبب مدون"
                try:
                    async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_update):
                        if entry.target.id == after.id:
                            moderator = f"{entry.user.mention} (`{entry.user}`)"
                            reason = entry.reason or "لا يوجد سبب"
                            break
                except Exception:
                    pass

                timeout_ts = int(after.timed_out_until.timestamp())
                embed = discord.Embed(
                    title="⏳ تطبيق عقوبة إسكات (Timeout)",
                    color=discord.Color.from_rgb(230, 126, 34),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(name="👤 العضو المعاقب", value=f"{after.mention} (`{after}`)", inline=False)
                embed.add_field(name="🛠️ بواسطة المشرف", value=moderator, inline=False)
                embed.add_field(name="📌 السبب", value=reason, inline=False)
                embed.add_field(name="⏰ ينتهي في", value=f"<t:{timeout_ts}:F> (<t:{timeout_ts}:R>)", inline=False)
                await channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="🔊 رفع عقوبة الإسكات",
                    color=discord.Color.from_rgb(52, 152, 219),
                    timestamp=datetime.datetime.utcnow()
                )
                embed.add_field(name="👤 العضو", value=f"{after.mention} (`{after}`)", inline=False)
                await channel.send(embed=embed)

    # 6. الحظر (Ban)
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        channel_id = get_log_channel(guild.id)
        if not channel_id: return
        channel = guild.get_channel(channel_id)
        if not channel: return

        moderator = "مشرف غير معروف"
        reason = "لا يوجد سبب مدون"
        try:
            async for entry in guild.audit_logs(limit=5, action=discord.AuditLogAction.ban):
                if entry.target.id == user.id:
                    moderator = f"{entry.user.mention} (`{entry.user}`)"
                    reason = entry.reason or "لا يوجد سبب"
                    break
        except Exception:
            pass

        embed = discord.Embed(
            title="🔨 رصد عقوبة حظر (Ban)",
            color=discord.Color.from_rgb(155, 89, 182),
            timestamp=datetime.datetime.utcnow()
        )
        if user.avatar: embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="👤 المستخدم المحظور", value=f"{user.mention} (`{user}`)", inline=False)
        embed.add_field(name="🛠️ بواسطة المشرف", value=moderator, inline=False)
        embed.add_field(name="📌 السبب", value=reason, inline=False)
        await channel.send(embed=embed)

    # 7. إلغاء الحظر (Unban)
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        channel_id = get_log_channel(guild.id)
        if not channel_id: return
        channel = guild.get_channel(channel_id)
        if not channel: return

        embed = discord.Embed(
            title="🔓 إلغاء حظر (Unban)",
            color=discord.Color.from_rgb(26, 188, 156),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="👤 المستخدم", value=f"{user.mention} (`{user}`)", inline=False)
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logs(bot))

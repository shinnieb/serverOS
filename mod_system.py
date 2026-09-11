import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                date TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                note TEXT,
                date TEXT
            )
        """)
        conn.commit()
        conn.close()

    # --- 1. أمر إعطاء تحذير (إداري فقط) ---
    @app_commands.command(name="تحذير", description="[إداري] إعطاء تحذير رسمي لعضو وتسجيله في النظام")
    @app_commands.describe(عضو="العضو المراد تحذيره", السبب="سبب التحذير")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def warn_user(self, interaction: discord.Interaction, عضو: discord.Member, السبب: str):
        if عضو.bot:
            await interaction.response.send_message("❌ لا يمكنك تحذير بوت!", ephemeral=True)
            return

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO warnings (guild_id, user_id, moderator_id, reason, date)
            VALUES (?, ?, ?, ?, ?)
        """, (interaction.guild_id, عضو.id, interaction.user.id, السبب, current_date))
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?", (interaction.guild_id, عضو.id))
        warn_count = cursor.fetchone()[0]
        conn.close()

        try:
            dm_embed = discord.Embed(
                title="⚠️ تنبيه إداري رسمي",
                description=f"لقد تلقيت تحذيراً جديداً في سيرفر **{interaction.guild.name}**.\n\n📌 **السبب:** {السبب}\n📊 **إجمالي تحذيراتك:** `{warn_count}`",
                color=discord.Color.orange()
            )
            dm_embed.set_footer(text="ServerOS • Developed by i5z_w")
            await عضو.send(embed=dm_embed)
        except:
            pass

        embed = discord.Embed(
            title="⚠️ تم تحذير العضو بنجاح",
            description=f"👤 **العضو:** {عضو.mention}\n🛡️ **المشرف:** {interaction.user.mention}\n📌 **السبب:** `{السبب}`\n📊 **عدد التحذيرات الكلي:** `{warn_count}`",
            color=0x2b2d31
        )
        embed.set_footer(text="ServerOS • Developed by i5z_w")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- 2. أمر إضافة ملاحظة إدارية (إداري فقط) ---
    @app_commands.command(name="ملاحظة", description="[إداري] إضافة ملاحظة سرية على العضو خاصة بالإدارة")
    @app_commands.describe(عضو="العضو المراد إضافة ملاحظة له", الملاحظة="نص الملاحظة الإدارية")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def add_note(self, interaction: discord.Interaction, عضو: discord.Member, الملاحظة: str):
        if عضو.bot:
            await interaction.response.send_message("❌ لا يمكنك إضافة ملاحظة على بوت!", ephemeral=True)
            return

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO member_notes (guild_id, user_id, moderator_id, note, date)
            VALUES (?, ?, ?, ?, ?)
        """, (interaction.guild_id, عضو.id, interaction.user.id, الملاحظة, current_date))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="📝 تم تسجيل الملاحظة بنجاح",
            description=f"👤 **العضو:** {عضو.mention}\n🛡️ **المشرف:** {interaction.user.mention}\n📌 **الملاحظة:** `{الملاحظة}`",
            color=0x2b2d31
        )
        embed.set_footer(text="ServerOS • Developed by i5z_w")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- 3. سجل العضو (متاح للجميع وبرد سري مخفي عن الآخرين) ---
    @app_commands.command(name="سجل_العضو", description="استعراض السجل الشامل (التحذيرات والملاحظات)")
    @app_commands.describe(عضو="العضو المراد استعراض سجله (اتركه فارغاً لعرض سجلك الشخصي)")
    async def member_profile(self, interaction: discord.Interaction, عضو: discord.Member = None):
        target_member = عضو if عضو else interaction.user
        is_admin = interaction.user.guild_permissions.manage_guild
        
        if target_member.id != interaction.user.id and not is_admin:
            await interaction.response.send_message("❌ لا يمكنك استعراض سجل الأعضاء الآخرين!", ephemeral=True)
            return

        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, moderator_id, reason, date FROM warnings WHERE guild_id = ? AND user_id = ?", (interaction.guild_id, target_member.id))
        warnings_rows = cursor.fetchall()
        
        cursor.execute("SELECT id, moderator_id, note, date FROM member_notes WHERE guild_id = ? AND user_id = ?", (interaction.guild_id, target_member.id))
        notes_rows = cursor.fetchall()
        
        conn.close()

        warnings_text = ""
        if not warnings_rows:
            warnings_text = "✨ لا توجد تحذيرات مسجلة."
        else:
            for idx, (warn_id, mod_id, reason, date) in enumerate(warnings_rows, start=1):
                warnings_text += f"**{idx}.** {reason}\n ↳ التاريخ: `{date}`\n"

        notes_text = ""
        if not is_admin:
            notes_text = "🔒 الملاحظات الإدارية مخفية."
        else:
            if not notes_rows:
                notes_text = "✨ لا توجد ملاحظات إدارية."
            else:
                for idx, (note_id, mod_id, note, date) in enumerate(notes_rows, start=1):
                    mod = interaction.guild.get_member(mod_id)
                    mod_name = mod.mention if mod else f"مشرف"
                    notes_text += f"**{idx}.** (ID: `{note_id}`) {note}\n ↳ بواسطة: {mod_name} | `{date}`\n"

        embed = discord.Embed(
            title=f"📁 الملف الشامل للعضو: {target_member.display_name}",
            description=f"👤 **العضو:** {target_member.mention}\n",
            color=0x2b2d31
        )
        embed.add_field(name=f"⚠️ التحذيرات ({len(warnings_rows)})", value=warnings_text, inline=False)
        
        if is_admin:
            embed.add_field(name=f"📝 الملاحظات الإدارية ({len(notes_rows)})", value=notes_text, inline=False)
        
        embed.set_thumbnail(url=target_member.display_avatar.url)
        embed.set_footer(text="ServerOS • Developed by i5z_w")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- 4. تصفير التحذيرات (إداري فقط) ---
    @app_commands.command(name="مسح_تحذيرات", description="[إداري] مسح وإزالة جميع تحذيرات عضو معين")
    @app_commands.describe(عضو="العضو المراد تصفير سجله")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.checks.has_permissions(manage_guild=True)
    async def clear_warnings(self, interaction: discord.Interaction, عضو: discord.Member):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM warnings WHERE guild_id = ? AND user_id = ?", (interaction.guild_id, عضو.id))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="🧹 تم تصفير السجل",
            description=f"تمت إزالة جميع التحذيرات المسجلة بحق العضو {عضو.mention} بنجاح.",
            color=discord.Color.red()
        )
        embed.set_footer(text="ServerOS • Developed by i5z_w")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))

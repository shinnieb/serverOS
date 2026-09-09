import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

class AutoReplies(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auto_replies (
                guild_id INTEGER,
                trigger TEXT,
                response TEXT,
                should_mention INTEGER,
                PRIMARY KEY (guild_id, trigger)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deleted_replies (
                guild_id INTEGER,
                trigger TEXT,
                response TEXT,
                deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT response, should_mention FROM auto_replies WHERE guild_id = ? AND trigger = ?", (message.guild.id, message.content.strip()))
        row = cursor.fetchone()
        conn.close()

        if row:
            response, should_mention = row
            if should_mention == 1:
                await message.reply(response, mention_author=True)
            else:
                await message.channel.send(response)

    @app_commands.command(name="اضافة_رد", description="إضافة رد تلقائي جديد للكلمات")
    @app_commands.describe(
        trigger="الكلمة أو الجملة التي يكتبها العضو",
        response="رد البوت عليها",
        mention="هل تريد أن يمنشن البوت العضو في الرد؟"
    )
    @app_commands.choices(mention=[
        app_commands.Choice(name="نعم (يمنشن)", value=1),
        app_commands.Choice(name="لا (بدون منشن)", value=0)
    ])
    async def add_reply(self, interaction: discord.Interaction, trigger: str, response: str, mention: app_commands.Choice[int]):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO auto_replies (guild_id, trigger, response, should_mention)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id, trigger) DO UPDATE SET
                response = excluded.response,
                should_mention = excluded.should_mention
        """, (interaction.guild_id, trigger.strip(), response, mention.value))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="✅ تم إضافة الرد التلقائي",
            description=f"💬 **الكلمة:** `{trigger}`\n🗣️ **الرد:** {response}\n🔔 **المنشن:** {'مفعل' if mention.value == 1 else 'معطل'}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="حذف_رد", description="حذف رد تلقائي موجود")
    @app_commands.describe(trigger="الكلمة المراد حذف ردها")
    async def delete_reply(self, interaction: discord.Interaction, trigger: str):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT response FROM auto_replies WHERE guild_id = ? AND trigger = ?", (interaction.guild_id, trigger.strip()))
        row = cursor.fetchone()

        if row:
            cursor.execute("INSERT INTO deleted_replies (guild_id, trigger, response) VALUES (?, ?, ?)", (interaction.guild_id, trigger.strip(), row[0]))
            cursor.execute("DELETE FROM auto_replies WHERE guild_id = ? AND trigger = ?", (interaction.guild_id, trigger.strip()))
            conn.commit()
            conn.close()
            embed = discord.Embed(title="🗑️ تم حذف الرد", description=f"تم حذف الرد الخاص بكلمة: `{trigger}` بنجاح.", color=discord.Color.red())
        else:
            conn.close()
            embed = discord.Embed(title="❌ غير موجود", description=f"لم يتم العثور على رد تلقائي للكلمة: `{trigger}`", color=discord.Color.orange())

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="الردود_المحذوفة", description="عرض الأرشيف الخاص بالردود المحذوفة")
    async def show_deleted_replies(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT trigger, response, deleted_at FROM deleted_replies WHERE guild_id = ? ORDER BY deleted_at DESC LIMIT 10", (interaction.guild_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message("📜 لا يوجد ردود محذوفة في الأرشيف حالياً.", ephemeral=True)
            return

        description = ""
        for trigger, response, deleted_at in rows:
            description += f"• **الكلمة:** `{trigger}` | **الرد:** `{response}` | ⏱️ `{deleted_at}`\n"

        embed = discord.Embed(
            title="📜 أرشيف الردود المحذوفة (آخر 10)",
            description=description,
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AutoReplies(bot))
import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

class RepliesPaginator(discord.ui.View):
    def __init__(self, pages):
        super().__init__(timeout=180)
        self.pages = pages
        self.current_page = 0
        self.update_buttons()

    def update_buttons(self):
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1

    @discord.ui.button(label="السابق ◀", style=discord.ButtonStyle.blurple)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="التالي ▶", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

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

    @app_commands.command(name="اضافة_رد", description="[إداري] إضافة رد تلقائي جديد للكلمات في السيرفر")
    @app_commands.describe(
        trigger="الكلمة أو الجملة التي يكتبها العضو",
        response="رد البوت عليها",
        mention="هل تريد أن يمنشن البوت العضو في الرد؟"
    )
    @app_commands.choices(mention=[
        app_commands.Choice(name="نعم (يمنشن)", value=1),
        app_commands.Choice(name="لا (بدون منشن)", value=0)
    ])
    @app_commands.checks.has_permissions(manage_guild=True)
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
            title="✨ تم إضافة/تحديث الرد التلقائي بنجاح",
            description=f"💬 **الكلمة المُحفزة:** `{trigger}`\n🗣️ **رد البوت:** {response}\n🔔 **حالة المنشن:** `{'مفعل ✅' if mention.value == 1 else 'معطل ❌'}`",
            color=0x2b2d31
        )
        embed.set_footer(text="ServerOS Pro • Developed by i5z_w")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="حذف_رد", description="[إداري] حذف رد تلقائي موجود مسبقاً")
    @app_commands.describe(trigger="الكلمة المراد حذف ردها التلقائي")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def delete_reply(self, interaction: discord.Interaction, trigger: str):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT response FROM auto_replies WHERE guild_id = ? AND trigger = ?", (interaction.guild_id, trigger.strip()))
        row = cursor.fetchone()

        if row:
            cursor.execute("DELETE FROM auto_replies WHERE guild_id = ? AND trigger = ?", (interaction.guild_id, trigger.strip()))
            conn.commit()
            conn.close()
            
            embed = discord.Embed(
                title="🗑️ تم حذف الرد التلقائي", 
                description=f"تمت إزالة الرد الخاص بالكلمة: `{trigger}` من قاعدة البيانات بنجاح.", 
                color=discord.Color.red()
            )
        else:
            conn.close()
            embed = discord.Embed(
                title="❌ غير موجود", 
                description=f"لم يتم العثور على أي رد تلقائي مسجل للكلمة: `{trigger}`", 
                color=discord.Color.orange()
            )

        embed.set_footer(text="ServerOS Pro • Developed by i5z_w")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="عرض_الردود_المحفوظة", description="[إداري] عرض قائمة جميع الردود التلقائية المحفوظة في السيرفر عبر صفحة تفاعلية")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def show_saved_replies(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT trigger, response, should_mention FROM auto_replies WHERE guild_id = ?", (interaction.guild_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            embed = discord.Embed(
                title="📜 الردود التلقائية المحفوظة",
                description="عذراً، لا توجد أي ردود تلقائية مسجلة في هذا السيرفر حالياً.",
                color=discord.Color.orange()
            )
            embed.set_footer(text="ServerOS Pro • Developed by i5z_w")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # تقسيم الردود إلى صفحات (كل 5 ردود في صفحة لضمان شكل فخم ونظيف)
        items_per_page = 5
        chunks = [rows[i:i + items_per_page] for i in range(0, len(rows), items_per_page)]
        pages = []

        for index, chunk in enumerate(chunks, start=1):
            description = ""
            for idx, (trigger, response, should_mention) in enumerate(chunk, start=1):
                global_idx = (index - 1) * items_per_page + idx
                mention_status = "🔔 منشن مفعل" if should_mention == 1 else "🔕 بدون منشن"
                description += f"**{global_idx}.** الكلمة: `{trigger}`\n ↳ الرد: {response} (`{mention_status}`)\n\n"

            embed = discord.Embed(
                title="📜 قائمة الردود التلقائية المحفوظة",
                description=description,
                color=0x2b2d31
            )
            embed.set_footer(text=f"الصفحة {index} من {len(chunks)} • إجمالي الردود: {len(rows)} • Developed by i5z_w")
            pages.append(embed)

        view = RepliesPaginator(pages)
        # تم جعل الرسالة تظهر للجميع في الروم (ephemeral=False)
        await interaction.response.send_message(embed=pages[0], view=view, ephemeral=False)

async def setup(bot):
    await bot.add_cog(AutoReplies(bot))

import discord
from discord import app_commands
from discord.ext import commands
import sqlite3

class TicketModal(discord.ui.Modal, title="فتح تذكرة دعم جديدة"):
    reason = discord.ui.TextInput(
        label="ما هي مشكلتك أو استفسارك؟",
        style=discord.TextStyle.paragraph,
        placeholder="اكتب تفاصيل مشكلتك هنا بوضوح...",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "✅ تم استلام طلبك بنجاح! سيقوم فريق الإدارة بمراجعة مشكلتك والرد عليك قريباً عبر الرسائل الخاصة (DM).", 
            ephemeral=True
        )

        guild = interaction.guild
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("SELECT admin_channel_id FROM ticket_settings WHERE guild_id = ?", (guild.id,))
        row = cursor.fetchone()
        conn.close()

        if not row or not row[0]:
            return

        admin_channel = guild.get_channel(row[0])
        if admin_channel:
            embed = discord.Embed(
                title="🎫 تذكرة دعم جديدة واردة",
                description=f"**صاحب التذكرة:** {interaction.user.mention} (`{interaction.user.id}`)\n\n**المحتوى:**\n{self.reason.value}",
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"للرد على هذا العضو، استخدم أمر الرد المخصص أو اكتب في هذه الروم.")
            msg = await admin_channel.send(embed=embed)
            
            # حفظ ربط رسالة الإدارة بصاحب التذكرة في قاعدة البيانات للرد السهل
            conn = sqlite3.connect("serveros_pro.db")
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_tickets (
                    admin_msg_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    guild_id INTEGER
                )
            """)
            cursor.execute("INSERT OR REPLACE INTO active_tickets (admin_msg_id, user_id, guild_id) VALUES (?, ?, ?)", (msg.id, interaction.user.id, guild.id))
            conn.commit()
            conn.close()

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ticket_settings (
                guild_id INTEGER PRIMARY KEY,
                admin_channel_id INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_tickets (
                admin_msg_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                guild_id INTEGER
            )
        """)
        conn.commit()
        conn.close()

    @app_commands.command(name="تحديد_روم_الإدارة", description="[خاص بالإداريين] تحديد الروم السرية التي ستصل إليها تفاصيل التذاكر")
    @app_commands.describe(الروم="اختر الروم المخصصة لاستلام التذاكر")
    @app_commands.default_permissions(administrator=True)
    async def set_admin_channel(self, interaction: discord.Interaction, الروم: discord.TextChannel):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ticket_settings (guild_id, admin_channel_id) VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET admin_channel_id = ?
        """, (interaction.guild.id, الروم.id, الروم.id))
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"✅ تم تحديد روم الإدارة السرية بنجاح لتصبح: {الروم.mention}\n(تأكد من إعطاء صلاحيات رؤية هذه الروم للمشرفين فقط وإخفائها عن الأعضاء).", ephemeral=True)

    @app_commands.command(name="تذكرة", description="فتح تذكرة دعم جديدة وإرسالها للإدارة بسرية تامة")
    async def create_ticket(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("SELECT admin_channel_id FROM ticket_settings WHERE guild_id = ?", (interaction.guild.id,))
        row = cursor.fetchone()
        conn.close()

        if not row or not row[0]:
            await interaction.response.send_message("❌ عذراً، نظام التذاكر لم يتم إعداده في هذا السيرفر بعد من قبل الإدارة.", ephemeral=True)
            return

        await interaction.response.send_modal(TicketModal())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # إذا قام الإداري بالرد كـ Reply على رسالة التذكرة في روم الإدارة، يرسل البوت الرد للخاص للعضو
        if message.reference and message.reference.message_id:
            conn = sqlite3.connect("serveros_pro.db")
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM active_tickets WHERE admin_msg_id = ?", (message.reference.message_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                user_id = row[0]
                target_user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
                if target_user:
                    try:
                        embed = discord.Embed(
                            title="📩 رد من فريق الإدارة",
                            description=message.content,
                            color=discord.Color.green()
                        )
                        embed.set_footer(text=f"السيرفر: {message.guild.name}")
                        await target_user.send(embed=embed)
                        await message.add_reaction("✅")
                    except discord.Forbidden:
                        await message.channel.send(f"⚠️ تعذر إرسال الرد إلى {target_user.mention} لأن رسائله الخاصة (DM) مغلقة.")

async def setup(bot):
    await bot.add_cog(Tickets(bot))

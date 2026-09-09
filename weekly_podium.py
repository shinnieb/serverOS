import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3

class WeeklyPodium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()
        self.weekly_reward_task.start()

    def init_db(self):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        # جدول لتسجيل رسائل الأعضاء الأسبوعية
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_activity (
                guild_id INTEGER,
                user_id INTEGER,
                messages_count INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        # جدول لحفظ روم الإعلانات الخاص بكل سيرفر
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS server_settings (
                guild_id INTEGER PRIMARY KEY,
                podium_channel_id INTEGER
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
        cursor.execute("""
            INSERT INTO weekly_activity (guild_id, user_id, messages_count) VALUES (?, ?, 1)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET messages_count = messages_count + 1
        """, (message.guild.id, message.author.id))
        conn.commit()
        conn.close()

    @app_commands.command(name="تعيين_روم_التفاعل", description="تعيين الروم التي سيتم إرسال لوحة الشرف الأسبوعية فيها (للمشرفين فقط)")
    @app_commands.describe(channel="الروم المخصصة لإعلانات التفاعل")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_podium_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO server_settings (guild_id, podium_channel_id) VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET podium_channel_id = ?
        """, (interaction.guild_id, channel.id, channel.id))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="✅ تم التعيين بنجاح",
            description=f"تم تحديد {channel.mention} لتكون روم إعلانات أبطال التفاعل الأسبوعي!",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # مهمة تعمل كل أسبوع تلقائياً (168 ساعة = أسبوع كامل)
    @tasks.loop(hours=168)
    async def weekly_reward_task(self):
        await self.bot.wait_until_ready()

        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()

        # استخراج السيرفرات المسجلة
        cursor.execute("SELECT guild_id, podium_channel_id FROM server_settings")
        settings = cursor.fetchall()

        for guild_id, channel_id in settings:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue

            channel = guild.get_channel(channel_id)
            if not channel:
                continue

            # جلب أكثر 3 متفاعلين هذا الأسبوع
            cursor.execute("""
                SELECT user_id, messages_count FROM weekly_activity
                WHERE guild_id = ? ORDER BY messages_count DESC LIMIT 3
            """, (guild_id,))
            top_users = cursor.fetchall()

            if not top_users:
                continue

            description = "شكرًا لتفاعلكم الخرافي هذا الأسبوع! نار وشرار بالشات 🔥 وهنا أبطال التفاعل:\n\n"
            medals = ['👑', '🥈', '🥉']
            rewards = [500, 300, 150]  # مكافأة نقاط لكل مركز

            for index, (user_id, msgs) in enumerate(top_users):
                member = guild.get_member(user_id)
                mention = member.mention if member else f"مستخدم #{user_id}"
                medal = medals[index]
                reward = rewards[index]

                description += f"{medal} **المركز الـ {index+1}**: {mention} — `💬 {msgs} رسالة` (جائزة: 💰 {reward} نقطة)\n\n"

                # إضافة النقاط لمحفظة المستثمر تلقائياً
                cursor.execute("""
                    INSERT INTO user_wallet (guild_id, user_id, balance) VALUES (?, ?, 500)
                    ON CONFLICT(guild_id, user_id) DO UPDATE SET balance = balance + ?
                """, (guild_id, user_id, reward))

            embed = discord.Embed(
                title="🏆 احتفالية أبطال التفاعل الأسبوعي",
                description=description,
                color=discord.Color.gold()
            )
            embed.set_footer(text="تمت المكافأة وإعادة ضبط العداد للأسبوع القادم تلقائياً!")

            await channel.send(content="@everyone تهانينا للمبدعين!", embeds=[embed])

        # تصفير عداد الأسبوع لبدء منافسة جديدة نظيفة
        cursor.execute("DELETE FROM weekly_activity")
        conn.commit()
        conn.close()

    @weekly_reward_task.before_loop
    async def before_weekly_task(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(WeeklyPodium(bot))
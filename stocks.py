import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3
import random

class ServerStocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()
        self.pay_dividends.start()

    def init_db(self):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        # جدول أرصدة الأعضاء
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_wallet (
                guild_id INTEGER,
                user_id INTEGER,
                balance INTEGER DEFAULT 500,
                PRIMARY KEY (guild_id, user_id)
            )
        """)
        # جدول أسهم الرومات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS channel_stocks (
                guild_id INTEGER,
                channel_id INTEGER,
                share_price INTEGER DEFAULT 100,
                messages_count INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, channel_id)
            )
        """)
        # جدول محفظة أسهم الأعضاء
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_shares (
                guild_id INTEGER,
                user_id INTEGER,
                channel_id INTEGER,
                shares_amount INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id, channel_id)
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

        # 1. إعطاء نقاط لكل رسالة (10 نقاط) + تسجيل حساب جديد إذا مو موجود
        cursor.execute("""
            INSERT INTO user_wallet (guild_id, user_id, balance) VALUES (?, ?, 500)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET balance = balance + 10
        """, (message.guild.id, message.author.id))

        # 2. تحديث عداد الرسائل للروم في سوق الأسهم
        cursor.execute("""
            INSERT INTO channel_stocks (guild_id, channel_id, share_price, messages_count) VALUES (?, ?, 100, 1)
            ON CONFLICT(guild_id, channel_id) DO UPDATE SET messages_count = messages_count + 1
        """, (message.guild.id, message.channel.id))

        conn.commit()
        conn.close()

    @app_commands.command(name="رصيدي", description="عرض رصيدك الحالي من النقاط")
    async def balance(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM user_wallet WHERE guild_id = ? AND user_id = ?", (interaction.guild_id, interaction.user.id))
        row = cursor.fetchone()
        conn.close()

        bal = row[0] if row else 500
        embed = discord.Embed(title="💰 محفظتك المالية", description=f"رصيدك الحالي هو: **{bal} نقطة**", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="سوق_الأسهم", description="عرض رومات السيرفر وأسعار الأسهم فيها")
    async def stock_market(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT channel_id, share_price, messages_count FROM channel_stocks WHERE guild_id = ?", (interaction.guild_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message("📈 لا توجد رومات مسجلة في سوق الأسهم حتى الآن. ابدأوا بالسوالف في الرومات!", ephemeral=True)
            return

        description = ""
        for ch_id, price, msgs in rows:
            channel = interaction.guild.get_channel(ch_id)
            ch_name = channel.mention if channel else "روم محذوف"
            description += f"📌 {ch_name} | سعر السهم: `💰 {price} نقطة` | التفاعل: `💬 {msgs} رسالة`\n"

        embed = discord.Embed(title="📈 سوق أسهم السيرفر", description=description, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="شراء_سهم", description="شراء أسهم في روم معينة لاستلام أرباح")
    @app_commands.describe(channel="الروم المراد شراء أسهم فيها", amount="عدد الأسهم المراد شراؤها")
    async def buy_stock(self, interaction: discord.Interaction, channel: discord.TextChannel, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ يرجى تحديد عدد صحيح أكبر من صفر.", ephemeral=True)
            return

        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()

        # التأكد من وجود سهم للروم
        cursor.execute("SELECT share_price FROM channel_stocks WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, channel.id))
        row = cursor.fetchone()
        if not row:
            conn.close()
            await interaction.response.send_message("❌ هذه الروم غير مسجلة في السوق بعد، دع الأعضاء يسولفون فيها أولاً!", ephemeral=True)
            return

        price_per_share = row[0]
        total_cost = price_per_share * amount

        # فحص رصيد المستخدم
        cursor.execute("SELECT balance FROM user_wallet WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id))
        user_row = cursor.fetchone()
        user_balance = user_row[0] if user_row else 500

        if user_balance < total_cost:
            conn.close()
            await interaction.response.send_message(f"❌ رصيدك غير كافي! تحتاج إلى **{total_cost} نقطة** وشراء {amount} سهم.", ephemeral=True)
            return

        # خصم الرصيد وتسجيل الأسهم
        cursor.execute("UPDATE user_wallet SET balance = balance - ? WHERE guild_id = ? AND user_id = ?", (total_cost, interaction.guild.id, interaction.user.id))
        cursor.execute("""
            INSERT INTO user_shares (guild_id, user_id, channel_id, shares_amount) VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id, user_id, channel_id) DO UPDATE SET shares_amount = shares_amount + ?
        """, (interaction.guild.id, interaction.user.id, channel.id, amount, amount))

        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="✅ تمت عملية الشراء بنجاح",
            description=f"لقد اشتريت **{amount} سهم** في الروم {channel.mention}\nتكلفة الشراء الإجمالية: **{total_cost} نقطة**",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="المستثمرين", description="عرض قائمة أغنى المستثمرين في السيرفر")
    async def top_investors(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, balance FROM user_wallet WHERE guild_id = ? ORDER BY balance DESC LIMIT 5", (interaction.guild.id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message("🏆 لا يوجد مستثمرين حتى الآن.", ephemeral=True)
            return

        description = ""
        for index, (user_id, balance) in enumerate(rows, start=1):
            member = interaction.guild.get_member(user_id)
            name = member.mention if member else f"مستخدم #{user_id}"
            medal = "👑" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else "🔹"
            description += f"{medal} **#{index}** {name} — الرصيد: `💰 {balance} نقطة`\n"

        embed = discord.Embed(title="🏆 قائمة كبار المستثمرين بالسيرفر", description=description, color=discord.Color.purple())
        await interaction.response.send_message(embed=embed)

    @tasks.loop(minutes=30)
    async def pay_dividends(self):
        # مهمة تلقائية كل 30 دقيقة: ترتفع أسعار الأسهم وتوزع أرباح بناءً على تفاعل الرومات
        conn = sqlite3.connect("serveros.db")
        cursor = conn.cursor()
        cursor.execute("SELECT guild_id, channel_id, messages_count FROM channel_stocks")
        channels = cursor.fetchall()

        for guild_id, channel_id, msgs in channels:
            # تعديل سعر السهم بناءً على عدد الرسائل الجديدة
            new_price = max(50, 100 + (msgs * 5))
            cursor.execute("UPDATE channel_stocks SET share_price = ?, messages_count = 0 WHERE guild_id = ? AND channel_id = ?", (new_price, guild_id, channel_id))

            # توزيع أرباح لمن يملك أسهم في هذه الروم
            cursor.execute("SELECT user_id, shares_amount FROM user_shares WHERE guild_id = ? AND channel_id = ?", (guild_id, channel_id))
            holders = cursor.fetchall()
            for user_id, shares in holders:
                profit = shares * int(new_price * 0.1)  # ربح 10% من قيمة السهم للمستثمر
                cursor.execute("UPDATE user_wallet SET balance = balance + ? WHERE guild_id = ? AND user_id = ?", (profit, guild_id, user_id))

        conn.commit()
        conn.close()

    @pay_dividends.before_loop
    async def before_dividends(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ServerStocks(bot))
import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3
import datetime

class ServerStocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()
        self.pay_dividends.start()

    def init_db(self):
        conn = sqlite3.connect("serveros_pro.db")
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

        # جدول تتبع جوائز الأسبوع للمستثمرين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weekly_stats (
                guild_id INTEGER,
                user_id INTEGER,
                weekly_score INTEGER DEFAULT 0,
                last_reset TIMESTAMP,
                PRIMARY KEY (guild_id, user_id)
            )
        """)

        # جدول إعدادات رتب السوق لكل سيرفر
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_roles (
                guild_id INTEGER PRIMARY KEY,
                investor_role_id INTEGER,
                top3_role_id INTEGER,
                king_role_id INTEGER
            )
        """)
        
        conn.commit()
        conn.close()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()

        # 1. إعطاء نقاط تفاعل ورصيد لكل رسالة (10 نقاط) وتأكيد الحفظ
        cursor.execute("""
            INSERT INTO user_wallet (guild_id, user_id, balance) VALUES (?, ?, 500)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET balance = balance + 10
        """, (message.guild.id, message.author.id))

        # 2. تحديث عداد الرسائل للروم في سوق الأسهم
        cursor.execute("""
            INSERT INTO channel_stocks (guild_id, channel_id, share_price, messages_count) VALUES (?, ?, 100, 1)
            ON CONFLICT(guild_id, channel_id) DO UPDATE SET messages_count = messages_count + 1
        """, (message.guild.id, message.channel.id))

        # 3. تحديث النقاط الأسبوعية للمتفاعل
        cursor.execute("""
            INSERT INTO weekly_stats (guild_id, user_id, weekly_score, last_reset) VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET weekly_score = weekly_score + 1
        """, (message.guild.id, message.author.id))

        # 4. منح رتبة "مستثمر" العامة تلقائياً لمن يرسل رسالة
        cursor.execute("SELECT investor_role_id FROM market_roles WHERE guild_id = ?", (message.guild.id,))
        role_row = cursor.fetchone()
        
        conn.commit()
        conn.close()

        if role_row and role_row[0]:
            role = message.guild.get_role(role_row[0])
            if role and role not in message.author.roles:
                try:
                    await message.author.add_roles(role, reason="التفاعل في السيرفر والحصول على رتبة مستثمر")
                except Exception:
                    pass

    @app_commands.command(name="رصيدي", description="عرض رصيدك الحالي من النقاط في الخزينة الملكية")
    async def balance(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM user_wallet WHERE guild_id = ? AND user_id = ?", (interaction.guild_id, interaction.user.id))
        row = cursor.fetchone()
        conn.close()

        bal = row[0] if row else 500
        embed = discord.Embed(
            title="💰 الخزينة المالية الشخصية", 
            description=f"رصيدك الحالي المتاح للاستثمار:\n# 💎 `{bal:,} نقطة`", 
            color=0x2ECC71
        )
        embed.set_footer(text=f"بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="سوق_الأسهم", description="استعراض أسعار أسهم رومات السيرفر ونشاطها")
    async def stock_market(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("SELECT channel_id, share_price, messages_count FROM channel_stocks WHERE guild_id = ?", (interaction.guild_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message("📈 لا توجد رومات مسجلة في سوق الأسهم حتى الآن. ابدأوا بالتفاعل في الرومات!", ephemeral=True)
            return

        description = "إليك قائمة الرومات المتاحة للاستثمار وتداول الأسهم:\n\n"
        for ch_id, price, msgs in rows:
            channel = interaction.guild.get_channel(ch_id)
            ch_name = channel.mention if channel else "روم غير معروف"
            description += f"📌 {ch_name}\n └ السعر: `💰 {price:,}` | التفاعل: `💬 {msgs} رسالة`\n\n"

        embed = discord.Embed(title="📈 بورصة وسوق أسهم السيرفر", description=description, color=0x3498DB)
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="شراء_سهم", description="شراء أسهم استثمارية في روم معينة لتحقيق أرباح")
    @app_commands.describe(channel="الروم المراد شراء أسهم فيها", amount="عدد الأسهم المراد شراؤها")
    async def buy_stock(self, interaction: discord.Interaction, channel: discord.TextChannel, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ عذراً، يجب تحديد عدد أسهم أكبر من الصفر.", ephemeral=True)
            return

        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()

        cursor.execute("SELECT share_price FROM channel_stocks WHERE guild_id = ? AND channel_id = ?", (interaction.guild.id, channel.id))
        row = cursor.fetchone()
        if not row:
            conn.close()
            await interaction.response.send_message("❌ هذه الروم غير مدرجة في السوق بعد، دع الأعضاء يتفاعلون فيها أولاً!", ephemeral=True)
            return

        price_per_share = row[0]
        total_cost = price_per_share * amount

        cursor.execute("SELECT balance FROM user_wallet WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, interaction.user.id))
        user_row = cursor.fetchone()
        user_balance = user_row[0] if user_row else 500

        if user_balance < total_cost:
            conn.close()
            await interaction.response.send_message(f"❌ رصيدك غير كافي! تكلفة شراء {amount} سهم هي **{total_cost:,} نقطة** بينما رصيدك **{user_balance:,} نقطة**.", ephemeral=True)
            return

        cursor.execute("UPDATE user_wallet SET balance = balance - ? WHERE guild_id = ? AND user_id = ?", (total_cost, interaction.guild.id, interaction.user.id))
        cursor.execute("""
            INSERT INTO user_shares (guild_id, user_id, channel_id, shares_amount) VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id, user_id, channel_id) DO UPDATE SET shares_amount = shares_amount + ?
        """, (interaction.guild.id, interaction.user.id, channel.id, amount, amount))

        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="✅ تمت عملية الاستثمار بنجاح",
            description=f"لقد اشتريت **{amount:,} سهم** في الروم {channel.mention}\nإجمالي التكلفة المدفوعة: `💰 {total_cost:,} نقطة`",
            color=0xF1C40F
        )
        embed.set_footer(text=f"بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="المستثمرين", description="عرض قائمة أثرياء وكبار المستثمرين في السيرفر")
    async def top_investors(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, balance FROM user_wallet WHERE guild_id = ? ORDER BY balance DESC LIMIT 5", (interaction.guild.id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message("🏆 لا يوجد مستثمرين مسجلين حتى الآن.", ephemeral=True)
            return

        description = ""
        for index, (user_id, balance) in enumerate(rows, start=1):
            member = interaction.guild.get_member(user_id)
            name = member.display_name if member else f"مستخدم #{user_id}"
            medal = "👑" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else "🔹"
            description += f"{medal} ** المركز #{index}** | **{name}** — الرصيد: `💰 {balance:,} نقطة`\n"

        embed = discord.Embed(title="🏆 قائمة أثرياء وكبار المستثمرين", description=description, color=0x9B59B6)
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="مستثمرين_الاسبوع", description="عرض أكثر الأعضاء تفاعلاً واستثماراً لهذا الأسبوع")
    async def weekly_top_investors(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, weekly_score FROM weekly_stats WHERE guild_id = ? ORDER BY weekly_score DESC LIMIT 5", (interaction.guild.id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await interaction.response.send_message("⭐ لا توجد إحصائيات أسبوعية مسجلة حتى الآن.", ephemeral=True)
            return

        description = "أبرز الشخصيات النشطة في السيرفر لهذا الأسبوع:\n\n"
        for index, (user_id, score) in enumerate(rows, start=1):
            member = interaction.guild.get_member(user_id)
            name = member.display_name if member else f"مستخدم #{user_id}"
            medal = "🔥" if index == 1 else "⭐" if index == 2 else "✨" if index == 3 else "🔹"
            description += f"{medal} **#{index}** | **{name}** — التفاعل: `{score:,} نقطة نشاط`\n"

        embed = discord.Embed(title="🌟 أساطير التفاعل والاستثمار الأسبوعي", description=description, color=0xE67E22)
        embed.set_footer(text=f"تتحدث الإحصائيات أسبوعياً تلقائياً | طلب: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="إعداد_رتب_السوق", description="[خاص بالإداريين] تحديد رتب المستثمرين والرتب الخاصة بأوائل الأثرياء والسيرفر")
    @app_commands.describe(
        رتبة_مستثمر="الرتبة العامة التي تُمنح لأي شخص يتفاعل",
        رتبة_مستثمر_كبير="رتبة كبار المستثمرين (لأكبر 3 أرصدة بالسيرفر)",
        رتبة_ملك_المستثمرين="رتبة ملك المستثمرين (لصاحب المركز الأول والمركز المالي الأعلى)"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def set_market_roles(self, interaction: discord.Interaction, رتبة_مستثمر: discord.Role = None, رتبة_مستثمر_كبير: discord.Role = None, رتبة_ملك_المستثمرين: discord.Role = None):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT investor_role_id, top3_role_id, king_role_id FROM market_roles WHERE guild_id = ?", (interaction.guild.id,))
        existing = cursor.fetchone()

        inv_id = رتبة_مستثمر.id if رتبة_مستثمر else (existing[0] if existing else None)
        top3_id = رتبة_مستثمر_كبير.id if رتبة_مستثمر_كبير else (existing[1] if existing else None)
        king_id = رتبة_ملك_المستثمرين.id if رتبة_ملك_المستثمرين else (existing[2] if existing else None)

        cursor.execute("""
            INSERT INTO market_roles (guild_id, investor_role_id, top3_role_id, king_role_id) VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET investor_role_id = ?, top3_role_id = ?, king_role_id = ?
        """, (interaction.guild.id, inv_id, top3_id, king_id, inv_id, top3_id, king_id))

        conn.commit()
        conn.close()

        # تحديث فوري للرتب عند حفظ الإعدادات لتطبيقها مباشرة على الأثرياء الحاليين
        await self.update_wealth_roles(interaction.guild)

        embed = discord.Embed(
            title="⚙️ إعدادات رتب السوق والتمويل",
            description="✅ تم حفظ وتطبيق رتب السوق بنجاح:\n\n"
                        f"• رتبة المتفاعل العادي: {رتبة_مستثمر.mention if رتبة_مستثمر else 'لم تُتغير'}\n"
                        f"• رتبة كبار المستثمرين (Top 3): {رتبة_مستثمر_كبير.mention if رتبة_مستثمر_كبير else 'لم تُتغير'}\n"
                        f"• رتبة ملك المستثمرين (#1): {رتبة_ملك_المستثمرين.mention if رتبة_ملك_المستثمرين else 'لم تُتغير'}",
            color=0x2ECC71
        )
        embed.set_footer(text=f"بإشراف الإداري: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @set_market_roles.error
    async def set_market_roles_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ عذراً، هذا الأمر مخصص حصرياً للمشرفين والإداريين فقط.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ حدث خطأ أثناء تنفيذ الأمر الإداري.", ephemeral=True)

    @app_commands.command(name="إدارة_السوق", description="[خاص بالإداريين] تصفير وتحديث إحصائيات السوق الأسبوعية")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def reset_market(self, interaction: discord.Interaction):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM weekly_stats WHERE guild_id = ?", (interaction.guild.id,))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="⚙️ لوحة التحكم الإدارية",
            description="✅ تم بنجاح تصفير سجلات التفاعل الأسبوعي وبدء دورة أسبوعية جديدة للمستثمرين.",
            color=0xE74C3C
        )
        embed.set_footer(text=f"بإشراف الإداري: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, ephemeral=True, allowed_mentions=discord.AllowedMentions.none())

    @reset_market.error
    async def reset_market_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ عذراً، هذا الأمر مخصص حصرياً للمشرفين والإداريين فقط.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ حدث خطأ أثناء تنفيذ الأمر الإداري.", ephemeral=True)

    async def update_wealth_roles(self, guild: discord.Guild):
        """دالة مسؤولة عن منح وسحب رتب الثروة (الملك وكبار المستثمرين) بناءً على الأرصدة الحالية بدقة"""
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("SELECT top3_role_id, king_role_id FROM market_roles WHERE guild_id = ?", (guild.id,))
        role_row = cursor.fetchone()
        conn.close()

        if not role_row:
            return

        top3_role_id, king_role_id = role_row
        top3_role = guild.get_role(top3_role_id) if top3_role_id else None
        king_role = guild.get_role(king_role_id) if king_role_id else None

        # سحب الرتب القديمة أولاً لتحديثها نظيفة
        if top3_role:
            for member in top3_role.members:
                try:
                    await member.remove_roles(top3_role)
                except Exception:
                    pass
        if king_role:
            for member in king_role.members:
                try:
                    await member.remove_roles(king_role)
                except Exception:
                    pass

        # جلب أكبر 3 أعضاء أصحاب أرصدة مالية في المحفظة
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM user_wallet WHERE guild_id = ? ORDER BY balance DESC LIMIT 3", (guild.id,))
        top_wealth = cursor.fetchall()
        conn.close()

        for index, (uid,) in enumerate(top_wealth):
            member = guild.get_member(uid)
            if not member:
                continue
            
            # المركز الأول (أكبر رصيد مثل 100 ألف وأكثر) يصبح ملك المستثمرين
            if index == 0 and king_role:
                try:
                    await member.add_roles(king_role, reason="الحصول على أعلى رصيد مالي وتصدر ملك المستثمرين")
                except Exception:
                    pass
            
            # أول 3 أثرياء يحصلون على رتبة كبار المستثمرين
            if top3_role:
                try:
                    await member.add_roles(top3_role, reason="التواجد ضمن قائمة أكبر 3 مستثمرين وأثرياء السيرفر")
                except Exception:
                    pass

    @tasks.loop(hours=168)
    async def pay_dividends(self):
        conn = sqlite3.connect("serveros_pro.db")
        cursor = conn.cursor()
        
        # 1. تحديث أسعار الأسهم وأرباح الرومات وتوزيع الأرباح على المحافظ
        cursor.execute("SELECT guild_id, channel_id, messages_count FROM channel_stocks")
        channels = cursor.fetchall()

        for guild_id, channel_id, msgs in channels:
            new_price = max(50, 100 + (msgs * 2))
            cursor.execute("UPDATE channel_stocks SET share_price = ?, messages_count = 0 WHERE guild_id = ? AND channel_id = ?", (new_price, guild_id, channel_id))

            cursor.execute("SELECT user_id, shares_amount FROM user_shares WHERE guild_id = ? AND channel_id = ?", (guild_id, channel_id))
            holders = cursor.fetchall()
            for user_id, shares in holders:
                profit = shares * int(new_price * 0.15)
                cursor.execute("UPDATE user_wallet SET balance = balance + ? WHERE guild_id = ? AND user_id = ?", (profit, guild_id, user_id))

        # تصفير النشاط الأسبوعي
        cursor.execute("DELETE FROM weekly_stats")
        conn.commit()
        conn.close()

        # تحديث رتب الثروة لجميع السيرفرات تلقائياً مع الأرباح الجديدة
        for guild in self.bot.guilds:
            await self.update_wealth_roles(guild)

    @pay_dividends.before_loop
    async def before_dividends(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ServerStocks(bot))

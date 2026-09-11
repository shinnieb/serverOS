import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class MatchView(discord.ui.View):
    def __init__(self, p1: str, p2: str, match_title: str, timeout_seconds: float):
        super().__init__(timeout=timeout_seconds)
        self.p1 = p1
        self.p2 = p2
        self.winner = None

    @discord.ui.button(label="", style=discord.ButtonStyle.success, emoji="⚔️")
    async def vote_p1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.winner = self.p1
        await self.finish_vote(interaction)

    @discord.ui.button(label="", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def vote_p2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.winner = self.p2
        await self.finish_vote(interaction)

    async def finish_vote(self, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
        
        embed = interaction.message.embeds[0]
        embed.color = 0x2ECC71
        embed.add_field(name="🏆 النتيجة النهائية وتأهل البطل:", value=f"انتهت المعركة بتأهل: **{self.winner}** بنجاح واستحقاق!", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        try:
            pass
        except:
            pass

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="8ball", description="البلورة الذكية للإجابة على الأسئلة العامة وأسئلة السيرفر")
    @app_commands.describe(question="اكتب سؤالك (مثلاً: من مالك السيرفر؟ هل بفوز؟)")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        q_lower = question.lower()
        
        if "مالك" in q_lower or "صاحب" in q_lower or "مين مؤسس" in q_lower:
            answer = f"مالك السيرفر والقائد الأعلى هو صاحب الرؤية هنا ({interaction.guild.owner.name if interaction.guild else 'غير معروف'})!"
        elif "انا" in q_lower and ("احب" in q_lower or "كفو" in q_lower):
            answer = "طبعاً، أنت من أساطير هذا السيرفر ولا شك في ذلك!"
        elif "بفوز" in q_lower or "بفوز بالمسابقة" in q_lower:
            answer = "الفرصة أمامك مواتية، لكن الحظ يحتاج إلى شوية تركيز!"
        else:
            responses = [
                "✨ بناءً على المعطيات الحالية، الإجابة هي: نعم وبقوة.",
                "🌟 الأمور تميل لصالح هذا الخيار، توكل على الله.",
                "⏳ الصورة غير واضحة تماماً، لكن المؤشرات إيجابية.",
                "⚠️ الحذر مطلوب، الظروف قد تتغير في أي لحظة.",
                "❌ للأسف، التوقعات تشير إلى عكس ذلك تماماً."
            ]
            answer = random.choice(responses)
        
        embed = discord.Embed(title="🔮 البلورة الذكية", color=0x2b2d31)
        embed.add_field(name="📌 سؤالك:", value=f"> {question}", inline=False)
        embed.add_field(name="💡 الرد المنطقي:", value=f"```ansi\n\u001b[0;32m{answer}\u001b[0m\n```", inline=False)
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="coinflip", description="رمي عملة ملكية ذهبية لاختيار الحظ (ملك أم كتابة)")
    async def coinflip(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)
        await asyncio.sleep(1)
        
        result = random.choice(["الملك 👑 (Head)", "الكتابة 🦅 (Tail)"])
        color = 0xFFD700 if "الملك" in result else 0xC0C0C0
        
        embed = discord.Embed(title="🪙 ساحة العملة الملكية", description=f"دارت العملة في الهواء واستقرت لتعلن عن النتيجة:\n\n# ⚡ **{result}**", color=color)
        embed.set_footer(text=f"بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.followup.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="roll", description="رمي النرد الفاخر لاختبار الحظ العشوائي")
    @app_commands.describe(max_num="الحد الأعلى لرقم النرد (الافتراضي 6)")
    async def roll(self, interaction: discord.Interaction, max_num: int = 6):
        if max_num < 1:
            await interaction.response.send_message("❌ عذراً، يجب أن يكون النرد أكبر من الصفر.", ephemeral=True)
            return
            
        result = random.randint(1, max_num)
        
        embed = discord.Embed(title="🎲 النرد الفاخر", description=f"تم اهتزاز النرد في الساحة الملكية واستقر الرقم على:\n\n# 🎲 `{result}` \n*(من أصل {max_num} وجه)*", color=0x5865F2)
        embed.set_footer(text=f"حظ سعيد، {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="ship", description="مقياس التوافق والانسجام الراقي بين شخصين")
    @app_commands.describe(user1="الشخص الأول", user2="الشخص الثاني (اختياري)")
    async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member = None):
        user2 = user2 or interaction.user
        
        if user1.id == user2.id:
            percentage = 100
        else:
            percentage = (user1.id + user2.id) % 101
            
        filled_blocks = int(percentage / 10)
        progress_bar = "🟩" * filled_blocks + "⬛" * (10 - filled_blocks)

        if percentage > 85:
            status = "🔥 توافق أسطوري وخارق!"
        elif percentage > 60:
            status = "⭐ انسجام وتناغم جميل جداً"
        elif percentage > 30:
            status = "💫 علاقة مقبولة وتحتاج بعض الجهد"
        else:
            status = "❄️ تباعد قطبي وبارد جداً!"

        embed = discord.Embed(title="❤️ مقياس التوافق الملكي", color=0xFF69B4)
        embed.add_field(name="🔗 الأطراف المعنية:", value=f"• **{user1.display_name}**\n• **{user2.display_name}**", inline=False)
        embed.add_field(name="📊 نسبة الانسجام:", value=f"**{percentage}%**\n{progress_bar}\n*{status}*", inline=False)
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="avatar", description="استعراض الصورة الشخصية بدقة فائقة وبشكل فخم")
    @app_commands.describe(member="العضو المراد استعراض صورته الشخصية")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        avatar_url = member.display_avatar.url
        
        embed = discord.Embed(title=f"🖼️ الملف الشخصي لـ: {member.display_name}", color=0x3498DB)
        embed.set_image(url=avatar_url)
        embed.add_field(name="🔗 روابط التحميل السريع:", value=f"[عرض الصورة بالحجم الكامل]({avatar_url})", inline=False)
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="match", description="[خاص بالإداريين] إنشاء مواجهة رسمية مع تحديد وقت التصويت بالساعات")
    @app_commands.describe(
        member1="الطرف الأول (اسم أو فريق)", 
        member2="الطرف الثاني (اسم أو فريق)", 
        hours="مدة التصويت بالساعات (مثال: 1 يعني ساعة، 24 يعني يوم كامل)", 
        round_title="اسم الجولة أو المسابقة"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def match(self, interaction: discord.Interaction, member1: str, member2: str, hours: float = 1.0, round_title: str = "مواجهة الإقصاء الكبرى"):
        timeout_seconds = hours * 3600
        view = MatchView(member1, member2, round_title, timeout_seconds)
        view.children[0].label = member1
        view.children[1].label = member2

        embed = discord.Embed(title=f"⚔️ حلبة التحدي والتصفيات | {round_title}", description=f"معركة حامية الوطيس! باب التصويت مفتوح لجميع الحضور. اختر الفائز من الأزرار بالأسفل:\n⏱️ **مدة التصويت المحددة:** {hours} ساعة!", color=0xF1C40F)
        embed.add_field(name="🏟️ أطراف المواجهة:", value=f"🟢 **{member1}**\n*ضد*\n🔴 **{member2}**", inline=False)
        embed.set_footer(text=f"بإشراف: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, view=view, allowed_mentions=discord.AllowedMentions.none())

    @match.error
    async def match_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ عذراً، هذا الأمر مخصص فقط للمشرفين ومن يمتلكون صلاحية إسكات الأعضاء (Timeout)!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ حدث خطأ ما أثناء تنفيذ الأمر.", ephemeral=True)

    @app_commands.command(name="bracket", description="[خاص بالإداريين] عرض جدول وتنسيق بطولة التصفيات المتعددة")
    @app_commands.describe(m1_t1="مباراة 1 - الطرف الأول", m1_t2="مباراة 1 - الطرف الثاني", m2_t1="مباراة 2 - الطرف الأول", m2_t2="مباراة 2 - الطرف الثاني")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def bracket(self, interaction: discord.Interaction, m1_t1: str, m1_t2: str, m2_t1: str, m2_t2: str):
        embed = discord.Embed(title="🏆 جدول وشجرة البطولات الرسمية", description="هذه مواجهات الدور الحالي، استخدم أمر `/match` لكل مباراة لبدء التصويت وحسم المتأهلين!", color=0x9B59B6)
        
        embed.add_field(name="🔹 اللقاء الأول:", value=f"• **{m1_t1}**  VS  **{m1_t2}**", inline=False)
        embed.add_field(name="🔸 اللقاء الثاني:", value=f"• **{m2_t1}**  VS  **{m2_t2}**", inline=False)
        embed.set_footer(text=f"إدارة البطولة بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @bracket.error
    async def bracket_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ عذراً، هذا الأمر مخصص فقط للمشرفين ومن يمتلكون صلاحية إسكات الأعضاء (Timeout)!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ حدث خطأ ما أثناء تنفيذ الأمر.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Fun(bot))

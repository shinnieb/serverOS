import discord
from discord.ext import commands
from discord import app_commands
import random

class MatchView(discord.ui.View):
    def __init__(self, p1: str, p2: str, match_title: str):
        super().__init__(timeout=300)
        self.p1 = p1
        self.p2 = p2
        self.winner = None

    @discord.ui.button(label="الفريق 1", style=discord.ButtonStyle.success, emoji="⚔️")
    async def vote_p1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.winner = self.p1
        await self.finish_vote(interaction)

    @discord.ui.button(label="الفريق 2", style=discord.ButtonStyle.danger, emoji="⚔️")
    async def vote_p2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.winner = self.p2
        await self.finish_vote(interaction)

    async def finish_vote(self, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
        
        embed = interaction.message.embeds[0]
        embed.color = 0x2ECC71
        embed.add_field(name="🏆 حسم المواجهة والتأهل:", value=f"انتهت اللقاء بتأهل: **{self.winner}** بجدارة!", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self)
        self.stop()

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="8ball", description="[VIP] البلورة الذكية للإجابة على الأسئلة العامة وأسئلة السيرفر")
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
        
        embed = discord.Embed(title="🔮 البلورة الذكية | 8Ball", color=0x2b2d31)
        embed.add_field(name="📌 سؤالك:", value=f"> {question}", inline=False)
        embed.add_field(name="💡 الرد المنطقي:", value=f"```ansi\n\u001b[0;32m{answer}\u001b[0m\n```", inline=False)
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="coinflip", description="[VIP] رمي عملة ملكية ذهبية (ملك أم كتابة)")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["الملك 👑 (Head)", "الكتابة 🦅 (Tail)"])
        color = 0xFFD700 if "الملك" in result else 0xC0C0C0
        
        embed = discord.Embed(title="🪙 ساحة العملة الملكية", description=f"استقرت العملة بسلام، وكانت النتيجة:\n\n### ⚡ **{result}**", color=color)
        embed.set_footer(text=f"بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="roll", description="[VIP] رمي النرد الفاخر لاختبار الحظ العشوائي")
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

    @app_commands.command(name="ship", description="[VIP] مقياس التوافق والانسجام الراقي بين شخصين")
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

        embed = discord.Embed(title="❤️ مقياس التوافق الملكي (VIP Ship)", color=0xFF69B4)
        embed.add_field(name="🔗 الأطراف المعنية:", value=f"• **{user1.display_name}**\n• **{user2.display_name}**", inline=False)
        embed.add_field(name="📊 نسبة الانسجام:", value=f"**{percentage}%**\n{progress_bar}\n*{status}*", inline=False)
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="avatar", description="[VIP] استعراض الصورة الشخصية بدقة فائقة وبشكل فخم")
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

    @app_commands.command(name="match", description="[VIP] إنشاء مواجهة فردية بين طرفين بنظام التصفيات")
    @app_commands.describe(name1="اسم الطرف الأول (مثلاً: ريال مدريد / مشرف 1)", name2="اسم الطرف الثاني (مثلاً: برشلونة / مشرف 2)", round_title="اسم الجولة أو المسابقة")
    async def match(self, interaction: discord.Interaction, name1: str, name2: str, round_title: str = "مواجهة الإقصاء"):
        view = MatchView(name1, name2, round_title)
        view.children[0].label = name1
        view.children[1].label = name2

        embed = discord.Embed(title=f"⚔️ جدول التصفيات | {round_title}", description="اختر الفريق أو الطرف الفائز في هذه المواجهة عبر الأزرار بالأسفل:", color=0xF1C40F)
        embed.add_field(name="🏟️ طرفي اللقاء:", value=f"🟢 **{name1}**\n*ضد*\n🔴 **{name2}**", inline=False)
        embed.set_footer(text=f"أُنشئت بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, view=view, allowed_mentions=discord.AllowedMentions.none())

    @app_commands.command(name="bracket", description="[VIP] عرض شجرة بطولة كاملة (نظام تصفيات متعدد المواجهات)")
    @app_commands.describe(match1_t1="مباراة 1 - الطرف الأول", match1_t2="مباراة 1 - الطرف الثاني", match2_t1="مباراة 2 - الطرف الأول", match2_t2="مباراة 2 - الطرف الثاني")
    async def bracket(self, interaction: discord.Interaction, match1_t1: str, match1_t2: str, match2_t1: str, match2_t2: str):
        embed = discord.Embed(title="🏆 شجرة التصفيات والبطولة الرسمية", description="هذه مباريات الدور الحالي، يرجى التصويت في كل مواجهة لحين حسم المتأهلين للدور القادم!", color=0x9B59B6)
        
        embed.add_field(name="⚔️ المواجهة الأولى:", value=f"🔹 **{match1_t1}**  VS  **{match1_t2}**", inline=False)
        embed.add_field(name="⚔️ المواجهة الثانية:", value=f"🔸 **{match2_t1}**  VS  **{match2_t2}**", inline=False)
        embed.add_field(name="📌 طريقة اللعب:", value="استخدم أمر `/match` لكل مواجهة لحسم التصويت وتحديد من ينتصر ويصعد للدور التالي!", inline=False)
        
        embed.set_footer(text=f"إدارة البطولة بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, allowed_mentions=discord.AllowedMentions.none())

async def setup(bot):
    await bot.add_cog(Fun(bot))

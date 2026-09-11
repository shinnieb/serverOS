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
        self.votes_p1 = set()
        self.votes_p2 = set()
        self.message = None

    @discord.ui.button(label="", style=discord.ButtonStyle.success, emoji="🟢")
    async def vote_p1(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        if user_id in self.votes_p2:
            self.votes_p2.remove(user_id)
        
        if user_id in self.votes_p1:
            self.votes_p1.remove(user_id)
            await interaction.response.send_message("❌ تم إلغاء صوتك لصالح الطرف الأول.", ephemeral=True)
        else:
            self.votes_p1.add(user_id)
            await interaction.response.send_message(f"✅ تم تسجيل صوتك بنجاح لصالح: **{self.p1}**", ephemeral=True)
        
        await self.update_embed(interaction)

    @discord.ui.button(label="", style=discord.ButtonStyle.danger, emoji="🔴")
    async def vote_p2(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        if user_id in self.votes_p1:
            self.votes_p1.remove(user_id)
        
        if user_id in self.votes_p2:
            self.votes_p2.remove(user_id)
            await interaction.response.send_message("❌ تم إلغاء صوتك لصالح الطرف الثاني.", ephemeral=True)
        else:
            self.votes_p2.add(user_id)
            await interaction.response.send_message(f"✅ تم تسجيل صوتك بنجاح لصالح: **{self.p2}**", ephemeral=True)
        
        await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction):
        if not self.message and interaction.message:
            self.message = interaction.message
            
        if self.message:
            try:
                embed = self.message.embeds[0]
                for i, field in enumerate(embed.fields):
                    if "أصوات" in field.name or "طرفي" in field.name or "النتيجة" in field.name:
                        embed.set_field_at(
                            i,
                            name="🏟️ أطراف المواجهة والأصوات الحالية:",
                            value=f"🟢 **{self.p1}** (الأصوات: `{len(self.votes_p1)}`)\n*ضد*\n🔴 **{self.p2}** (الأصوات: `{len(self.votes_p2)}`)",
                            inline=False
                        )
                        break
                await self.message.edit(embed=embed, view=self)
            except Exception:
                pass

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        
        if len(self.votes_p1) > len(self.votes_p2):
            winner = self.p1
        elif len(self.votes_p2) > len(self.votes_p1):
            winner = self.p2
        else:
            winner = "تعادل بين الطرفين!"

        if self.message:
            try:
                embed = self.message.embeds[0]
                embed.color = 0x2ECC71
                embed.add_field(
                    name="🏆 انتهى وقت التصويت وتم حسم النتيجة:", 
                    value=f"انتهت المعركة بفوز: **{winner}**\n📊 إجمالي الأصوات: ({len(self.votes_p1)} ضد {len(self.votes_p2)})", 
                    inline=False
                )
                await self.message.edit(embed=embed, view=self)
            except Exception:
                pass
        self.stop()

class DynamicBracketView(discord.ui.View):
    def __init__(self, matches_list, hours):
        super().__init__(timeout=hours * 3600)
        self.matches_list = matches_list # قائمة تحتوي على ثنائيات المباريات
        
        # إضافة زر لكل مباراة بشكل ديناميكي مهما كان عددها!
        for index, (p1, p2) in enumerate(matches_list):
            button = discord.ui.Button(
                label=f"مباراة {index+1}: {p1} vs {p2}", 
                style=discord.ButtonStyle.primary, 
                emoji="⚔️",
                custom_id=f"match_{index}"
            )
            button.callback = self.create_match_callback(p1, p2, index + 1)
            self.add_item(button)

    def create_match_callback(self, p1, p2, match_num):
        async def callback(interaction: discord.Interaction):
            view = MatchView(p1, p2, f"المباراة رقم {match_num} من الشجرة", 3600)
            view.children[0].label = p1
            view.children[1].label = p2
            
            embed = discord.Embed(
                title=f"⚔️ حلبة التحدي | المباراة ({match_num})", 
                description=f"🟢 **{p1}** (الأصوات: `0`)\n*ضد*\n🔴 **{p2}** (الأصوات: `0`)", 
                color=0xF1C40F
            )
            embed.set_footer(text=f"بإشراف: {interaction.user.display_name}")
            
            msg = await interaction.channel.send(embed=embed, view=view)
            view.message = msg
            await interaction.response.send_message(f"✅ تم فتح صندوق اقتراع المباراة رقم ({match_num}) بنجاح!", ephemeral=True)
        return callback

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

    @app_commands.command(name="match", description="[خاص بالإداريين] إنشاء مواجهة رسمية فردية مع تحديد وقت التصويت بالساعات")
    @app_commands.describe(
        member1="الطرف الأول", 
        member2="الطرف الثاني", 
        hours="مدة التصويت بالساعات", 
        round_title="اسم الجولة"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def match(self, interaction: discord.Interaction, member1: str, member2: str, hours: float = 1.0, round_title: str = "مواجهة الإقصاء الكبرى"):
        timeout_seconds = hours * 3600
        view = MatchView(member1, member2, round_title, timeout_seconds)
        view.children[0].label = member1
        view.children[1].label = member2

        embed = discord.Embed(title=f"⚔️ حلبة التحدي والتصفيات | {round_title}", description=f"معركة حامية الوطيس! باب التصويت مفتوح لجميع الحضور.\n🟢 **{member1}** (الأصوات: `0`)\n*ضد*\n🔴 **{member2}** (الأصوات: `0`)\n\n⏱️ **مدة التصويت المحددة:** {hours} ساعة!", color=0xF1C40F)
        embed.set_footer(text=f"بإشراف: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        msg = await interaction.channel.send(embed=embed, view=view, allowed_mentions=discord.AllowedMentions.none())
        view.message = msg
        await interaction.response.send_message("✅ تم إطلاق المواجهة بنجاح!", ephemeral=True)

    @match.error
    async def match_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ عذراً، هذا الأمر مخصص فقط للمشرفين ومن يمتلكون صلاحية إسكات الأعضاء (Timeout)!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ حدث خطأ ما أثناء تنفيذ الأمر.", ephemeral=True)

    @app_commands.command(name="bracket", description="[خاص بالإداريين] إنشاء شجرة بطولة بأي عدد من المشاركين (افصل بينهم بفاصلة ,)")
    @app_commands.describe(
        participants="اكتب الأسماء مفصولة بفاصلة (مثال: أحمد, خالد, فهد, سلطان, تركي, راكان)",
        hours="مدة التصويت العامة بالساعات"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def bracket(self, interaction: discord.Interaction, participants: str, hours: float = 24.0):
        # تقسيم الأسماء المدخلة عن طريق الفاصلة وتنظيف المسافات
        names = [name.strip() for name in participants.split(",") if name.strip()]
        
        if len(names) < 2:
            await interaction.response.send_message("❌ يجب إدخال اسمين على الأقل لتشكيل المواجهات!", ephemeral=True)
            return

        # خلط الأسماء عشوائياً لتشكيل المواجهات
        random.shuffle(names)
        
        matches = []
        for i in range(0, len(names) - 1, 2):
            matches.append((names[i], names[i+1]))
        
        # إذا كان العدد فردي، الأخير يصعد تلقائياً أو يتم تنبيهه
        extra_person = names[-1] if len(names) % 2 != 0 else None

        view = DynamicBracketView(matches, hours)
        
        embed = discord.Embed(title="🏆 جدول وشجرة البطولات الرسمية (مفتوحة العدد)", description="تم توزيع المشاركين عشوائياً إلى مواجهات. اضغط على أزرار المباريات أدناه لفتح صناديق الاقتراع للحضور والتصويت:", color=0x9B59B6)
        
        desc_text = ""
        for idx, (p1, p2) in enumerate(matches, 1):
            desc_text += f"**المباراة {idx}:** 🔹 {p1}  VS  🔴 {p2}\n"
        
        if extra_person:
            desc_text += f"\n✨ **تأهل تلقائي للدور القادم بدون مواجهة:** {extra_person}"
            
        embed.add_field(name="⚔️ جدول المباريات المُولّد:", value=desc_text, inline=False)
        embed.set_footer(text=f"إدارة البطولة بواسطة: {interaction.user.display_name}")
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, view=view, allowed_mentions=discord.AllowedMentions.none())

    @bracket.error
    async def bracket_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ عذراً، هذا الأمر مخصص فقط للمشرفين ومن يمتلكون صلاحية إسكات الأعضاء (Timeout)!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ حدث خطأ ما أثناء تنفيذ الأمر.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Fun(bot))

import discord
from discord.ext import commands
from discord import app_commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="8ball", description="إسأل البلورة السحرية سؤالاً وسوف تجيبك!")
    @app_commands.describe(question="السؤال الذي تريد طرحه")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        responses = [
            "بالتأكيد نعم! 🟢",
            "من المؤكد ذلك ✨",
            "بدون أسباب للشك، نعم 👌",
            "عد وسلني لاحقاً... 🤔",
            "لا تعتمد على ذلك 🛑",
            "إجابتي هي لا 🔴"
        ]
        answer = random.choice(responses)
        embed = discord.Embed(title="🔮 البلورة السحرية", color=discord.Color.purple())
        embed.add_field(name="السؤال:", value=question, inline=False)
        embed.add_field(name="الجواب:", value=answer, inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="ارمي قطعة نقدية (ملك أم كتابة)")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["ملك 🪙", "كتابة 📜"])
        embed = discord.Embed(title="🪙 رمي قطعة نقدية", description=f"النتيجة هي: **{result}**", color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roll", description="ارمي النرد واحصل على رقم عشوائي")
    @app_commands.describe(max_num="أعلى رقم للنرد (الافتراضي 6)")
    async def roll(self, interaction: discord.Interaction, max_num: int = 6):
        if max_num < 1:
            await interaction.response.send_message("الرجاء اختيار رقم أكبر من 0!", ephemeral=True)
            return
        result = random.randint(1, max_num)
        embed = discord.Embed(title="🎲 رمي النرد", description=f"حصلت على الرقم: **{result}** (من {max_num})", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ship", description="احسب نسبة التوافق والمحبة بين شخصين")
    @app_commands.describe(user1="الشخص الأول", user2="الشخص الثاني (اختياري)")
    async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member = None):
        user2 = user2 or interaction.user
        percentage = (user1.id + user2.id) % 101
        filled_blocks = int(percentage / 10)
        progress_bar = "🟢" * filled_blocks + "⚪" * (10 - filled_blocks)

        embed = discord.Embed(title="❤️ مقياس التوافق (Ship)", color=discord.Color.magenta())
        embed.add_field(name="الأطراف:", value=f"{user1.mention} + {user2.mention}", inline=False)
        embed.add_field(name="النسبة:", value=f"**{percentage}%**\n{progress_bar}", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="عرض صورة حساب أي شخص")
    @app_commands.describe(member="العضو المراد عرض صورته")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = discord.Embed(title=f"🖼️ صورة {member.display_name}", color=discord.Color.blue())
        embed.set_image(url=member.display_avatar.url)
        embed.add_field(name="رابط الصورة:", value=f"[تحميل الصورة]({member.display_avatar.url})")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="مسح عدد محدد من الرسائل")
    @app_commands.describe(amount="عدد الرسائل المراد مسحها")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message("الرجاء تحديد رقم أكبر من صفر!", ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"تم مسح {len(deleted)} رسالة بنجاح!", ephemeral=True)

    @app_commands.command(name="kick", description="طرد عضو من السيرفر")
    @app_commands.describe(member="العضو المراد طرده", reason="السبب")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"تم طرد العضو {member.mention} بنجاح. السبب: {reason}")

    @app_commands.command(name="ban", description="حظر عضو من السيرفر")
    @app_commands.describe(member="العضو المراد حظره", reason="السبب")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "لا يوجد سبب"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"تم حظر العضو {member.mention} بنجاح. السبب: {reason}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
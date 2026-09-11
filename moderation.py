import discord
from discord.ext import commands
from discord.app_commands import checks

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clear", description="مسح عدد محدد من الرسائل")
    @checks.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int):
        if amount <= 0:
            await ctx.send("الرجاء تحديد رقم أكبر من صفر!", ephemeral=True)
            return
            
        await ctx.defer(ephemeral=True)
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.followup.send(f"تم مسح {len(deleted)} رسالة بنجاح!", ephemeral=True)

    @commands.hybrid_command(name="kick", description="طرد عضو من السيرفر")
    @checks.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "لا يوجد سبب"):
        await member.kick(reason=reason)
        await ctx.send(f"تم طرد العضو {member.mention} بنجاح. السبب: {reason}")

    @commands.hybrid_command(name="ban", description="حظر عضو من السيرفر")
    @checks.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "لا يوجد سبب"):
        await member.ban(reason=reason)
        await ctx.send(f"تم حظر العضو {member.mention} بنجاح. السبب: {reason}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))

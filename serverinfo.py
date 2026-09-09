import discord
from discord.ext import commands
from discord import app_commands
import config

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server", description="يعرض معلومات السيرفر الحالي")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("هذا الأمر لا يعمل إلا داخل سيرفر!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📊 معلومات سيرفر: {guild.name}",
            color=0x2b2d31
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        embed.add_field(name="👑 صاحب السيرفر", value=f"{guild.owner}", inline=True)
        embed.add_field(name="👥 الأعضاء", value=f"{guild.member_count}", inline=True)
        embed.add_field(name="🆔 آي دي السيرفر", value=f"`{guild.id}`", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
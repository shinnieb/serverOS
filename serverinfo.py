import discord
from discord.ext import commands
from discord import app_commands
import config

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server", description="عرض معلومات وإحصائيات السيرفر بشكل فخم وشامل")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ هذا الأمر لا يعمل إلا داخل سيرفر!", ephemeral=True)
            return

        # حساب أنواع الرومات والبوتات والأعضاء
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        total_channels = text_channels + voice_channels + categories
        
        roles_count = len(guild.roles)
        emojis_count = len(guild.emojis)
        
        # فرز الأعضاء (بشريين وبوتات)
        bots_count = sum(1 for m in guild.members if m.bot)
        humans_count = guild.member_count - bots_count

        # تنسيق تاريخ إنشاء السيرفر
        created_at = int(guild.created_at.timestamp())

        embed = discord.Embed(
            title=f"📊 إحصائيات ومعلومات سيرفر: {guild.name}",
            description=f"✨ **نبذة عامة عن إمبراطورية السيرفر وتفاصيلها الأساسية**",
            color=0x2b2d31
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        # الحقول الأساسية
        embed.add_field(name="👑 صاحب السيرفر", value=f"{guild.owner.mention}\n`{guild.owner}`", inline=True)
        embed.add_field(name="🆔 آي دي السيرفر", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="📅 تاريخ الإنشاء", value=f"<t:{created_at}:F>\n(<t:{created_at}:R>)", inline=False)
        
        # إحصائيات الأعضاء
        embed.add_field(
            name=f"👥 الأعضاء ({guild.member_count})", 
            value=f"👤 بشريين: `{humans_count}`\n🤖 بوتات: `{bots_count}`", 
            inline=True
        )
        
        # إحصائيات الرومات
        embed.add_field(
            name=f"📁 الرومات ({total_channels})", 
            value=f"💬 كتابية: `{text_channels}`\n🔊 صوتية: `{voice_channels}`\n📂 أقسام: `{categories}`", 
            inline=True
        )

        # معلومات إضافية (رتب وإيموجيز)
        embed.add_field(
            name="⚡ إضافات السيرفر", 
            value=f"🎨 الرتب: `{roles_count}` رتبة\n😀 الإيموجيز: `{emojis_count}` إيموجي", 
            inline=True
        )

        # مستوى الحماية والتعزيزات
        boosts = guild.premium_subscription_count
        boost_tier = guild.premium_tier
        embed.add_field(
            name="🚀 التعزيزات (Boosts)", 
            value=f"💎 المستوى: `{boost_tier}`\n🔮 عدد البوستات: `{boosts}` بوست", 
            inline=True
        )

        embed.set_footer(text=f"تم الطلب بواسطة {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))

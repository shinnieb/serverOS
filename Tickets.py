import discord
from discord import app_commands
from discord.ext import commands

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="إعداد_التذاكر", description="إنشاء رسالة إنشاء التذاكر مع زر تفاعلي")
    @app_commands.checks.has_permissions(administrator=True)
    async def ticket_setup(self, interaction: discord.Interaction):
        class TicketButton(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=None)

            @discord.ui.button(label="فتح تذاكر 🎫", style=discord.ButtonStyle.green, custom_id="open_ticket_btn")
            async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
                guild = interaction.guild
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
                }
                
                # إنشاء روم خاصة بالتذكرة
                category = discord.utils.get(guild.categories, name="التذاكر")
                if not category:
                    category = await guild.create_category("التذاكر")

                channel = await guild.create_text_channel(f"تذكرة-{interaction.user.name}", category=category, overwrites=overwrites)
                
                embed = discord.Embed(
                    title="🎫 تذكرة دعم جديدة",
                    description=f"مرحباً بك {interaction.user.mention}\nأخبرنا بمشكلتك أو استفسارك، وسيقوم فريق الإدارة بالرد عليك قريباً.",
                    color=discord.Color.blue()
                )
                await channel.send(embed=embed)
                await interaction.response.send_message(f"تم إنشاء تذكرتك بنجاح: {channel.mention}", ephemeral=True)

        embed = discord.Embed(
            title="🎫 نظام التذاكر - ServerOS",
            description="اضغط على الزر أدناه لفتح تذكرة دعم خاصة مع الإدارة.",
            color=discord.Color.blurple()
        )
        await interaction.channel.send(embed=embed, view=TicketButton())
        await interaction.response.send_message("تم إرسال رسالة التذاكر بنجاح!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
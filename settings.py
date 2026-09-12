import json
import os
import discord
from discord import app_commands
from discord.ext import commands

CONFIG_FILE = "bot_settings.json"


def load_config():
  if os.path.exists(CONFIG_FILE):
    try:
      with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      pass
  return {
      "features": {
          "welcome": True,
          "tickets": True,
          "lockdown": False,
          "maintenance": False,
      }
  }


def save_config(config):
  with open(CONFIG_FILE, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)


class SettingsCog(commands.Cog):

  def __init__(self, bot):
    self.bot = bot

  def get_settings_view(self, author):
    config = load_config()
    features = config["features"]

    view = discord.ui.View(timeout=None)

    welcome_btn = discord.ui.Button(
        label="نظام الترحيب",
        style=(
            discord.ButtonStyle.success
            if features.get("welcome", True)
            else discord.ButtonStyle.danger
        ),
        emoji="👋",
        custom_id="toggle_welcome",
    )

    tickets_btn = discord.ui.Button(
        label="نظام التذاكر",
        style=(
            discord.ButtonStyle.success
            if features.get("tickets", True)
            else discord.ButtonStyle.danger
        ),
        emoji="🎫",
        custom_id="toggle_tickets",
    )

    lockdown_btn = discord.ui.Button(
        label="الوضع الآمن (Lockdown)",
        style=(
            discord.ButtonStyle.danger
            if features.get("lockdown", False)
            else discord.ButtonStyle.secondary
        ),
        emoji="🔒",
        custom_id="toggle_lockdown",
        row=1,
    )

    maint_btn = discord.ui.Button(
        label="وضع الصيانة",
        style=(
            discord.ButtonStyle.danger
            if features.get("maintenance", False)
            else discord.ButtonStyle.secondary
        ),
        emoji="🛠️",
        custom_id="toggle_maintenance",
        row=1,
    )

    async def update_panel(interaction: discord.Interaction):
      cfg = load_config()
      f = cfg["features"]
      w_st = "مفعل ✅" if f.get("welcome", True) else "معطل ❌"
      t_st = "مفعل ✅" if f.get("tickets", True) else "معطل ❌"
      l_st = "مفعل 🔴 (طوارئ)" if f.get("lockdown", False) else "غير مفعل 🟢"
      m_st = "مفعل 🛠️" if f.get("maintenance", False) else "متصل طبيعي 🟢"

      embed = discord.Embed(
          title="❖ لـوحـة تـحـكـم السيرفر الشاملة",
          description=(
              "مرحباً بك يا قائد السيرفر. الأزرار الملونة توضح حالة الأنظمة"
              " مباشرة (أخضر = شغال، أحمر = معطل/طوارئ)."
          ),
          color=discord.Color.from_rgb(20, 21, 24),
      )
      if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)

      embed.add_field(name="👋 نظام الترحيب", value=w_st, inline=True)
      embed.add_field(name="🎫 نظام التذاكر", value=t_st, inline=True)
      embed.add_field(name="🔒 الوضع الآمن (Lockdown)", value=l_st, inline=False)
      embed.add_field(name="🛠️ وضع الصيانة", value=m_st, inline=False)
      embed.set_footer(
          text=f"أُستدعي بواسطة: {interaction.user.name}",
          icon_url=interaction.user.display_avatar.url,
      )

      new_view = self.get_settings_view(interaction.user)
      await interaction.response.edit_message(embed=embed, view=new_view)

    async def welcome_callback(interaction: discord.Interaction):
      if not (
          interaction.user.guild_permissions.administrator
          or interaction.user == author
      ):
        return await interaction.response.send_message(
            "⛔ للإداريين فقط!", ephemeral=True
        )
      cfg = load_config()
      current = cfg["features"].get("welcome", True)
      cfg["features"]["welcome"] = not current
      save_config(cfg)
      await update_panel(interaction)

    async def tickets_callback(interaction: discord.Interaction):
      if not (
          interaction.user.guild_permissions.administrator
          or interaction.user == author
      ):
        return await interaction.response.send_message(
            "⛔ للإداريين فقط!", ephemeral=True
      )
      cfg = load_config()
      current = cfg["features"].get("tickets", True)
      cfg["features"]["tickets"] = not current
      save_config(cfg)
      await update_panel(interaction)

    async def lockdown_callback(interaction: discord.Interaction):
      if not (
          interaction.user.guild_permissions.administrator
          or interaction.user == author
      ):
        return await interaction.response.send_message(
            "⛔ للإداريين فقط!", ephemeral=True
        )
      cfg = load_config()
      current = cfg["features"].get("lockdown", False)
      cfg["features"]["lockdown"] = not current
      save_config(cfg)

      status_text = (
          "🔒 **تم تفعيل الوضع الآمن! تم إيقاف التفاعل مؤقتاً.**"
          if not current
          else "🔓 **تم إلغاء الوضع الآمن وعودة الأمور لطبيعتها.**"
      )
      await interaction.channel.send(status_text)
      await update_panel(interaction)

    async def maintenance_callback(interaction: discord.Interaction):
      if not (
          interaction.user.guild_permissions.administrator
          or interaction.user == author
      ):
        return await interaction.response.send_message(
            "⛔ للإداريين فقط!", ephemeral=True
        )
      cfg = load_config()
      current = cfg["features"].get("maintenance", False)
      cfg["features"]["maintenance"] = not current
      save_config(cfg)
      await update_panel(interaction)

    welcome_btn.callback = welcome_callback
    tickets_btn.callback = tickets_callback
    lockdown_btn.callback = lockdown_callback
    maint_btn.callback = maintenance_callback

    view.add_item(welcome_btn)
    view.add_item(tickets_btn)
    view.add_item(lockdown_btn)
    view.add_item(maint_btn)

    return view

  @app_commands.command(
      name="إعدادات-البوت", description="لوحة التحكم الشاملة لإدارة أنظمة السيرفر"
  )
  @app_commands.checks.has_permissions(administrator=True)
  async def settings_panel(self, interaction: discord.Interaction):
    config = load_config()
    f = config["features"]

    w_st = "مفعل ✅" if f.get("welcome", True) else "معطل ❌"
    t_st = "مفعل ✅" if f.get("tickets", True) else "معطل ❌"
    l_st = "مفعل 🔴 (طوارئ)" if f.get("lockdown", False) else "غير مفعل 🟢"
    m_st = "مفعل 🛠️" if f.get("maintenance", False) else "متصل طبيعي 🟢"

    embed = discord.Embed(
        title="❖ لـوحـة تـحـكـم السيرفر الشاملة",
        description=(
            "مرحباً بك يا قائد السيرفر. الأزرار الملونة توضح حالة الأنظمة مباشرة"
            " (أخضر = شغال، أحمر = معطل/طوارئ)."
        ),
        color=discord.Color.from_rgb(20, 21, 24),
    )
    if interaction.guild.icon:
      embed.set_thumbnail(url=interaction.guild.icon.url)

    embed.add_field(name="👋 نظام الترحيب", value=w_st, inline=True)
    embed.add_field(name="🎫 نظام التذاكر", value=t_st, inline=True)
    embed.add_field(name="🔒 الوضع الآمن (Lockdown)", value=l_st, inline=False)
    embed.add_field(name="🛠️ وضع الصيانة", value=m_st, inline=False)
    embed.set_footer(
        text=f"أُستدعي بواسطة: {interaction.user.name}",
        icon_url=interaction.user.display_avatar.url,
    )

    view = self.get_settings_view(interaction.user)
    await interaction.response.send_message(
        embed=embed, view=view, ephemeral=True
    )

  @settings_panel.error
  async def settings_error(self, interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
      msg = (
          "❌ عذراً، هذا الأمر مخصص للأعضاء الحاصلين على صلاحية **Administrator**"
          " فقط."
      )
      if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
      else:
        await interaction.response.send_message(msg, ephemeral=True)


async def setup(bot):
  await bot.add_cog(SettingsCog(bot))
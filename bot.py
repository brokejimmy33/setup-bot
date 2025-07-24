import discord
from discord.ext import commands
from discord import app_commands, Interaction
import json
import asyncio
import os
import os
import os
import traceback

while True:
    try:
        bot.run(TOKEN)
    except Exception as e:
        with open("error_log.txt", "a") as f:
            f.write(traceback.format_exc())
        time.sleep(10)

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # Needed to read messages
bot = commands.Bot(command_prefix='!', intents=intents)

import time
from keep_alive import keep_alive
import discord
from discord.ext import commands

keep_alive()

while True:
    try:
        bot = commands.Bot(command_prefix="!")
        # your bot setup here
        bot.run(os.getenv("DISCORD_TOKEN"))
    except Exception as e:
        print(f"Bot crashed with error: {e}")
        time.sleep(5)

from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "I'm alive!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


from dotenv import load_dotenv

load_dotenv()  # Loads .env file into environment
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Constants ---
CONFIG_FILE = "config.json"

# --- Bot setup ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# --- Config management ---
def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({}, f)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


config = load_config()


def get_guild_config(guild_id):
    gid = str(guild_id)
    if gid not in config:
        config[gid] = {}
    return config[gid]


# --- Logging helper ---
async def log_action(guild, message):
    conf = get_guild_config(guild.id)
    log_channel_id = conf.get("log_channel")
    if log_channel_id:
        channel = guild.get_channel(log_channel_id)
        if channel:
            embed = discord.Embed(description=message,
                                  color=discord.Color.orange())
            await channel.send(embed=embed)


# --- Events ---
@bot.event
async def on_ready():
    for guild in bot.guilds:
        await tree.sync(guild=guild)
        print(f"✅ Synced commands to: {guild.name} ({guild.id})")

    await tree.sync()  # Global sync
    print(f"✅ Global command sync complete")
    print(f"✅ Bot is online as {bot.user}")


@bot.event
async def on_member_join(member):
    conf = get_guild_config(member.guild.id)
    role_id = conf.get("auto_role")
    if role_id:
        role = member.guild.get_role(role_id)
        if role:
            await member.add_roles(role)
            print(f"✅ Auto-role '{role.name}' assigned to {member}")

    # Welcome message in #🌱-start-here if exists
    channel = discord.utils.get(member.guild.text_channels,
                                name="🌱-start-here")
    if channel:
        await channel.send(
            f"🎉 Welcome {member.mention} to **{member.guild.name}**!")

    # Welcome DM
    try:
        await member.send(
            f"Welcome to **{member.guild.name}**! Enjoy your stay 🥔")
    except Exception:
        pass

    await log_action(member.guild, f"🌐 {member} joined the server.")


@bot.event
async def on_member_remove(member):
    await log_action(member.guild, f"❌ {member} has left the server.")


# --- Error handling ---
@bot.event
async def on_app_command_error(interaction: Interaction, error):
    await interaction.response.send_message(f"❌ Error: {error}")


# --- Commands ---


@tree.command(name="setup",
              description="Create server categories, channels, and roles")
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: Interaction):
    guild = interaction.guild
    await interaction.response.send_message("⚙️ Setting up server...")

    # Existing roles
    roles = {
        "🥔 The Ultimate Admin":
        discord.Permissions(administrator=True),
        "🥄 Mashed Mod":
        discord.Permissions(kick_members=True, manage_messages=True),
        "👥 Potato People":
        discord.Permissions(send_messages=True, read_messages=True),
        "🥔 Guest Tater":
        discord.Permissions(read_messages=True, send_messages=False),
        # New fun roles
        "🎉 Party People":
        discord.Permissions(send_messages=True, read_messages=True),
        "🧠 Big Brain":
        discord.Permissions(send_messages=True, read_messages=True),
        "🔧 Tech Wizard":
        discord.Permissions(send_messages=True, read_messages=True),
        "🎮 Gamer":
        discord.Permissions(send_messages=True, read_messages=True),
        "📚 Learner":
        discord.Permissions(send_messages=True, read_messages=True),
        "👑 Server Founder":
        discord.Permissions(administrator=True)
    }

    created_roles = {}
    for name, perms in roles.items():
        role = discord.utils.get(guild.roles, name=name)
        if not role:
            role = await guild.create_role(name=name, permissions=perms)
        created_roles[name] = role

    # Helper to create category if not exists
    async def create_category(name, overwrites=None):
        cat = discord.utils.get(guild.categories, name=name)
        if cat:
            return cat
        return await guild.create_category(name, overwrites=overwrites)

    # Helper to create text channel if not exists
    async def create_text(name, category):
        if not discord.utils.get(guild.text_channels, name=name):
            await guild.create_text_channel(name, category=category)

    # Helper to create voice channel if not exists
    async def create_voice(name, category):
        if not discord.utils.get(guild.voice_channels, name=name):
            await guild.create_voice_channel(name, category=category)

    # Permission overwrites
    everyone = guild.default_role
    admin_roles = [
        created_roles["🥔 The Ultimate Admin"], created_roles["🥄 Mashed Mod"],
        created_roles["👑 Server Founder"]
    ]

    overwrites_public = {
        everyone:
        discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }
    overwrites_admin_only = {
        everyone: discord.PermissionOverwrite(view_channel=False),
    }
    for r in admin_roles:
        overwrites_admin_only[r] = discord.PermissionOverwrite(
            view_channel=True, send_messages=True)

    # 1 - Essential Categories & Channels
    welcome_cat = await create_category("🏠 Welcome", overwrites_public)
    await create_text("welcome", welcome_cat)
    await create_text("rules", welcome_cat)
    await create_text("announcements", welcome_cat)

    roles_cat = await create_category("📋 Roles", overwrites_public)
    await create_text("roles", roles_cat)

    # 2 - Community
    community_cat = await create_category("👋 Community", overwrites_public)
    await create_text("general-chat", community_cat)
    await create_text("introductions", community_cat)
    await create_text("media", community_cat)
    await create_text("off-topic", community_cat)

    # 3 - Server Info / Logs (admin/mod only)
    logs_cat = await create_category("📢 Server Info / Logs",
                                     overwrites_admin_only)
    await create_text("server-logs", logs_cat)
    await create_text("mod-log", logs_cat)
    await create_text("bot-log", logs_cat)

    # 4 - Gaming
    gaming_cat = await create_category("🎮 Gaming", overwrites_public)
    await create_text("game-chat", gaming_cat)
    await create_text("team-up", gaming_cat)
    await create_text("clips-and-screenshots", gaming_cat)

    # 5 - Study / Work / Tech
    study_cat = await create_category("📚 Study / Work / Tech",
                                      overwrites_public)
    await create_text("resources", study_cat)
    await create_text("questions", study_cat)
    await create_text("daily-progress", study_cat)
    await create_text("projects", study_cat)

    # 6 - Voice Channels
    voice_cat = await create_category("🔊 Voice Channels", overwrites_public)
    await create_voice("General VC", voice_cat)
    await create_voice("Study Room", voice_cat)
    await create_voice("Gaming VC", voice_cat)
    # Private Room with restricted access to Admin and Mods
    overwrites_private = {
        everyone: discord.PermissionOverwrite(view_channel=False),
    }
    for r in admin_roles:
        overwrites_private[r] = discord.PermissionOverwrite(view_channel=True,
                                                            connect=True,
                                                            speak=True)
    private_vc = discord.utils.get(guild.voice_channels, name="Private Room")
    if not private_vc:
        await guild.create_voice_channel("Private Room",
                                         category=voice_cat,
                                         overwrites=overwrites_private)

    # 7 - Advanced (optional)
    advanced_cat = await create_category("🚀 Advanced", overwrites_public)
    await create_text("suggestions", advanced_cat)
    await create_text("polls", advanced_cat)
    await create_text("faq", advanced_cat)
    await create_text("support", advanced_cat)

    await interaction.followup.send(
        "✅ Server setup complete with new categories, channels, and roles added!"
    )


@tree.command(name="setlogchannel",
              description="Set the channel where logs will be sent")
@app_commands.describe(channel="Select a text channel")
@app_commands.checks.has_permissions(administrator=True)
async def setlogchannel(interaction: Interaction,
                        channel: discord.TextChannel):
    conf = get_guild_config(interaction.guild.id)
    conf["log_channel"] = channel.id
    save_config(config)
    await interaction.response.send_message(
        f"📃 Logs will be sent to {channel.mention}")


@tree.command(name="autorole",
              description="Choose a role to auto-assign to new members")
@app_commands.describe(role="The role to give on join")
@app_commands.checks.has_permissions(administrator=True)
async def autorole(interaction: Interaction, role: discord.Role):
    conf = get_guild_config(interaction.guild.id)
    conf["auto_role"] = role.id
    save_config(config)
    await interaction.response.send_message(f"📁 Auto-role set: {role.mention}")


@tree.command(name="config",
              description="Show all current configuration settings")
@app_commands.checks.has_permissions(administrator=True)
async def config_show(interaction: Interaction):
    conf = get_guild_config(interaction.guild.id)
    log_channel_id = conf.get("log_channel")
    auto_role_id = conf.get("auto_role")

    log_channel = interaction.guild.get_channel(
        log_channel_id) if log_channel_id else None
    auto_role = interaction.guild.get_role(
        auto_role_id) if auto_role_id else None

    embed = discord.Embed(title="🔧 Server Configuration",
                          color=discord.Color.blue())
    embed.add_field(name="📝 Log Channel",
                    value=log_channel.mention if log_channel else "❌ Not set",
                    inline=False)
    embed.add_field(name="👤 Auto Role",
                    value=auto_role.mention if auto_role else "❌ Not set",
                    inline=False)
    await interaction.response.send_message(embed=embed)


@tree.command(name="commands", description="Show all available commands")
async def show_commands(interaction: Interaction):
    embed = discord.Embed(
        title="📘 The Ultimate Potato Commands",
        description="Here's a list of all slash commands you can use:",
        color=discord.Color.green())

    embed.add_field(name="/setup",
                    value="Create server categories and roles",
                    inline=False)
    embed.add_field(name="/setlogchannel",
                    value="Set the log channel for moderation actions",
                    inline=False)
    embed.add_field(name="/autorole",
                    value="Set an auto-role for new members",
                    inline=False)
    embed.add_field(name="/config",
                    value="Show all current config values",
                    inline=False)
    embed.add_field(name="/mute",
                    value="Temporarily mute a member",
                    inline=False)
    embed.add_field(name="/unmute", value="Unmute a member", inline=False)
    embed.add_field(name="/ban", value="Ban a user", inline=False)
    embed.add_field(name="/kick", value="Kick a user", inline=False)
    embed.add_field(name="/bots",
                    value="Show recommended bots for your server",
                    inline=False)
    embed.add_field(name="/resync",
                    value="Force re-sync of commands (Admin only)",
                    inline=False)

    embed.set_footer(
        text="Some commands require special permissions (Admin, Mod, etc.)")
    await interaction.response.send_message(embed=embed)


@tree.command(name="bots", description="Show recommended bots")
async def bots(interaction: Interaction):
    embed = discord.Embed(title="🥔 Recommended Bots for The Ultimate Potato",
                          description="Useful bots to help your server grow!",
                          color=discord.Color.gold())
    embed.add_field(
        name="🛡️ Moderation",
        value=
        "[Carl-bot](https://carl.gg/invite)\n[Dyno](https://dyno.gg/invite)",
        inline=False)
    embed.add_field(
        name="📊 Stats & Tickets",
        value=
        "[Statbot](https://statbot.net/invite)\n[Ticket Tool](https://tickettool.xyz/direct-invite)",
        inline=False)
    embed.add_field(
        name="🎉 Fun & XP",
        value=
        "[Arcane](https://arcane.bot/invite)\n[Dank Memer](https://dankmemer.lol/invite)",
        inline=False)
    embed.set_footer(text="You must have 'Manage Server' to invite bots.")
    await interaction.response.send_message(embed=embed)


@tree.command(name="mute", description="Mute a user for a duration in minutes")
@app_commands.describe(member="Member to mute", duration="Duration in minutes")
@app_commands.checks.has_permissions(manage_roles=True)
async def mute(interaction: Interaction, member: discord.Member,
               duration: int):
    guild = interaction.guild
    mute_role = discord.utils.get(guild.roles, name="Muted")
    if not mute_role:
        mute_role = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(mute_role,
                                          send_messages=False,
                                          speak=False)

    await member.add_roles(mute_role)
    await interaction.response.send_message(
        f"⏱ {member.mention} has been muted for {duration} minutes.")
    await log_action(
        guild,
        f"⛔ {member} was muted for {duration} min by {interaction.user}.")

    await asyncio.sleep(duration * 60)
    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        await log_action(guild, f"🔈 {member} was automatically unmuted.")


@tree.command(name="unmute", description="Unmute a member")
@app_commands.checks.has_permissions(manage_roles=True)
async def unmute(interaction: Interaction, member: discord.Member):
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if mute_role in member.roles:
        await member.remove_roles(mute_role)
        await interaction.response.send_message(
            f"🔈 {member.mention} has been unmuted.")
        await log_action(
            interaction.guild,
            f"🔈 {member} was manually unmuted by {interaction.user}.")
    else:
        await interaction.response.send_message(
            f"❌ {member.mention} is not muted.")


@tree.command(name="ban", description="Ban a user")
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(member="User to ban", reason="Reason for ban")
async def ban(interaction: Interaction,
              member: discord.Member,
              reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await interaction.response.send_message(
        f"🔨 {member.mention} has been banned.")
    await log_action(interaction.guild,
                     f"🔨 {member} was banned by {interaction.user}: {reason}")


@tree.command(name="kick", description="Kick a user")
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.describe(member="User to kick", reason="Reason for kick")
async def kick(interaction: Interaction,
               member: discord.Member,
               reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(
        f"👢 {member.mention} has been kicked.")
    await log_action(interaction.guild,
                     f"👢 {member} was kicked by {interaction.user}: {reason}")


@tree.command(name="resync", description="Force re-sync of slash commands")
@app_commands.checks.has_permissions(administrator=True)
async def resync(interaction: Interaction):
    await tree.sync()
    await interaction.response.send_message("🔄 Slash commands resynced!")


TOKEN = os.getenv("DISCORD_TOKEN")
keep_alive()
bot.run(TOKEN)

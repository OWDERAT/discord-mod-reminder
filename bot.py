
import os
import re
import discord

# ==============================
# CONFIGURATION
# ==============================

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

REMINDER_CHANNEL_ID = 1553381648425287792
MOD_CHANNEL_ID = 1556313791153705091

TRIGGER_WORDS = {
    "get",
    "download",
    "install",
    "mod",
    "find",
}

# ==============================
# BOT SETUP
# ==============================

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")
    print(f"Listening for: {', '.join(sorted(TRIGGER_WORDS))}")


@client.event
async def on_message(message):
    # Ignore bots to prevent loops.
    if message.author.bot:
        return

    # Only process messages sent in servers.
    if message.guild is None:
        return

    # Match complete words, ignoring capitalization.
    words = set(
        re.findall(r"\b[a-zA-Z]+\b", message.content.lower())
    )

    if not words.intersection(TRIGGER_WORDS):
        return

    # Find both channels.
    reminder_channel = client.get_channel(REMINDER_CHANNEL_ID)
    mod_channel = client.get_channel(MOD_CHANNEL_ID)

    if reminder_channel is None:
        print(f"Reminder channel not found: {REMINDER_CHANNEL_ID}")
        return

    if mod_channel is None:
        print(f"Mod channel not found: {MOD_CHANNEL_ID}")
        return

    # Send the reminder to the designated channel.
    try:
        await reminder_channel.send(
            f"**Mod reminder!** Link to the mod: {mod_channel.mention}"
        )
        print(
            f"Reminder sent to #{reminder_channel.name} "
            f"for a message by {message.author}."
        )

    except discord.Forbidden:
        print("Missing permission to send messages in the reminder channel.")

    except discord.HTTPException as error:
        print(f"Failed to send reminder: {error}")


# ==============================
# START BOT
# ==============================

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError(
            "DISCORD_BOT_TOKEN is missing. "
            "Configure it in your hosting environment variables."
        )

    client.run(TOKEN)

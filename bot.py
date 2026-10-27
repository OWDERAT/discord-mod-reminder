
import os
import re
import discord

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

REMINDER_CHANNEL_ID = 1553381648425287792
MOD_CHANNEL_ID = 1556313791153705091

# Mod names and related topics.
MOD_TOPIC = re.compile(
    r"\bmods?\b"
    r"|frame[\s-]*counter"
    r"|window[\s-]*mod"
    r"|\bfps\b"
    r"|razys?\s+(?:mod|frame|counter|window)",
    re.IGNORECASE,
)

# Strong indicators that someone wants to FIND or ACCESS something.
REQUEST_PATTERNS = [
    # Where/how questions
    r"\bwhere\b.{0,80}\b(?:get|find|download|install|access|link|channel|posted|located)\b",
    r"\bhow\b.{0,80}\b(?:get|find|download|install|access)\b",
    r"\bwhere\s+is\s+(?:the\s+)?(?:download|link|mod|mods|mod\s+channel)\b",
    r"\bwhat\s+channel\b.{0,80}\b(?:mod|download|link|it|that)\b",
    r"\bwhich\s+channel\b.{0,80}\b(?:mod|download|link|it|that)\b",

    # Asking for a link or download
    r"\b(?:anyone|anybody|someone|somebody)\b.{0,60}\b(?:got|have|has|know\s+where)\b.{0,80}\b(?:mod|link|download|it|one)\b",
    r"\b(?:any|a)\s+(?:download|link)\s+(?:for|to)\b",
    r"\b(?:link|download)\s+(?:for|to)\b",
    r"\b(?:send|give|drop|share)\s+(?:me\s+)?(?:the\s+)?(?:mod\s+)?(?:link|download)\b",
    r"\bcan\s+(?:someone|anyone)\s+(?:send|give|drop|share|link)\b",

    # Looking for something
    r"\b(?:looking|searching)\s+for\b",
    r"\b(?:can't|cannot|cant|unable\s+to)\s+find\b",
    r"\b(?:need|want)\b.{0,50}\b(?:mod|link|download|install)\b",
    r"\bdoes\s+(?:anyone|anybody|this\s+server)\s+have\b",
    r"\bis\s+there\s+(?:a|any|an)\b",

    # Direct instructions/questions about obtaining a mod
    r"\bhow\s+to\s+(?:get|find|download|install)\b",
    r"\bhow\s+(?:can|do)\s+i\s+(?:get|find|download|install)\b",
    r"\b(?:get|find|download|install)\b.{0,80}\b(?:mod|mods|frame[\s-]*counter|window[\s-]*mod)\b",
]

# Reject obvious non-requests before checking request patterns.
EXCLUSION_PATTERNS = [
    r"\bget\s+(?:someone|somebody)\s+to\b",
    r"\bfind\s+(?:someone|somebody)\s+to\b",
    r"\b(?:moderator|moderators|moderation)\b",
    r"\b(?:is|was|looks|sounds|feels)\s+(?:so\s+)?(?:good|great|awesome|cool|amazing|fire|goated)\b",
    r"\b(?:w|goat)\s+for\s+this\b",
    r"\b(?:cooked|goated|based)\b",
    r"\bshould\s+(?:add|change|fix|make|remove)\b",
    r"\b(?:already|just|finally)\s+(?:got|found|downloaded|installed)\b",
]

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def is_excluded(text):
    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in EXCLUSION_PATTERNS
    )


def is_mod_request(text):
    # Do not trigger on obvious chatter or compliments.
    if is_excluded(text):
        return False

    # A request must match an actual request pattern.
    if not any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in REQUEST_PATTERNS
    ):
        return False

    # It must also be about a mod, a download, a link, or a channel.
    return bool(MOD_TOPIC.search(text)) or bool(
        re.search(
            r"\b(?:download|installation|install|link|mod\s+channel)\b",
            text,
            re.IGNORECASE,
        )
    )


@client.event
async def on_ready():
    print(f"Bot is online as {client.user}")
    print("Listening for mod requests.")


@client.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    if not is_mod_request(message.content):
        return

    reminder_channel = client.get_channel(REMINDER_CHANNEL_ID)
    mod_channel = client.get_channel(MOD_CHANNEL_ID)

    if reminder_channel is None or mod_channel is None:
        print("A configured channel could not be found.")
        return

    try:
        await reminder_channel.send(
            f"**Mod reminder!** Link to the mod: {mod_channel.mention}"
        )
        print(f"Reminder sent for message by {message.author}.")

    except discord.Forbidden:
        print("Missing permission to send messages in the reminder channel.")

    except discord.HTTPException as error:
        print(f"Failed to send reminder: {error}")


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError(
            "DISCORD_BOT_TOKEN is missing. "
            "Configure it in your hosting environment variables."
        )

    client.run(TOKEN)

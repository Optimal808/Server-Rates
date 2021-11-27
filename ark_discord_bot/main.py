import discord
from discord.ext import commands
import ark_discord_bot
import logging
from ark_discord_bot.utils import setup_argparse
from ark_discord_bot.bot import ConfigurableBot
from ark_discord_bot.config import setup_config, REQUIRED_VALUES

# https://discord.com/api/oauth2/authorize?client_id=912847784477065278&permissions=117760&scope=bot//

logger = logging.getLogger("ark-discord-bot")


def cli():
    # Configure logging for CLI usage.
    logger.setLevel(level=logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Define CLI arguments.
    parser = setup_argparse()

    # Load arguments from CLI
    args = parser.parse_args()

    # Override default log level
    if args.debug:
        ch.setLevel(logging.DEBUG)

    # Set up configuration dict
    config = setup_config(args)

    # Check for required values
    missing_vals = []
    for val in REQUIRED_VALUES:
        if not config.get(val):
            missing_vals.append(val)
    if len(missing_vals) > 0:
        logger.error(f"Missing required configuration variables: {missing_vals}")
        exit(1)

    run(**config)


def run(**kwargs):
    client = ConfigurableBot(".", kwargs)

    # load a cog
    @client.command()
    @commands.has_any_role(*client.config.allowed_roles)
    async def load(ctx, extension):
        client.load_extension(f"ark_discord_bot.cogs.{extension}")

    # unload a cogcd
    @client.command()
    @commands.has_any_role(*client.config.allowed_roles)
    async def unload(ctx, extension):
        client.unload_extension(f"ark_discord_bot.cogs.{extension}")

    # reload a cog
    @client.command()
    @commands.has_any_role(*client.config.allowed_roles)
    async def reload(ctx, extension):
        client.unload_extension(f"ark_discord_bot.cogs.{extension}")
        client.load_extension(f"ark_discord_bot.cogs.{extension}")
        await ctx.send(f"Extension '{extension}' reloaded.")

    # load all cogs on boot
    for ext in ark_discord_bot.cogs.__all__:
        client.load_extension(f"ark_discord_bot.cogs.{ext}")

    # run the bot
    try:
        logger.debug(f"Running with config: {client.config.__dict__}")
        client.run(client.config.token)
    except discord.errors.LoginFailure as e:
        logger.error("Problem with token.")
        exit(1)


if __name__ == "__main__":

    cli()

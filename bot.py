"""Main bot file for PopcornBot."""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import logging
import sys
import os
import asyncio

from config import BOT_TOKEN
from models import InitiativeManager
from commands import (
    PoolGroup,
    popcorn_add,
    popcorn_start,
    popcorn_next,
    popcorn_end,
    popcorn_clear,
    popcorn_status,
)


# Set up logging
# In Docker, we want logs to go to stdout/stderr for container logging
# Check if we're in Docker by looking for .dockerenv file
handlers = [logging.StreamHandler(sys.stdout)]
if not os.path.exists('/.dockerenv'):
    # Not in Docker, also log to file
    handlers.append(logging.FileHandler('bot.log'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)


class PopcornBot(commands.Bot):
    """PopcornBot instance."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Privileged intent - enabled in Developer Portal
        intents.members = True  # Privileged intent - enabled in Developer Portal
        intents.guilds = True  # Already in default(), but explicit for clarity
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            description="A Discord bot for managing Popcorn Initiative in TTRPGs"
        )
        
        self.initiative_manager = InitiativeManager()
    
    async def setup_hook(self):
        """Called when the bot is starting up."""
        logger.info("Setting up bot...")
        
        # Create main popcorn command group
        popcorn_group = app_commands.Group(name="popcorn", description="Popcorn Initiative commands")
        
        # Register pool subcommand group
        pool_group = PoolGroup(self, self.initiative_manager)
        popcorn_group.add_command(pool_group)
        
        # Register initiative commands as subcommands
        @popcorn_group.command(name="add", description="Add user to pool and initiative")
        @app_commands.describe(user="The user to add")
        async def popcorn_add_cmd(interaction: discord.Interaction, user: discord.Member):
            await popcorn_add(interaction, user, self.initiative_manager)
        
        @popcorn_group.command(name="start", description="Start the initiative")
        @app_commands.describe(user="Optional: The user to start with")
        async def popcorn_start_cmd(interaction: discord.Interaction, user: Optional[discord.Member] = None):
            await popcorn_start(interaction, user, self.initiative_manager)
        
        @popcorn_group.command(name="next", description="Pass turn to next player")
        @app_commands.describe(user="Optional: The user to pass to")
        async def popcorn_next_cmd(interaction: discord.Interaction, user: Optional[discord.Member] = None):
            await popcorn_next(interaction, user, self.initiative_manager)
        
        @popcorn_group.command(name="end", description="End the current initiative")
        async def popcorn_end_cmd(interaction: discord.Interaction):
            await popcorn_end(interaction, self.initiative_manager)
        
        @popcorn_group.command(name="clear", description="Clear initiative brackets")
        async def popcorn_clear_cmd(interaction: discord.Interaction):
            await popcorn_clear(interaction, self.initiative_manager)
        
        @popcorn_group.command(name="status", description="Show current initiative status")
        async def popcorn_status_cmd(interaction: discord.Interaction):
            await popcorn_status(interaction, self.initiative_manager)
        
        # Add the popcorn group to the command tree
        self.tree.add_command(popcorn_group)
        
        # Log registered commands for debugging
        logger.info(f"Registered command group: {popcorn_group.name}")
        logger.info(f"Commands in tree: {[cmd.name for cmd in self.tree.get_commands()]}")
        
        # Commands will be synced in on_ready() after bot is fully connected
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"{self.user} has connected to Discord!")
        logger.info(f"Bot is in {len(self.guilds)} guild(s)")
        
        # Verify commands are registered
        commands_list = [cmd.name for cmd in self.tree.get_commands()]
        logger.info(f"Commands registered in tree: {commands_list}")
        
        # Sync commands globally and to all guilds when ready
        logger.info("Syncing commands globally and to all guilds...")
        try:
            # Sync globally first (for all servers)
            logger.info("Syncing global commands...")
            synced_global = await self.tree.sync()
            logger.info(f"✅ Synced {len(synced_global)} global command(s): {[cmd.name for cmd in synced_global]}")
            
            # Note: Global commands are available immediately but can take up to 1 hour to appear in all servers
            # Guild-specific syncing is not needed when using global commands
            if len(self.guilds) == 0:
                logger.warning("⚠️ Bot is not in any guilds. Commands will be available when bot is added to a server.")
            else:
                logger.info(f"⚠️ Global commands synced. They may take a few minutes to appear in {len(self.guilds)} guild(s).")
                logger.info("   You can wait or try typing '/' in Discord to see if commands appear.")
        except discord.errors.Forbidden:
            logger.error("❌ Missing permissions to sync global commands. Bot needs 'applications.commands' scope.")
        except discord.errors.HTTPException as e:
            logger.error(f"❌ HTTP error syncing commands: {e.status} - {e.text}")
        except Exception as e:
            logger.error(f"❌ Failed to sync commands: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def on_guild_join(self, guild):
        """Called when the bot joins a guild."""
        logger.info(f"Joined guild: {guild.name} (ID: {guild.id})")
        
        # Sync commands to the new guild immediately
        try:
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            logger.info(f"Synced {len(synced)} command(s) to new guild: {guild.name} (ID: {guild.id})")
        except Exception as e:
            logger.error(f"Failed to sync commands to new guild {guild.name}: {e}")
    
    async def on_guild_remove(self, guild):
        """Called when the bot is removed from a guild."""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")


async def main():
    """Main entry point."""
    # Validate token before creating bot
    if not BOT_TOKEN or not BOT_TOKEN.strip():
        logger.error("❌ DISCORD_BOT_TOKEN is missing or empty!")
        logger.error("   Please check your .env file or environment variables.")
        raise ValueError("DISCORD_BOT_TOKEN is required")
    
    logger.info("Initializing bot...")
    logger.info(f"Token loaded: {len(BOT_TOKEN)} characters")
    
    bot = PopcornBot()
    
    try:
        logger.info("Attempting to connect to Discord...")
        await bot.start(BOT_TOKEN)
    except discord.errors.LoginFailure as e:
        logger.error(f"❌ Discord login failed: {e}")
        logger.error("   This usually means the bot token is incorrect or invalid.")
        logger.error("   Please verify your DISCORD_BOT_TOKEN in the .env file.")
        raise
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        await bot.close()
    except Exception as e:
        logger.error(f"❌ Bot error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await bot.close()
        raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

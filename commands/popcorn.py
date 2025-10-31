"""Popcorn Initiative slash commands."""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from models import InitiativeManager
from helpers import validate_discord_user, has_manager_role, is_current_player_or_manager


class PopcornGroup(app_commands.Group):
    """Popcorn Initiative command group."""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(name="popcorn", description="Popcorn Initiative commands")
        self.bot = bot
        self.initiative_manager = InitiativeManager()


# Pool management commands
class PoolGroup(app_commands.Group):
    """Player pool management commands."""
    
    def __init__(self, bot: commands.Bot, initiative_manager: InitiativeManager):
        super().__init__(name="pool", description="Manage player pool")
        self.bot = bot
        self.initiative_manager = initiative_manager

    @app_commands.command(name="add", description="Add a user to the player pool")
    @app_commands.describe(user="The user to add to the pool")
    async def pool_add(self, interaction: discord.Interaction, user: discord.Member):
        """Add a user to the player pool."""
        try:
            # Check permissions
            if not has_manager_role(interaction.user):
                await interaction.response.send_message(
                    "❌ You need the GM or Popcorn Manager role to manage the player pool.",
                    ephemeral=True
                )
                return

            # Validate user
            validated_member = await validate_discord_user(user, interaction.guild)
            
            # Add to pool
            self.initiative_manager.add_to_pool(
                interaction.guild.id,
                interaction.channel.id,
                validated_member.id
            )
            
            await interaction.response.send_message(
                f"✅ {validated_member.mention} has been added to the player pool."
            )
        except ValueError as e:
            await interaction.response.send_message(f"❌ {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="remove", description="Remove a user from the player pool")
    @app_commands.describe(user="The user to remove from the pool")
    async def pool_remove(self, interaction: discord.Interaction, user: discord.Member):
        """Remove a user from the player pool."""
        try:
            # Check permissions
            if not has_manager_role(interaction.user):
                await interaction.response.send_message(
                    "❌ You need the GM or Popcorn Manager role to manage the player pool.",
                    ephemeral=True
                )
                return

            # Validate user
            validated_member = await validate_discord_user(user, interaction.guild)
            
            # Remove from pool
            self.initiative_manager.remove_from_pool(
                interaction.guild.id,
                interaction.channel.id,
                validated_member.id
            )
            
            await interaction.response.send_message(
                f"✅ {validated_member.mention} has been removed from the player pool."
            )
        except ValueError as e:
            await interaction.response.send_message(f"❌ {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="list", description="List all players in the pool")
    async def pool_list(self, interaction: discord.Interaction):
        """List all players in the player pool."""
        try:
            # Check permissions
            if not has_manager_role(interaction.user):
                await interaction.response.send_message(
                    "❌ You need the GM or Popcorn Manager role to view the player pool.",
                    ephemeral=True
                )
                return

            pool = self.initiative_manager.get_player_pool(
                interaction.guild.id,
                interaction.channel.id
            )
            
            if not pool:
                await interaction.response.send_message(
                    "📋 The player pool is empty."
                )
                return
            
            # Build player list
            player_mentions = []
            for player_id in pool:
                member = interaction.guild.get_member(player_id)
                if member:
                    player_mentions.append(member.mention)
            
            if not player_mentions:
                await interaction.response.send_message(
                    "📋 The player pool is empty (no valid members found)."
                )
                return
            
            player_list = "\n".join(f"• {mention}" for mention in player_mentions)
            await interaction.response.send_message(
                f"📋 **Player Pool** ({len(player_mentions)} players):\n{player_list}"
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}", ephemeral=True
            )

    @app_commands.command(name="clear", description="Clear the entire player pool")
    async def pool_clear(self, interaction: discord.Interaction):
        """Clear the entire player pool."""
        try:
            # Check permissions
            if not has_manager_role(interaction.user):
                await interaction.response.send_message(
                    "❌ You need the GM or Popcorn Manager role to manage the player pool.",
                    ephemeral=True
                )
                return

            self.initiative_manager.clear_pool(
                interaction.guild.id,
                interaction.channel.id
            )
            
            await interaction.response.send_message(
                "✅ The player pool has been cleared."
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}", ephemeral=True
            )


# Initiative management commands
async def popcorn_add(
    interaction: discord.Interaction,
    user: discord.Member,
    initiative_manager: InitiativeManager
):
    """Add a user to the pool and current initiative (if running)."""
    try:
        # Check permissions
        if not has_manager_role(interaction.user):
            await interaction.response.send_message(
                "❌ You need the GM or Popcorn Manager role to add players.",
                ephemeral=True
            )
            return

        # Validate user
        validated_member = await validate_discord_user(user, interaction.guild)
        
        # Add to pool
        initiative_manager.add_to_pool(
            interaction.guild.id,
            interaction.channel.id,
            validated_member.id
        )
        
        # Add to current initiative if running
        initiative = initiative_manager.get_initiative(
            interaction.guild.id,
            interaction.channel.id
        )
        if initiative.is_active():
            initiative.add_to_participants(validated_member.id)
            await interaction.response.send_message(
                f"✅ {validated_member.mention} has been added to the pool and current initiative."
            )
        else:
            await interaction.response.send_message(
                f"✅ {validated_member.mention} has been added to the pool."
            )
    except ValueError as e:
        await interaction.response.send_message(f"❌ {str(e)}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}", ephemeral=True
        )


async def popcorn_start(
    interaction: discord.Interaction,
    user: Optional[discord.Member],
    initiative_manager: InitiativeManager
):
    """Start the initiative."""
    try:
        # Check permissions
        if not has_manager_role(interaction.user):
            await interaction.response.send_message(
                "❌ You need the GM or Popcorn Manager role to start the initiative.",
                ephemeral=True
            )
            return

        # Check if initiative already active
        initiative = initiative_manager.get_initiative(
            interaction.guild.id,
            interaction.channel.id
        )
        if initiative.is_active():
            await interaction.response.send_message(
                "❌ An initiative is already running. Use `/popcorn end` to end it first.",
                ephemeral=True
            )
            return

        # Get pool
        pool = initiative_manager.get_player_pool(
            interaction.guild.id,
            interaction.channel.id
        )
        if not pool:
            await interaction.response.send_message(
                "❌ The player pool is empty. Add players to the pool first.",
                ephemeral=True
            )
            return

        # Validate user if provided
        first_player_id = None
        if user:
            validated_member = await validate_discord_user(user, interaction.guild)
            if validated_member.id not in pool:
                await interaction.response.send_message(
                    f"❌ {validated_member.mention} is not in the player pool.",
                    ephemeral=True
                )
                return
            first_player_id = validated_member.id

        # Initialize initiative
        selected_player_id = initiative_manager.initialize_initiative_from_pool(
            interaction.guild.id,
            interaction.channel.id,
            first_player_id
        )

        if not selected_player_id:
            await interaction.response.send_message(
                "❌ Failed to start initiative.",
                ephemeral=True
            )
            return

        selected_member = interaction.guild.get_member(selected_player_id)
        if selected_member:
            await interaction.response.send_message(
                f"🎬 **Popcorn Initiative Started!**\n"
                f"🎯 {selected_member.mention} goes first!"
            )
        else:
            await interaction.response.send_message(
                f"🎬 **Popcorn Initiative Started!**\n"
                f"🎯 Player ID {selected_player_id} goes first!"
            )
    except ValueError as e:
        await interaction.response.send_message(f"❌ {str(e)}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}", ephemeral=True
        )


async def popcorn_next(
    interaction: discord.Interaction,
    user: Optional[discord.Member],
    initiative_manager: InitiativeManager
):
    """Pass the turn to the next player."""
    try:
        initiative = initiative_manager.get_initiative(
            interaction.guild.id,
            interaction.channel.id
        )

        # Check if initiative is active
        if not initiative.is_active():
            await interaction.response.send_message(
                "❌ No active initiative. Use `/popcorn start` to start one.",
                ephemeral=True
            )
            return

        # Check permissions - must be current player or manager
        can_use = await is_current_player_or_manager(
            interaction.user,
            interaction.guild.id,
            interaction.channel.id,
            initiative_manager
        )
        
        if not can_use:
            current_player_id = initiative.get_current_player()
            current_member = interaction.guild.get_member(current_player_id) if current_player_id else None
            if current_member:
                await interaction.response.send_message(
                    f"❌ Only {current_member.mention} (current player) or a GM/Popcorn Manager can use this command.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Only the current player or a GM/Popcorn Manager can use this command.",
                    ephemeral=True
                )
            return

        # Handle next player selection
        pool = initiative_manager.get_player_pool(
            interaction.guild.id,
            interaction.channel.id
        )

        # If user specified
        if user:
            validated_member = await validate_discord_user(user, interaction.guild)
            
            # If manager is using this and no participants left, start new initiative
            if has_manager_role(interaction.user) and not initiative.has_participants():
                # Start new initiative with this user
                if validated_member.id not in pool:
                    # Add to pool if not already there
                    initiative_manager.add_to_pool(
                        interaction.guild.id,
                        interaction.channel.id,
                        validated_member.id
                    )
                
                initiative_manager.initialize_initiative_from_pool(
                    interaction.guild.id,
                    interaction.channel.id,
                    validated_member.id
                )
                await interaction.response.send_message(
                    f"🔄 **New Initiative Started!**\n"
                    f"🎯 {validated_member.mention} goes first!"
                )
                return
            
            # Check if user is in participants
            if validated_member.id not in initiative.participants:
                if validated_member.id in pool:
                    initiative.add_to_participants(validated_member.id)
                else:
                    await interaction.response.send_message(
                        f"❌ {validated_member.mention} is not in the player pool or initiative participants.",
                        ephemeral=True
                    )
                    return
            
            # Pass to specified user
            initiative.set_current_player(validated_member.id)
            await interaction.response.send_message(
                f"🎯 Turn passed to {validated_member.mention}!"
            )
            return

        # No user specified - random selection
        if not initiative.has_participants():
            # Check if we can start a new initiative
            if not pool:
                # End initiative - pool is empty
                initiative.reset()
                await interaction.response.send_message(
                    "🏁 **Initiative ended** - Player pool is exhausted."
                )
                return
            
            # Start new random initiative
            new_first_player_id = initiative_manager.initialize_initiative_from_pool(
                interaction.guild.id,
                interaction.channel.id,
                None
            )
            
            if new_first_player_id:
                new_member = interaction.guild.get_member(new_first_player_id)
                if new_member:
                    await interaction.response.send_message(
                        f"🔄 **New Initiative Started!**\n"
                        f"🎯 {new_member.mention} goes first!"
                    )
                else:
                    await interaction.response.send_message(
                        f"🔄 **New Initiative Started!**\n"
                        f"🎯 Player ID {new_first_player_id} goes first!"
                    )
            else:
                initiative.reset()
                await interaction.response.send_message(
                    "🏁 **Initiative ended** - Could not start new initiative."
                )
            return

        # Select random participant
        next_player_id = initiative.select_random_participant()
        if next_player_id:
            initiative.set_current_player(next_player_id)
            next_member = interaction.guild.get_member(next_player_id)
            if next_member:
                await interaction.response.send_message(
                    f"🎯 Turn passed to {next_member.mention}!"
                )
            else:
                await interaction.response.send_message(
                    f"🎯 Turn passed to Player ID {next_player_id}!"
                )
        else:
            # This shouldn't happen, but handle it
            initiative.reset()
            await interaction.response.send_message(
                "🏁 **Initiative ended** - No more participants."
            )

    except ValueError as e:
        await interaction.response.send_message(f"❌ {str(e)}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}", ephemeral=True
        )


async def popcorn_end(
    interaction: discord.Interaction,
    initiative_manager: InitiativeManager
):
    """End the current initiative."""
    try:
        # Check permissions
        if not has_manager_role(interaction.user):
            await interaction.response.send_message(
                "❌ You need the GM or Popcorn Manager role to end the initiative.",
                ephemeral=True
            )
            return

        initiative = initiative_manager.get_initiative(
            interaction.guild.id,
            interaction.channel.id
        )

        if not initiative.is_active():
            await interaction.response.send_message(
                "❌ No active initiative to end.",
                ephemeral=True
            )
            return

        initiative.reset()
        await interaction.response.send_message(
            "🏁 **Initiative ended** by manager."
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}", ephemeral=True
        )


async def popcorn_clear(
    interaction: discord.Interaction,
    initiative_manager: InitiativeManager
):
    """Clear initiative brackets."""
    try:
        # Check permissions
        if not has_manager_role(interaction.user):
            await interaction.response.send_message(
                "❌ You need the GM or Popcorn Manager role to clear the initiative.",
                ephemeral=True
            )
            return

        initiative_manager.clear_initiative(
            interaction.guild.id,
            interaction.channel.id
        )
        
        await interaction.response.send_message(
            "✅ Initiative brackets have been cleared."
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}", ephemeral=True
        )


async def popcorn_status(
    interaction: discord.Interaction,
    initiative_manager: InitiativeManager
):
    """Show current initiative status."""
    try:
        initiative = initiative_manager.get_initiative(
            interaction.guild.id,
            interaction.channel.id
        )
        pool = initiative_manager.get_player_pool(
            interaction.guild.id,
            interaction.channel.id
        )

        # Build status message
        status_parts = []
        
        # Pool status
        pool_count = len(pool)
        pool_list = []
        for player_id in list(pool)[:10]:  # Show first 10
            member = interaction.guild.get_member(player_id)
            if member:
                pool_list.append(member.mention)
        if len(pool) > 10:
            pool_list.append(f"... and {len(pool) - 10} more")
        
        if pool_list:
            status_parts.append(f"**Player Pool:** {pool_count} player(s)\n{', '.join(pool_list)}")
        else:
            status_parts.append("**Player Pool:** Empty")

        # Initiative status
        if initiative.is_active():
            current_player_id = initiative.get_current_player()
            current_member = interaction.guild.get_member(current_player_id) if current_player_id else None
            
            status_parts.append("\n**Initiative:** Active")
            
            if current_member:
                status_parts.append(f"**Current Player:** {current_member.mention}")
            elif current_player_id:
                status_parts.append(f"**Current Player:** ID {current_player_id}")
            
            participants = initiative.participants
            if participants:
                participant_list = []
                for player_id in participants[:10]:  # Show first 10
                    member = interaction.guild.get_member(player_id)
                    if member:
                        participant_list.append(member.mention)
                if len(participants) > 10:
                    participant_list.append(f"... and {len(participants) - 10} more")
                
                status_parts.append(f"**Remaining Participants:** {len(participants)} ({', '.join(participant_list)})")
            else:
                status_parts.append("**Remaining Participants:** None")
            
            if initiative.history:
                status_parts.append(f"**Players Acted:** {len(initiative.history)}")
        else:
            status_parts.append("\n**Initiative:** Not active")

        await interaction.response.send_message(
            "📊 **Popcorn Initiative Status**\n\n" + "\n".join(status_parts)
        )
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}", ephemeral=True
        )


"""Validation and permission checking helpers."""
import discord
from discord import Member, User, Guild
from config import GM_ROLE_NAME, POPCORN_MANAGER_ROLE_NAME


async def validate_discord_user(user: User | Member, guild: Guild) -> Member:
    """
    Validate that a user is a valid Discord user in the guild.
    
    Args:
        user: The user to validate
        guild: The guild to check membership in
        
    Returns:
        Member: The validated member object
        
    Raises:
        ValueError: If user is invalid, not in guild, or is a bot
    """
    if not user:
        raise ValueError("User parameter is required.")
    
    # Try to get the member from the guild
    if isinstance(user, Member):
        member = user
    else:
        member = guild.get_member(user.id)
        if not member:
            # Try to fetch if not cached
            try:
                member = await guild.fetch_member(user.id)
            except discord.NotFound:
                raise ValueError(f"User {user.mention} is not a member of this server.")
    
    if not member:
        raise ValueError(f"User {user.mention} is not a member of this server.")
    
    # Check if user is a bot (optional - you may want to allow bots)
    # if member.bot:
    #     raise ValueError(f"User {user.mention} is a bot and cannot participate.")
    
    return member


def has_manager_role(member: Member) -> bool:
    """
    Check if a member has GM or Popcorn Manager role.
    
    Args:
        member: The member to check
        
    Returns:
        bool: True if member has GM or Popcorn Manager role
    """
    if not member:
        return False
    
    role_names = [role.name for role in member.roles]
    return GM_ROLE_NAME in role_names or POPCORN_MANAGER_ROLE_NAME in role_names


async def is_current_player_or_manager(
    member: Member, guild_id: int, channel_id: int, initiative_manager
) -> bool:
    """
    Check if member is the current player OR has manager role.
    
    Args:
        member: The member to check
        guild_id: The guild ID
        channel_id: The channel ID
        initiative_manager: The InitiativeManager instance
        
    Returns:
        bool: True if member is current player or has manager role
    """
    if has_manager_role(member):
        return True
    
    initiative = initiative_manager.get_initiative(guild_id, channel_id)
    if not initiative.is_active():
        return False
    
    return initiative.get_current_player() == member.id


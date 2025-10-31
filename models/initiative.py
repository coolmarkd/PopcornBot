"""Data models for Popcorn Initiative tracking."""
from typing import Optional, Set, List
from dataclasses import dataclass, field
import random


@dataclass
class Initiative:
    """Represents an active Popcorn Initiative instance."""
    current_player_id: Optional[int] = None
    participants: List[int] = field(default_factory=list)
    history: List[int] = field(default_factory=list)

    def get_current_player(self) -> Optional[int]:
        """Get the current player ID."""
        return self.current_player_id

    def is_active(self) -> bool:
        """Check if initiative is active."""
        return self.current_player_id is not None

    def has_participants(self) -> bool:
        """Check if there are remaining participants."""
        return len(self.participants) > 0

    def add_to_participants(self, player_id: int) -> None:
        """Add a player to participants if not already present."""
        if player_id not in self.participants:
            self.participants.append(player_id)

    def remove_from_participants(self, player_id: int) -> None:
        """Remove a player from participants."""
        if player_id in self.participants:
            self.participants.remove(player_id)

    def move_to_history(self, player_id: int) -> None:
        """Move a player from participants to history."""
        self.remove_from_participants(player_id)
        if player_id not in self.history:
            self.history.append(player_id)

    def set_current_player(self, player_id: int) -> None:
        """Set the current player and move them from participants if needed."""
        self.current_player_id = player_id
        self.remove_from_participants(player_id)
        if player_id not in self.history:
            self.history.append(player_id)

    def select_random_participant(self) -> Optional[int]:
        """Randomly select a participant."""
        if not self.participants:
            return None
        return random.choice(self.participants)

    def reset(self) -> None:
        """Reset the initiative to empty state."""
        self.current_player_id = None
        self.participants.clear()
        self.history.clear()


class InitiativeManager:
    """Manages initiative instances by guild and channel."""
    
    def __init__(self):
        # Structure: {(guild_id, channel_id): Initiative}
        self._initiatives: dict[tuple[int, int], Initiative] = {}
        # Structure: {(guild_id, channel_id): Set[player_id]}
        self._player_pools: dict[tuple[int, int], Set[int]] = {}

    def get_key(self, guild_id: int, channel_id: int) -> tuple[int, int]:
        """Get the key for guild/channel combination."""
        return (guild_id, channel_id)

    def get_initiative(self, guild_id: int, channel_id: int) -> Initiative:
        """Get or create initiative for a guild/channel."""
        key = self.get_key(guild_id, channel_id)
        if key not in self._initiatives:
            self._initiatives[key] = Initiative()
        return self._initiatives[key]

    def clear_initiative(self, guild_id: int, channel_id: int) -> None:
        """Clear initiative for a guild/channel."""
        key = self.get_key(guild_id, channel_id)
        if key in self._initiatives:
            self._initiatives[key].reset()

    def remove_initiative(self, guild_id: int, channel_id: int) -> None:
        """Remove initiative for a guild/channel."""
        key = self.get_key(guild_id, channel_id)
        if key in self._initiatives:
            del self._initiatives[key]

    def get_player_pool(self, guild_id: int, channel_id: int) -> Set[int]:
        """Get player pool for a guild/channel."""
        key = self.get_key(guild_id, channel_id)
        if key not in self._player_pools:
            self._player_pools[key] = set()
        return self._player_pools[key]

    def add_to_pool(self, guild_id: int, channel_id: int, player_id: int) -> None:
        """Add player to pool."""
        pool = self.get_player_pool(guild_id, channel_id)
        pool.add(player_id)

    def remove_from_pool(self, guild_id: int, channel_id: int, player_id: int) -> None:
        """Remove player from pool."""
        pool = self.get_player_pool(guild_id, channel_id)
        pool.discard(player_id)

    def clear_pool(self, guild_id: int, channel_id: int) -> None:
        """Clear player pool for a guild/channel."""
        key = self.get_key(guild_id, channel_id)
        if key in self._player_pools:
            self._player_pools[key].clear()

    def initialize_initiative_from_pool(
        self, guild_id: int, channel_id: int, first_player_id: Optional[int] = None
    ) -> Optional[int]:
        """Initialize initiative from pool. Returns the first player ID."""
        pool = self.get_player_pool(guild_id, channel_id)
        if not pool:
            return None

        initiative = self.get_initiative(guild_id, channel_id)
        
        # Set participants from pool
        initiative.participants = list(pool)
        
        # Select first player
        if first_player_id and first_player_id in pool:
            player_id = first_player_id
        else:
            player_id = random.choice(list(pool))
        
        initiative.set_current_player(player_id)
        return player_id


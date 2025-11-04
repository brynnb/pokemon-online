"""
Configuration for Pokemon map data export scripts.

This module contains constants and configuration values used across multiple export scripts.
"""

# Tileset Aliases
# Maps tileset IDs to their alias IDs when they share the same graphics.
# Format: {original_tileset_id: aliased_tileset_id}
TILESET_ALIASES = {
    5: 7,  # DOJO -> GYM (DOJO uses same graphics as GYM)
    2: 6,  # MART -> POKECENTER (Marts and Pokecenters share similar interior graphics)
}


def get_tileset_alias(tileset_id):
    """
    Get the aliased tileset ID for a given tileset ID.

    Args:
        tileset_id: The original tileset ID

    Returns:
        The aliased tileset ID if one exists, otherwise the original tileset ID
    """
    return TILESET_ALIASES.get(tileset_id, tileset_id)


def get_reverse_aliases(tileset_id):
    """
    Get all tileset IDs that alias to the given tileset ID.

    Args:
        tileset_id: The target tileset ID

    Returns:
        A list of tileset IDs that alias to the target tileset ID
    """
    return [source_id for source_id, target_id in TILESET_ALIASES.items() if target_id == tileset_id]

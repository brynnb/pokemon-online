"""
Centralized configuration for Pokemon export scripts.

This module provides centralized paths and constants used across all export scripts,
making it easier to maintain and update common configuration values.
"""

from pathlib import Path

# Project structure
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "pokemon.db"

# Pokemon game data paths
GAME_DATA_ROOT = PROJECT_ROOT / "pokemon-game-data"
MAPS_DIR = GAME_DATA_ROOT / "maps"
MAP_HEADERS_DIR = GAME_DATA_ROOT / "data/maps/headers"
MAP_CONSTANTS_FILE = GAME_DATA_ROOT / "constants/map_constants.asm"
TILESETS_DIR = GAME_DATA_ROOT / "gfx/tilesets"
BLOCKSETS_DIR = GAME_DATA_ROOT / "gfx/blocksets"
TILESET_CONSTANTS_FILE = GAME_DATA_ROOT / "constants/tileset_constants.asm"
COLLISION_TILE_IDS_FILE = GAME_DATA_ROOT / "data/tilesets/collision_tile_ids.asm"

# Pokemon data directories
POKEMON_DATA_DIR = GAME_DATA_ROOT / "data/pokemon"
BASE_STATS_DIR = POKEMON_DATA_DIR / "base_stats"
POKEDEX_CONSTANTS_FILE = GAME_DATA_ROOT / "constants/pokedex_constants.asm"

# Items data
ITEMS_DATA_DIR = GAME_DATA_ROOT / "data/items"

# Moves data
MOVES_DATA_DIR = GAME_DATA_ROOT / "data/moves"

# Map objects data
MAP_OBJECTS_DIR = GAME_DATA_ROOT / "data/maps/objects"

# Constants directory
CONSTANTS_DIR = GAME_DATA_ROOT / "constants"

# Export settings
TILE_IMAGES_DIR = "tile_images"
BATCH_SIZE = 1000

# GameBoy color palette (white, light gray, dark gray, black)
GAMEBOY_PALETTE = [(255, 255, 255), (192, 192, 192), (96, 96, 96), (0, 0, 0)]

# Tileset aliases
# Some tilesets share the same graphics in the original game
TILESET_ALIASES = {
    5: 7,   # DOJO -> GYM
    2: 6    # MART -> POKECENTER
}

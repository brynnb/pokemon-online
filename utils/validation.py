"""
Data validation utilities for Pokemon game data export.

This module provides validation functions for all extracted data to ensure
data integrity and catch errors early in the export process.
"""

import logging
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors"""

    pass


def validate_map_data(map_data: Dict[str, Any]) -> List[str]:
    """
    Validate map data is complete and correct.

    Args:
        map_data: Dictionary containing map information with keys:
            - name: Map name (required)
            - width: Map width in blocks (required, > 0)
            - height: Map height in blocks (required, > 0)
            - tileset_id: ID of the tileset (required)
            - blk_data: Block data bytes (optional, but validated if present)

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # Check required fields
    if not map_data.get("name"):
        errors.append("Map has no name")

    if not map_data.get("tileset_id") and map_data.get("tileset_id") != 0:
        errors.append(f"Map {map_data.get('name', 'UNKNOWN')} has no tileset_id")

    # Validate dimensions
    width = map_data.get("width", 0)
    height = map_data.get("height", 0)

    if width <= 0 or height <= 0:
        errors.append(
            f"Map {map_data.get('name', 'UNKNOWN')} has invalid dimensions: {width}x{height}"
        )

    # Validate block data if present
    blk_data = map_data.get("blk_data")
    if blk_data and width > 0 and height > 0:
        expected_blocks = width * height
        actual_blocks = len(blk_data)
        if actual_blocks != expected_blocks:
            errors.append(
                f"Map {map_data.get('name', 'UNKNOWN')} block count mismatch: "
                f"expected {expected_blocks}, got {actual_blocks}"
            )

    return errors


def validate_tileset_data(tileset_data: Dict[str, Any]) -> List[str]:
    """
    Validate tileset data is complete and correct.

    Args:
        tileset_data: Dictionary containing tileset information with keys:
            - name: Tileset name (required)
            - tileset_id: Tileset ID (required)
            - blockset_path: Path to blockset file (optional)
            - tileset_path: Path to tileset file (optional)

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    if not tileset_data.get("name"):
        errors.append("Tileset has no name")

    tileset_id = tileset_data.get("tileset_id")
    if tileset_id is None:
        errors.append(f"Tileset {tileset_data.get('name', 'UNKNOWN')} has no ID")
    elif tileset_id < 0 or tileset_id > 100:
        errors.append(
            f"Tileset {tileset_data.get('name', 'UNKNOWN')} has invalid ID: {tileset_id}"
        )

    return errors


def validate_pokemon_data(pokemon_data: Dict[str, Any]) -> List[str]:
    """
    Validate Pokemon data is complete and correct.

    Args:
        pokemon_data: Dictionary containing Pokemon information with keys:
            - id: Pokedex number (required, 1-151 for Gen 1)
            - name: Pokemon name (required)
            - hp, atk, def, spd, spc: Base stats (required, 1-255)
            - type_1, type_2: Pokemon types (required)
            - catch_rate: Catch rate (required, 0-255)
            - base_exp: Base experience (required, 0-255)

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # Validate ID
    pokemon_id = pokemon_data.get("id")
    if pokemon_id is None:
        errors.append(f"Pokemon {pokemon_data.get('name', 'UNKNOWN')} has no ID")
    elif pokemon_id < 1 or pokemon_id > 151:
        errors.append(
            f"Pokemon {pokemon_data.get('name', 'UNKNOWN')} has invalid ID: {pokemon_id}"
        )

    # Validate name
    if not pokemon_data.get("name"):
        errors.append(f"Pokemon with ID {pokemon_id} has no name")

    # Validate base stats
    stats = ["hp", "atk", "def", "spd", "spc"]
    for stat in stats:
        value = pokemon_data.get(stat)
        if value is None:
            errors.append(
                f"Pokemon {pokemon_data.get('name', 'UNKNOWN')} missing stat: {stat}"
            )
        elif not isinstance(value, int) or value < 1 or value > 255:
            errors.append(
                f"Pokemon {pokemon_data.get('name', 'UNKNOWN')} has invalid {stat}: {value}"
            )

    # Validate types
    valid_types = {
        "NORMAL",
        "FIGHTING",
        "FLYING",
        "POISON",
        "GROUND",
        "ROCK",
        "BUG",
        "GHOST",
        "FIRE",
        "WATER",
        "GRASS",
        "ELECTRIC",
        "PSYCHIC",
        "ICE",
        "DRAGON",
    }

    for type_field in ["type_1", "type_2"]:
        poke_type = pokemon_data.get(type_field)
        if not poke_type:
            errors.append(
                f"Pokemon {pokemon_data.get('name', 'UNKNOWN')} missing {type_field}"
            )
        elif poke_type not in valid_types:
            errors.append(
                f"Pokemon {pokemon_data.get('name', 'UNKNOWN')} has invalid {type_field}: {poke_type}"
            )

    # Validate catch rate
    catch_rate = pokemon_data.get("catch_rate")
    if catch_rate is None:
        errors.append(
            f"Pokemon {pokemon_data.get('name', 'UNKNOWN')} missing catch_rate"
        )
    elif not isinstance(catch_rate, int) or catch_rate < 0 or catch_rate > 255:
        errors.append(
            f"Pokemon {pokemon_data.get('name', 'UNKNOWN')} has invalid catch_rate: {catch_rate}"
        )

    # Validate base exp
    base_exp = pokemon_data.get("base_exp")
    if base_exp is None:
        errors.append(
            f"Pokemon {pokemon_data.get('name', 'UNKNOWN')} missing base_exp"
        )
    elif not isinstance(base_exp, int) or base_exp < 0 or base_exp > 255:
        errors.append(
            f"Pokemon {pokemon_data.get('name', 'UNKNOWN')} has invalid base_exp: {base_exp}"
        )

    return errors


def validate_move_data(move_data: Dict[str, Any]) -> List[str]:
    """
    Validate move data is complete and correct.

    Args:
        move_data: Dictionary containing move information with keys:
            - id: Move ID (required, 1-165 for Gen 1)
            - name: Move name (required)
            - power: Move power (required, 0-255, 0 for status moves)
            - accuracy: Move accuracy (required, 0-100)
            - pp: Power points (required, 1-40)
            - type: Move type (required)

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # Validate ID
    move_id = move_data.get("id")
    if move_id is None:
        errors.append(f"Move {move_data.get('name', 'UNKNOWN')} has no ID")
    elif move_id < 1 or move_id > 165:
        errors.append(
            f"Move {move_data.get('name', 'UNKNOWN')} has invalid ID: {move_id}"
        )

    # Validate name
    if not move_data.get("name"):
        errors.append(f"Move with ID {move_id} has no name")

    # Validate power
    power = move_data.get("power")
    if power is None:
        errors.append(f"Move {move_data.get('name', 'UNKNOWN')} missing power")
    elif not isinstance(power, int) or power < 0 or power > 255:
        errors.append(
            f"Move {move_data.get('name', 'UNKNOWN')} has invalid power: {power}"
        )

    # Validate accuracy
    accuracy = move_data.get("accuracy")
    if accuracy is None:
        errors.append(f"Move {move_data.get('name', 'UNKNOWN')} missing accuracy")
    elif not isinstance(accuracy, int) or accuracy < 0 or accuracy > 255:
        errors.append(
            f"Move {move_data.get('name', 'UNKNOWN')} has invalid accuracy: {accuracy}"
        )

    # Validate PP
    pp = move_data.get("pp")
    if pp is None:
        errors.append(f"Move {move_data.get('name', 'UNKNOWN')} missing pp")
    elif not isinstance(pp, int) or pp < 1 or pp > 40:
        errors.append(f"Move {move_data.get('name', 'UNKNOWN')} has invalid pp: {pp}")

    # Validate type
    valid_types = {
        "NORMAL",
        "FIGHTING",
        "FLYING",
        "POISON",
        "GROUND",
        "ROCK",
        "BUG",
        "GHOST",
        "FIRE",
        "WATER",
        "GRASS",
        "ELECTRIC",
        "PSYCHIC",
        "ICE",
        "DRAGON",
    }

    move_type = move_data.get("type")
    if not move_type:
        errors.append(f"Move {move_data.get('name', 'UNKNOWN')} missing type")
    elif move_type not in valid_types:
        errors.append(
            f"Move {move_data.get('name', 'UNKNOWN')} has invalid type: {move_type}"
        )

    return errors


def validate_item_data(item_data: Dict[str, Any]) -> List[str]:
    """
    Validate item data is complete and correct.

    Args:
        item_data: Dictionary containing item information with keys:
            - id: Item ID (required, 1-255 for Gen 1)
            - name: Item name (required)
            - short_name: Short item name (required)
            - price: Item price (optional, >= 0 if present)

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # Validate ID
    item_id = item_data.get("id")
    if item_id is None:
        errors.append(f"Item {item_data.get('name', 'UNKNOWN')} has no ID")
    elif item_id < 1 or item_id > 255:
        errors.append(
            f"Item {item_data.get('name', 'UNKNOWN')} has invalid ID: {item_id}"
        )

    # Validate name
    if not item_data.get("name"):
        errors.append(f"Item with ID {item_id} has no name")

    # Validate short_name
    if not item_data.get("short_name"):
        errors.append(f"Item {item_data.get('name', 'UNKNOWN')} has no short_name")

    # Validate price (if present)
    price = item_data.get("price")
    if price is not None:
        if not isinstance(price, int) or price < 0:
            errors.append(
                f"Item {item_data.get('name', 'UNKNOWN')} has invalid price: {price}"
            )

    return errors


def validate_object_data(object_data: Dict[str, Any]) -> List[str]:
    """
    Validate object (NPC/item) data is complete and correct.

    Args:
        object_data: Dictionary containing object information with keys:
            - name: Object name (required)
            - map_id: Map ID where object is located (required)
            - object_type: Type of object (required: 'npc', 'item', 'sign')
            - local_x, local_y: Local coordinates (required, >= 0)
            - sprite_name: Sprite name (required)

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # Validate name
    if not object_data.get("name"):
        errors.append("Object has no name")

    # Validate map_id
    map_id = object_data.get("map_id")
    if map_id is None:
        errors.append(f"Object {object_data.get('name', 'UNKNOWN')} has no map_id")

    # Validate object_type
    valid_types = {"npc", "item", "sign"}
    object_type = object_data.get("object_type")
    if not object_type:
        errors.append(f"Object {object_data.get('name', 'UNKNOWN')} has no object_type")
    elif object_type not in valid_types:
        errors.append(
            f"Object {object_data.get('name', 'UNKNOWN')} has invalid object_type: {object_type}"
        )

    # Validate coordinates
    for coord in ["local_x", "local_y"]:
        value = object_data.get(coord)
        if value is None:
            errors.append(
                f"Object {object_data.get('name', 'UNKNOWN')} missing {coord}"
            )
        elif not isinstance(value, int) or value < 0:
            errors.append(
                f"Object {object_data.get('name', 'UNKNOWN')} has invalid {coord}: {value}"
            )

    # Validate sprite_name
    if not object_data.get("sprite_name"):
        errors.append(f"Object {object_data.get('name', 'UNKNOWN')} has no sprite_name")

    return errors


def validate_warp_data(warp_data: Dict[str, Any]) -> List[str]:
    """
    Validate warp data is complete and correct.

    Args:
        warp_data: Dictionary containing warp information with keys:
            - source_map: Source map name (required)
            - source_map_id: Source map ID (optional but validated if present)
            - source_x, source_y: Source coordinates (required, >= 0)
            - destination_map: Destination map name (required)
            - destination_warp_id: Destination warp ID (required, >= 0)

    Returns:
        List of error messages (empty if validation passes)
    """
    errors = []

    # Validate source map
    if not warp_data.get("source_map"):
        errors.append("Warp has no source_map")

    # Validate source coordinates
    for coord in ["source_x", "source_y"]:
        value = warp_data.get(coord)
        if value is None:
            errors.append(
                f"Warp from {warp_data.get('source_map', 'UNKNOWN')} missing {coord}"
            )
        elif not isinstance(value, int) or value < 0:
            errors.append(
                f"Warp from {warp_data.get('source_map', 'UNKNOWN')} has invalid {coord}: {value}"
            )

    # Validate destination map
    if not warp_data.get("destination_map"):
        errors.append(
            f"Warp from {warp_data.get('source_map', 'UNKNOWN')} has no destination_map"
        )

    # Validate destination warp ID
    dest_warp_id = warp_data.get("destination_warp_id")
    if dest_warp_id is None:
        errors.append(
            f"Warp from {warp_data.get('source_map', 'UNKNOWN')} has no destination_warp_id"
        )
    elif not isinstance(dest_warp_id, int) or dest_warp_id < 0:
        errors.append(
            f"Warp from {warp_data.get('source_map', 'UNKNOWN')} has invalid destination_warp_id: {dest_warp_id}"
        )

    return errors


def log_validation_errors(errors: List[str], data_type: str) -> None:
    """
    Log validation errors with appropriate severity.

    Args:
        errors: List of error messages
        data_type: Type of data being validated (for logging context)
    """
    if errors:
        logger.warning(f"Validation errors for {data_type}:")
        for error in errors:
            logger.warning(f"  - {error}")


def validate_and_log(
    data: Dict[str, Any], validator_func, data_type: str
) -> List[str]:
    """
    Validate data using provided validator and log any errors.

    Args:
        data: Data to validate
        validator_func: Validation function to use
        data_type: Type of data (for logging)

    Returns:
        List of validation errors
    """
    errors = validator_func(data)
    if errors:
        log_validation_errors(errors, data_type)
    return errors

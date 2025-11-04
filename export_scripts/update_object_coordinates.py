#!/usr/bin/env python3
"""
Update Object Coordinates

This script updates the global coordinates (x, y) of objects in the database
based on their local coordinates (local_x, local_y) and the position of their map.

Coordinate System:
- For overworld maps (is_overworld = 1), global coordinates are calculated by adding
  the map's offset to the local coordinates. The map's offset is determined by the
  global coordinates of the (0,0) local coordinates in that map.
- For non-overworld maps (is_overworld = 0), global coordinates are the same as
  local coordinates.

This ensures that objects in the overworld have consistent global coordinates
that match the global coordinate system of the tiles.
"""

import sqlite3
import time
from pathlib import Path
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Constants
# Get the project root directory (parent of the script's directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "pokemon.db"


def get_map_positions(cursor):
    """Get the positions of all maps"""
    # For overworld maps, get the global coordinates of the (0,0) local coordinates
    cursor.execute(
        """
        SELECT m.id, t.x, t.y
        FROM maps m
        JOIN tiles t ON m.id = t.map_id
        WHERE m.is_overworld = 1 AND t.local_x = 0 AND t.local_y = 0
        GROUP BY m.id
        """
    )
    return {map_id: (x, y) for map_id, x, y in cursor.fetchall()}


def update_object_coordinates(conn):
    """Update the global coordinates of objects based on their map's position"""
    cursor = conn.cursor()

    # Get map positions for overworld maps
    map_positions = get_map_positions(cursor)

    # Update object coordinates for overworld maps
    total_updated = 0
    for map_id, (offset_x, offset_y) in map_positions.items():
        cursor.execute(
            """
            UPDATE objects
            SET x = local_x + ?,
                y = local_y + ?
            WHERE map_id = ?
            """,
            (offset_x, offset_y, map_id),
        )
        total_updated += cursor.rowcount

    # For non-overworld maps, set global coordinates equal to local coordinates
    cursor.execute(
        """
        UPDATE objects
        SET x = local_x,
            y = local_y
        WHERE map_id IN (
            SELECT id FROM maps WHERE is_overworld = 0
        )
        """
    )
    total_updated += cursor.rowcount

    conn.commit()
    return total_updated


def check_prerequisites():
    """Verify required tables exist before running this script"""
    if not DB_PATH.exists():
        logger.error(f"Database not found at {DB_PATH}")
        logger.error("Run export_map.py first to create the database")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    required_tables = ['objects', 'maps', 'tiles']
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    existing_tables = {row[0] for row in cursor.fetchall()}

    missing = set(required_tables) - existing_tables
    if missing:
        logger.error(f"Missing required tables: {', '.join(sorted(missing))}")
        if 'objects' in missing:
            logger.error("Run export_objects.py first to create the objects table")
        if 'maps' in missing:
            logger.error("Run export_map.py first to create the maps table")
        if 'tiles' in missing:
            logger.error("Run create_zones_and_tiles.py first to create the tiles table")
        conn.close()
        return False

    conn.close()
    return True


def main():
    """Main function"""
    if not check_prerequisites():
        sys.exit(1)

    # Connect to the database
    conn = sqlite3.connect(DB_PATH)

    # Update object coordinates
    updated_count = update_object_coordinates(conn)

    # Close the connection
    conn.close()

    print(f"Successfully updated coordinates for {updated_count} objects")


if __name__ == "__main__":
    main()

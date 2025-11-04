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

Usage:
    python update_object_coordinates.py [--dry-run]
"""

import sqlite3
import time
from pathlib import Path
import argparse

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


def update_object_coordinates(conn, dry_run=False):
    """Update the global coordinates of objects based on their map's position"""
    cursor = conn.cursor()

    # Get map positions for overworld maps
    map_positions = get_map_positions(cursor)

    if dry_run:
        print(f"DRY RUN: Would update objects for {len(map_positions)} overworld maps")
        # Count non-overworld objects
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM objects
            WHERE map_id IN (SELECT id FROM maps WHERE is_overworld = 0)
            """
        )
        non_overworld_count = cursor.fetchone()[0]
        # Count overworld objects
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM objects
            WHERE map_id IN (SELECT id FROM maps WHERE is_overworld = 1)
            """
        )
        overworld_count = cursor.fetchone()[0]
        return overworld_count + non_overworld_count

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


def main(dry_run=False):
    """Main function"""
    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No database changes will be made")
        print("=" * 60)
        print()

    # Connect to the database
    conn = sqlite3.connect(DB_PATH)

    # Update object coordinates
    updated_count = update_object_coordinates(conn, dry_run)

    # Close the connection
    conn.close()

    if dry_run:
        print(f"\nDRY RUN SUMMARY:")
        print(f"  - Would update coordinates for {updated_count} objects")
        print("\nDRY RUN: No changes were made to the database")
    else:
        print(f"Successfully updated coordinates for {updated_count} objects")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update object coordinates in the database"
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Parse data but do not write to database')
    args = parser.parse_args()
    main(dry_run=args.dry_run)

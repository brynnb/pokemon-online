import sqlite3
import sys
from pathlib import Path
import argparse

# Get the project root directory (parent of the script's directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "pokemon.db"


def update_overworld_tiles(dry_run=False):
    """Update tiles to mark them as overworld based on their map's is_overworld flag"""
    if dry_run:
        print("=" * 60)
        print("DRY RUN MODE - No database changes will be made")
        print("=" * 60)
        print()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all maps marked as overworld
    cursor.execute("SELECT id, name FROM maps WHERE is_overworld = 1")
    overworld_maps = cursor.fetchall()

    if not overworld_maps:
        print("No maps marked as overworld found in the database.")
        conn.close()
        return

    print(f"Found {len(overworld_maps)} maps marked as overworld:")
    for map_id, map_name in overworld_maps:
        print(f"  - Map {map_id}: {map_name}")

    # Count tiles in overworld maps
    cursor.execute(
        """
        SELECT COUNT(*) FROM tiles
        WHERE map_id IN (SELECT id FROM maps WHERE is_overworld = 1)
        """
    )
    total_tiles = cursor.fetchone()[0]

    if total_tiles == 0:
        print("No tiles found in overworld maps.")
        conn.close()
        return

    print(f"Found {total_tiles} tiles in overworld maps.")

    if dry_run:
        print(f"\nDRY RUN SUMMARY:")
        print(f"  - Would update {total_tiles} tiles to be marked as overworld")
        print("\nDRY RUN: No changes were made to the database")
        conn.close()
        return

    # Update tiles to mark them as overworld
    cursor.execute(
        """
        UPDATE tiles
        SET is_overworld = 1
        WHERE map_id IN (SELECT id FROM maps WHERE is_overworld = 1)
        """
    )

    # Commit the changes
    conn.commit()

    # Verify the update
    cursor.execute("SELECT COUNT(*) FROM tiles WHERE is_overworld = 1")
    updated_tiles = cursor.fetchone()[0]

    print(f"Updated {updated_tiles} tiles to be marked as overworld.")

    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update overworld tiles in the database"
    )
    parser.add_argument('--dry-run', action='store_true',
                       help='Parse data but do not write to database')
    args = parser.parse_args()
    update_overworld_tiles(dry_run=args.dry_run)

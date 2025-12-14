import os
from pathlib import Path
import shutil

dbPath = Path(__file__).parent / "database" / "database.db"

uploadsDir = Path(__file__).parent / "uploads"

def clear_database():
    """Delete the database file."""
    if dbPath.exists():
        os.remove(dbPath)
        print("Database cleared.")
    else:
        print("No database file found to clear.")
    
def clear_uploads():
    if uploadsDir.exists():
        shutil.rmtree(uploadsDir, ignore_errors=True)
    else:
        print("No uploads directory found to clear.")
    print("Uploads directory cleared.")

def clear_all():
    clear_database()
    clear_uploads()
    print("All data cleared.")

if __name__ == "__main__":
    clear_all()

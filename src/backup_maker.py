import shutil
import datetime
from pathlib import Path
import os

def make_backup():
    base_path = Path()
    backups = Path("backups")
    backup_path = base_path / backups

    if not os.path.exists(backup_path):
        os.mkdir(backup_path)

    today = datetime.datetime.today().strftime("%Y.%m.%d-%H.%M.%S")

    shutil.copy2("database.db", backup_path / f"database-backup-{today}.db")

if __name__ == "__main__":
    make_backup()
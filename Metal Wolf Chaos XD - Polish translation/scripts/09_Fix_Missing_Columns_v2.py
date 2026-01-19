# scripts/09_Fix_Missing_Columns.py (Wersja v2 - Universal)
import sqlite3
from pathlib import Path

WORK_DB = Path("../work/texts_may30_PL.db")
GAME_DB = Path("/home/vertikal/Games/Heroic/Metal Wolf Chaos XD/Media/Texts/texts_may30.db")

def fix_all_structures():
    print("🏗️  Inicjacja TOTALNEGO upgrade'u struktury...")
    conn_work = sqlite3.connect(WORK_DB)
    conn_game = sqlite3.connect(GAME_DB)
    cursor_work = conn_work.cursor()
    cursor_game = conn_game.cursor()

    # Pobierz wszystkie tabele z Twojej bazy (oprócz credits i sqlite)
    cursor_work.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor_work.fetchall() if not t[0].startswith(('sqlite', 'credits'))]

    for table in tables:
        # Sprawdzamy jakie kolumny PL masz u siebie
        cursor_work.execute(f"PRAGMA table_info({table})")
        work_cols = [c[1] for c in cursor_work.fetchall()]
        
        # Sprawdzamy jakie kolumny są w grze
        cursor_game.execute(f"PRAGMA table_info({table})")
        game_cols = [c[1] for c in cursor_game.fetchall()]

        for col in work_cols:
            if "_pl_PL" in col:
                ru_col = col.replace("_pl_PL", "_ru_RU")
                if ru_col not in game_cols:
                    print(f"➕ Dodaję brakującą kolumnę {ru_col} do tabeli {table}")
                    try:
                        cursor_game.execute(f"ALTER TABLE {table} ADD COLUMN {ru_col} TEXT")
                    except Exception as e:
                        print(f"  ❌ Błąd: {e}")

    conn_game.commit()
    print("\n✅ Wszystkie tabele w bazie gry są teraz gotowe na przyjęcie polskiego tekstu.")
    conn_work.close()
    conn_game.close()

if __name__ == "__main__":
    fix_all_structures()

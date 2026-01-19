import sqlite3
import shutil
from pathlib import Path

# --- KONFIGURACJA ŚCIEŻEK ---
# Baza z Twoim gotowym tłumaczeniem
WORK_DB = Path("../work/texts_may30_PL.db")
# Baza w folderze gry, którą Heroic odpala
GAME_DB = Path("/home/vertikal/Games/Heroic/Metal Wolf Chaos XD/Media/Texts/texts_may30.db")

def infiltrate():
    print("🦅 Operacja 'RUSKI ŁĄCZNIK' - Inicjacja...")
    
    if not WORK_DB.exists():
        print(f"❌ Błąd: Nie znaleziono Twojej bazy tłumaczenia w {WORK_DB}")
        return

    # 1. Backup bazy gry przed zmianami
    backup = GAME_DB.with_suffix(".db.bak_russian_trick")
    if not backup.exists():
        shutil.copy2(GAME_DB, backup)
        print(f"✅ Zrobiono backup gry: {backup.name}")

    # 2. Połączenie
    conn_work = sqlite3.connect(WORK_DB)
    cursor_work = conn_work.cursor()
    
    conn_game = sqlite3.connect(GAME_DB)
    cursor_game = conn_game.cursor()

    # Tabele do przetworzenia
    tables = ["menu", "weapon", "maps", "item", "accessory", "creature", "game", "magic", "stage"]

    total_updated = 0

    for table in tables:
        try:
            # Sprawdzamy jakie kolumny masz u siebie w 'work'
            cursor_work.execute(f"PRAGMA table_info({table})")
            work_cols = [c[1] for c in cursor_work.fetchall()]
            
            # Szukamy Twojej kolumny źródłowej (np. Value_pl_PL)
            pl_col = next((c for c in work_cols if "_pl_PL" in c), None)
            
            if not pl_col:
                continue

            # Ustalamy nazwę kolumny ROSYJSKIEJ (cel w grze)
            # Jeśli źródło to Value_pl_PL, cel to Value_ru_RU
            # Jeśli źródło to Name_pl_PL, cel to Name_ru_RU
            ru_col = pl_col.replace("_pl_PL", "_ru_RU")
            
            print(f"📦 Tabela {table:10} | Przenoszę: {pl_col} -> {ru_col}")

            # Pobierz dane PL z bazy roboczej
            cursor_work.execute(f"SELECT StringID, {pl_col} FROM {table} WHERE {pl_col} IS NOT NULL")
            rows = cursor_work.fetchall()

            # Wstrzyknij do bazy gry w miejsce rosyjskiego
            for string_id, text_pl in rows:
                cursor_game.execute(f"UPDATE {table} SET {ru_col} = ? WHERE StringID = ?", (text_pl, string_id))
                total_updated += 1
                
        except Exception as e:
            print(f"  ⚠️ Problem z tabelą {table}: {e}")

    conn_game.commit()
    conn_work.close()
    conn_game.close()
    
    print(f"\n✨ GOTOWE! Wstrzyknięto {total_updated} linii tekstu.")
    print(f"🚀 TERAZ: Odpal Heroic, ustaw język RUSSIAN i sprawdź grę.")

if __name__ == "__main__":
    infiltrate()

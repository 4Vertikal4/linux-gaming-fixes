# scripts/08_Final_Remap_Infiltrator.py (Wersja v4 - Pełna Infiltracja)
import sqlite3
import shutil
from pathlib import Path

WORK_DB = Path("../work/texts_may30_PL.db")
GAME_DB = Path("/home/vertikal/Games/Heroic/Metal Wolf Chaos XD/Media/Texts/texts_may30.db")

REMAP_MAP = {
    'Ą': 'Ä', 'ą': 'ä', 'Ć': 'Ç', 'ć': 'ç', 'Ę': 'Ë', 'ę': 'ë',
    'Ł': 'Í', 'ł': 'í', 'Ń': 'Ñ', 'ń': 'ñ', 'Ó': 'Ö', 'ó': 'ö',
    'Ś': 'Ã', 'ś': 'ã', 'Ź': 'Â', 'ź': 'â', 'Ż': 'À', 'ż': 'à'
}

def remap_text(text):
    if text is None: return None
    for pl, sacrifice in REMAP_MAP.items():
        text = text.replace(pl, sacrifice)
    return text

def infiltrate():
    print("🦅 Inicjacja PEŁNEGO Remappingu (v4)...")
    conn_work = sqlite3.connect(WORK_DB)
    conn_game = sqlite3.connect(GAME_DB)
    cursor_work = conn_work.cursor()
    cursor_game = conn_game.cursor()

    # Automatycznie pobierz WSZYSTKIE tabele z bazy roboczej
    cursor_work.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor_work.fetchall() if not t[0].startswith('sqlite')]

    total_count = 0
    for table in tables:
        try:
            cursor_work.execute(f"PRAGMA table_info({table})")
            work_cols = [c[1] for c in cursor_work.fetchall()]
            pl_col = next((c for c in work_cols if "_pl_PL" in c), None)
            if not pl_col: continue

            ru_col = pl_col.replace("_pl_PL", "_ru_RU")
            
            # Sprawdź czy w grze istnieje kolumna ru_RU
            cursor_game.execute(f"PRAGMA table_info({table})")
            game_cols = [c[1] for c in cursor_game.fetchall()]
            
            if ru_col not in game_cols:
                print(f"  ❌ Skip {table}: Brak kolumny {ru_col} w grze.")
                continue

            print(f"📦 Przetwarzanie {table:10} | {pl_col} -> {ru_col}")
            cursor_work.execute(f"SELECT StringID, {pl_col} FROM {table} WHERE {pl_col} IS NOT NULL")
            for string_id, text_pl in cursor_work.fetchall():
                cursor_game.execute(f"UPDATE {table} SET {ru_col} = ? WHERE StringID = ?", (remap_text(text_pl), string_id))
                total_count += 1
        except Exception as e:
            print(f"  ⚠️  Błąd w {table}: {e}")

    conn_game.commit()
    print(f"\n✨ GOTOWE! Wstrzyknięto {total_count} linii do wszystkich dostępnych tabel.")
    conn_work.close()
    conn_game.close()

if __name__ == "__main__":
    infiltrate()

import sqlite3
import shutil
from pathlib import Path

# --- KONFIGURACJA ---
WORK_DB = Path("../work/texts_may30_PL.db")
GAME_DB = Path("/home/vertikal/Games/Heroic/Metal Wolf Chaos XD/Media/Texts/texts_may30.db")

# TWOJA OFICJALNA MAPA PODMIAN (V3 - Fix Kerningu dla Ł)
REMAP_MAP = {
    'Ą': 'Ä', 'ą': 'ä',
    'Ć': 'Ç', 'ć': 'ç',
    'Ę': 'Ë', 'ę': 'ë',
    'Ł': 'Í', 'ł': 'í', # Zmienione na Í/í (I-acute) dla najwęższego rozstawu
    'Ń': 'Ñ', 'ń': 'ñ',
    'Ó': 'Ö', 'ó': 'ö',
    'Ś': 'Ã', 'ś': 'ã',
    'Ź': 'Â', 'ź': 'â',
    'Ż': 'À', 'ż': 'à'
}

def remap_text(text):
    if text is None: return None
    for pl, sacrifice in REMAP_MAP.items():
        text = text.replace(pl, sacrifice)
    return text

def infiltrate():
    print("🦅 Operacja 'Ł-PRECISION' - Start!")
    
    if not GAME_DB.exists():
        print("❌ Krytyczny błąd: Nie znaleziono bazy gry!")
        return

    # Backup bazy gry
    backup = GAME_DB.with_suffix(".db.FINAL_POLISH_V3_SLIM_L")
    if not backup.exists():
        shutil.copy2(GAME_DB, backup)
        print(f"✅ Backup wykonany: {backup.name}")

    conn_work = sqlite3.connect(WORK_DB)
    cursor_work = conn_work.cursor()
    
    conn_game = sqlite3.connect(GAME_DB)
    cursor_game = conn_game.cursor()

    # Tabele z kolumnami RU
    tables = ["menu", "maps", "item", "creature"]
    total_count = 0

    for table in tables:
        try:
            cursor_work.execute(f"PRAGMA table_info({table})")
            cols = [c[1] for c in cursor_work.fetchall()]
            pl_col = next((c for c in cols if "_pl_PL" in c), None)
            if not pl_col: continue

            ru_col = pl_col.replace("_pl_PL", "_ru_RU")
            print(f"📦 Przetwarzanie {table:10} | {pl_col} -> {ru_col}")

            cursor_work.execute(f"SELECT StringID, {pl_col} FROM {table} WHERE {pl_col} IS NOT NULL")
            rows = cursor_work.fetchall()

            for string_id, text_pl in rows:
                remapped_text = remap_text(text_pl)
                cursor_game.execute(f"UPDATE {table} SET {ru_col} = ? WHERE StringID = ?", (remapped_text, string_id))
                total_count += 1

        except Exception as e:
            print(f"  ⚠️  Problem z tabelą {table}: {e}")

    conn_game.commit()
    conn_work.close()
    conn_game.close()
    
    print(f"\n✨ SUKCES! Wstrzyknięto {total_count} linii z poprawionym kerningiem.")
    print("🚀 TERAZ: Eksportuj DDS i odpal grę!")

if __name__ == "__main__":
    infiltrate()
import sqlite3
import os
import sys

# Ścieżka do oficjalnej bazy w paczce
WORK_DB = os.path.expanduser(
    "~/Github_Projects/linux-gaming-fixes/Metal Wolf Chaos XD - Polish translation/"
    "MWC_XD_Spolszczenie_PL/Media/Texts/texts_may30.db"
)

# Słownik remappingu (zgodny z atlasem DDS)
REAL_REMAP_DICT = {
    'ą': 'ä', 'Ą': 'Ä',
    'ć': 'ç', 'Ć': 'Ç',
    'ę': 'ë', 'Ę': 'Ë',
    'ł': 'í', 'Ł': 'Í',
    'ń': 'ñ', 'Ń': 'Ñ',
    'ó': 'ö', 'Ó': 'Ö',
    'ś': 'ã', 'Ś': 'Ã',
    'ź': 'â', 'Ź': 'Â',
    'ż': 'à', 'Ż': 'À'
}

def translate_text(text):
    """Zamienia polskie znaki na znaki-ofiary z atlasu DDS."""
    if text is None:
        return None
    res = list(text)
    for i, char in enumerate(res):
        if char in REAL_REMAP_DICT:
            res[i] = REAL_REMAP_DICT[char]
    return "".join(res)

def remap_table(conn, cur, table_name):
    """Remapuje jedną tabelę: _pl_PL -> _ru_RU."""
    cur.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cur.fetchall()]
    pl_cols = [c for c in columns if c.endswith("_pl_PL")]

    if not pl_cols:
        return 0

    primary_key = "StringID" if "StringID" in columns else columns[0]

    # Sprawdź czy istnieją kolumny _ru_RU
    ru_cols = [c.replace("_pl_PL", "_ru_RU") for c in pl_cols]
    existing_ru = [c for c in ru_cols if c in columns]
    if len(existing_ru) != len(ru_cols):
        print(f"    [-] Pominięto {table_name}: brak kolumn _ru_RU")
        return 0

    cur.execute(f"SELECT {primary_key}, {', '.join(pl_cols)} FROM {table_name}")
    rows = cur.fetchall()

    updates = 0
    for row in rows:
        row_id = row[0]
        pl_values = row[1:]
        ru_values = [translate_text(val) for val in pl_values]

        # Pomiń puste wiersze
        if all(v is None for v in ru_values):
            continue

        set_clause = ", ".join([f"{ru_col} = ?" for ru_col in ru_cols])
        update_query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?"

        try:
            cur.execute(update_query, list(ru_values) + [row_id])
            updates += 1
        except sqlite3.OperationalError as e:
            print(f"    [-] Błąd SQL w {table_name}: {e}")
            break

    return updates

def main():
    if not os.path.exists(WORK_DB):
        print(f"[!] BŁĄD: Nie znaleziono bazy: {WORK_DB}")
        sys.exit(1)

    conn = sqlite3.connect(WORK_DB)
    cur = conn.cursor()

    # Jeśli podano nazwę tabeli jako argument — remapuj tylko ją
    if len(sys.argv) > 1:
        target_table = sys.argv[1]
        print(f"--- REMAPPING TABELI: {target_table} ---")
        count = remap_table(conn, cur, target_table)
        print(f"[+] Zremapowano {count} wpisów w tabeli '{target_table}'")
    else:
        # Remapuj wszystkie tabele
        print("--- MASOWY REMAPPING PL -> RU (wszystkie tabele) ---")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cur.fetchall() if row[0] != "sqlite_sequence"]

        total = 0
        for table in tables:
            count = remap_table(conn, cur, table)
            if count > 0:
                print(f"    {table}: {count} wpisów")
                total += count

        print(f"\n[+] SUKCES! Zremapowano łącznie {total} wpisów.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()

import sqlite3
import os
import sys

# Ścieżka do bazy w folderze paczki
WORK_DB = os.path.expanduser(
    "~/Github_Projects/linux-gaming-fixes/Metal Wolf Chaos XD - Polish translation/"
    "MWC_XD_Spolszczenie_PL/Media/Texts/texts_may30.db"
)

# Słownik remappingu (z README_FONTS.md)
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
    """Zamienia polskie znaki na znaki-ofiary dla atlasu DDS."""
    if text is None:
        return None
    res = list(text)
    for i, char in enumerate(res):
        if char in REAL_REMAP_DICT:
            res[i] = REAL_REMAP_DICT[char]
    return "".join(res)

def remap_all_tables(conn, cur):
    """Masowy remapping wszystkich tabel PL -> RU."""
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall() if row[0] != "sqlite_sequence"]

    total_remapped = 0

    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cur.fetchall()]
        pl_cols = [c for c in columns if c.endswith("_pl_PL")]

        if not pl_cols:
            continue

        primary_key = "StringID" if "StringID" in columns else columns[0]
        cur.execute(f"SELECT {primary_key}, {', '.join(pl_cols)} FROM {table}")
        rows = cur.fetchall()

        table_updates = 0
        for row in rows:
            row_id = row[0]
            pl_values = row[1:]
            ru_values = [translate_text(val) for val in pl_values]

            # Pomijamy puste wiersze
            if all(v is None for v in ru_values):
                continue

            ru_cols = [c.replace("_pl_PL", "_ru_RU") for c in pl_cols]
            set_clause = ", ".join([f"{col} = ?" for col in ru_cols])
            update_query = f"UPDATE {table} SET {set_clause} WHERE {primary_key} = ?"

            try:
                cur.execute(update_query, list(ru_values) + [row_id])
                table_updates += 1
            except sqlite3.OperationalError as e:
                print(f"    [-] Błąd w tabeli {table}: {e}")
                break

        total_remapped += table_updates

    conn.commit()
    return total_remapped

def sniper_mode():
    print("\n" + "=" * 60)
    print(" 🎯 SNAJPER TEKSTOWY + AUTO-REMAPPING: METAL WOLF CHAOS XD ")
    print("=" * 60)
    print(" Edycja tekstu automatycznie zapisuje do _pl_PL i _ru_RU")
    print("=" * 60)

    if not os.path.exists(WORK_DB):
        print(f"[!] BŁĄD: Nie znaleziono {WORK_DB}")
        return

    conn = sqlite3.connect(WORK_DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall() if row[0] != "sqlite_sequence"]

    while True:
        search_term = input("\n🔍 Wpisz fragment tekstu (lub 'q' aby wyjść, 'r' aby zremapować wszystko): ")

        if search_term.lower() == 'q':
            break

        if search_term.lower() == 'r':
            print("\n--- ROZPOCZYNAM MASOWY REMAPPING ---")
            total = remap_all_tables(conn, cur)
            print(f"[+] Zremapowano {total} wpisów we wszystkich tabelach.")
            continue

        if len(search_term) < 1:
            print("Wpisz przynajmniej 1 znak!")
            continue

        # Wyszukiwanie
        results = []
        for table in tables:
            cur.execute(f"PRAGMA table_info({table})")
            cols = [col[1] for col in cur.fetchall()]
            pl_cols = [c for c in cols if c.endswith("_pl_PL")]
            primary_key = "StringID" if "StringID" in cols else cols[0]

            for pl_col in pl_cols:
                query = f"SELECT {primary_key}, {pl_col} FROM {table} WHERE {pl_col} LIKE ?"
                cur.execute(query, ('%' + search_term + '%',))
                rows = cur.fetchall()
                for row in rows:
                    results.append((table, pl_col, row[0], row[1]))

        if not results:
            print("[-] Nie znaleziono dopasowań.")
            continue

        print(f"\n[+] Znaleziono {len(results)} wyników:")
        for idx, (tbl, col, r_id, text) in enumerate(results):
            print(f"  [{idx}] {tbl}.{col} (ID: {r_id})")
            print(f"       -> {text[:80]}{'...' if len(text) > 80 else ''}")

        choice = input("\nWybierz numer do edycji (lub 'c' aby anulować): ")
        if choice.lower() == 'c' or not choice.isdigit() or int(choice) >= len(results):
            continue

        selected = results[int(choice)]
        tbl, pl_col, r_id, old_text = selected

        print(f"\nObecny tekst PL: {old_text}")
        new_text = input("Nowy tekst PL  : ")

        if not new_text:
            print("Anulowano.")
            continue

        # Automatyczny remapping dla kolumny RU
        ru_text = translate_text(new_text)
        ru_col = pl_col.replace("_pl_PL", "_ru_RU")

        # Aktualizacja OBU kolumn jednocześnie
        update_query = f"UPDATE {tbl} SET {pl_col} = ?, {ru_col} = ? WHERE StringID = ?"
        cur.execute(update_query, (new_text, ru_text, r_id))
        conn.commit()

        print(f"[+] Zapisano!")
        print(f"    PL ({pl_col}): {new_text[:60]}{'...' if len(new_text) > 60 else ''}")
        print(f"    RU ({ru_col}): {ru_text[:60]}{'...' if len(ru_text) > 60 else ''}")

    conn.close()
    print("\nZakończono pracę Snajpera.")

if __name__ == "__main__":
    sniper_mode()

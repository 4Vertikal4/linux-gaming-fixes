import sqlite3
import os
import sys
import shutil

# Ścieżki
WORK_DB = "/home/vertikal/Github_Projects/linux-gaming-fixes/Metal Wolf Chaos XD - Polish translation/work/texts_may30_PL.db"
GAME_DB = "/home/vertikal/Games/Heroic/Metal Wolf Chaos XD/Media/Texts/texts_may30.db"

# Twój zaufany słownik remappingu
REAL_REMAP_DICT = {
    'ą': 'ä', 'Ą': 'Ä', 'ć': 'ç', 'Ć': 'Ç', 'ę': 'ë', 'Ę': 'Ë',
    'ł': 'í', 'Ł': 'Í', 'ń': 'ñ', 'Ń': 'Ñ', 'ó': 'ö', 'Ó': 'Ö',
    'ś': 'ã', 'Ś': 'Ã', 'ź': 'â', 'Ź': 'Â', 'ż': 'à', 'Ż': 'À'
}

def translate_text(text):
    if text is None: return None
    res = list(text)
    for i, char in enumerate(res):
        if char in REAL_REMAP_DICT:
            res[i] = REAL_REMAP_DICT[char]
    return "".join(res)

def sniper_mode():
    print("\n" + "="*50)
    print(" 🎯 SNAJPER TEKSTOWY: METAL WOLF CHAOS XD ")
    print("="*50)
    
    if not os.path.exists(WORK_DB):
        print(f"[!] BŁĄD: Nie znaleziono {WORK_DB}")
        return

    conn = sqlite3.connect(WORK_DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables =[row[0] for row in cur.fetchall() if row[0] != "sqlite_sequence"]

    while True:
        search_term = input("\n🔍 Wpisz fragment tekstu do znalezienia (lub 'q' aby wyjść): ")
        if search_term.lower() == 'q': break
        if len(search_term) < 1:
            print("Wpisz przynajmniej 1 znaki!")
            continue

        results =[]
        for table in tables:
            cur.execute(f"PRAGMA table_info({table})")
            cols = [col[1] for col in cur.fetchall()]
            pl_cols =[c for c in cols if c.endswith("_pl_PL")]
            primary_key = "StringID" if "StringID" in cols else cols[0]

            for pl_col in pl_cols:
                query = f"SELECT {primary_key}, {pl_col} FROM {table} WHERE {pl_col} LIKE ?"
                cur.execute(query, ('%' + search_term + '%',))
                rows = cur.fetchall()
                for row in rows:
                    results.append((table, pl_col, row[0], row[1]))

        if not results:
            print("[-] Nie znaleziono żadnych dopasowań.")
            continue

        print(f"\n[+] Znaleziono {len(results)} wyników:")
        for idx, (tbl, col, r_id, text) in enumerate(results):
            print(f"  [{idx}] (Tabela: {tbl}) -> {text}")

        choice = input("\nWybierz numer do edycji (lub 'c' aby anulować): ")
        if choice.lower() == 'c' or not choice.isdigit() or int(choice) >= len(results):
            continue

        selected = results[int(choice)]
        tbl, pl_col, r_id, old_text = selected
        
        print(f"\nObecny tekst: {old_text}")
        new_text = input("Nowy tekst  : ")
        
        if not new_text:
            print("Anulowano.")
            continue

        # Remapping nowego tekstu dla kolumny rosyjskiej
        ru_text = translate_text(new_text)
        ru_col = pl_col.replace("_pl_PL", "_ru_RU")

        # Aktualizacja bazy roboczej
        update_query = f"UPDATE {tbl} SET {pl_col} = ?, {ru_col} = ? WHERE StringID = ?"
        cur.execute(update_query, (new_text, ru_text, r_id))
        conn.commit()
        
        print("[+] Baza projektowa zaktualizowana.")

        # Aktualizacja od razu w folderze gry (Opcjonalne, ale bardzo wygodne)
        try:
            shutil.copy2(WORK_DB, GAME_DB)
            print("[+] Baza w folderze gry zaktualizowana! (Wystarczy wczytać punkt kontrolny w grze).")
        except Exception as e:
            print(f"[-] Błąd podczas kopiowania do folderu gry: {e}")

    conn.close()
    print("Zakończono pracę Snajpera.")

if __name__ == "__main__":
    sniper_mode()

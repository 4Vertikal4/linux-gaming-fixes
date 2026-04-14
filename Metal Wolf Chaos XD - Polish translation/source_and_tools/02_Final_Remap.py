import sqlite3
import os
import sys

WORK_DB = "texts_may30_PL.db"

# Słownik zamian (Przeszczep Glifów) - dopasowany do Twojego atlasu DDS z Operacji 1
# Klucz: prawdziwa polska litera -> Wartość: znak-ofiara w atlasie
REMAP_DICT = {
    'ą': 'щ', 'Ą': 'Щ',
    'ć': 'ç', 'Ć': 'Ç',
    'ę': 'ë', 'Ę': 'Ë',
    'ł': 'í', 'Ł': 'Í',
    'ń': 'ñ', 'Ń': 'Ñ',
    'ó': 'ö', 'Ó': 'Ö',
    'ś': 'š', 'Ś': 'Š',
    'ź': 'ý', 'Ź': 'Ý',
    'ż': 'ż', 'Ż': 'Ż' # Często 'ż' było zmapowane np na 'ż' albo inny znak - zostawiam oryginał, 
                       # ALE upewnij się, czy u Ciebie 'ż' w grze wyświetla się z tego znaku, czy np. z 'ï'.
                       # Z Twoich screenów widzę, że masz "Rëce diabía", "Àoíniez" (Żołnierz). 
                       # CZEKAJ! Na Twoim screenie z accessory widzę "Àoíniez" dla "Żołnierz"! 
                       # SZYBKA KOREKTA SŁOWNIKA ZGODNIE Z TWOIM EKRANEM:
}

# ZAKTUALIZOWANY SŁOWNIK NA PODSTAWIE TWOJEGO ZDJĘCIA (accessory):
# Żołnierz -> Àoíniez (Ż -> À, ł -> í, rz -> rz)
# Ręce diabła -> Rëce diabía (ę -> ë, ł -> í)
# Czołg Specjalny -> Czoíg Specjalny (ł -> í)
# KULOSTRZAŁ -> KULOSTRZAÍ (Ł -> Í)

# ZAKTUALIZOWANY SŁOWNIK NA PODSTAWIE README_FONTS.md:
REAL_REMAP_DICT = {
    'ą': 'ä', 'Ą': 'Ä',
    'ć': 'ç', 'Ć': 'Ç',
    'ę': 'ë', 'Ę': 'Ë',
    'ł': 'í', 'Ł': 'Í',  # Wąski slot dla poprawnego kerningu!
    'ń': 'ñ', 'Ń': 'Ñ',
    'ó': 'ö', 'Ó': 'Ö',
    'ś': 'ã', 'Ś': 'Ã',
    'ź': 'â', 'Ź': 'Â',
    'ż': 'à', 'Ż': 'À'
}

def translate_text(text):
    if text is None:
        return None
    res = list(text)
    for i, char in enumerate(res):
        if char in REAL_REMAP_DICT:
            res[i] = REAL_REMAP_DICT[char]
    return "".join(res)

def final_remap():
    print("--- ROZPOCZYNAM MASOWY REMAPPING PL -> RU ---")
    
    if not os.path.exists(WORK_DB):
        print("[!] BŁĄD: Nie znaleziono bazy roboczej.")
        sys.exit(1)

    conn = sqlite3.connect(WORK_DB)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables =[row[0] for row in cur.fetchall() if row[0] != "sqlite_sequence"]

    total_remapped = 0

    for table in tables:
        cur.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cur.fetchall()]
        
        # Szukamy kolumn, które mają _pl_PL
        pl_cols =[c for c in columns if c.endswith("_pl_PL")]
        
        if not pl_cols:
            continue
            
        print(f"[*] Skanuję tabelę: {table}")
        primary_key = "StringID" if "StringID" in columns else columns[0]

        cur.execute(f"SELECT {primary_key}, {', '.join(pl_cols)} FROM {table}")
        rows = cur.fetchall()

        table_updates = 0
        for row in rows:
            row_id = row[0]
            pl_values = row[1:]
            
            # Remapujemy każdy polski tekst
            ru_values =[translate_text(val) for val in pl_values]
            
            # Budujemy zapytanie UPDATE (np. UPDATE accessory SET Name_ru_RU = ?, ShortDescription_ru_RU = ? WHERE StringID = ?)
            ru_cols =[c.replace("_pl_PL", "_ru_RU") for c in pl_cols]
            set_clause = ", ".join([f"{col} = ?" for col in ru_cols])
            
            # UWAGA: Omijamy puste (NULL) rzędy w bazie, jeśli całe polskie tłumaczenie jest puste
            if all(v is None for v in ru_values):
                continue
                
            update_query = f"UPDATE {table} SET {set_clause} WHERE {primary_key} = ?"
            
            update_params = list(ru_values)
            update_params.append(row_id)
            
            try:
                cur.execute(update_query, update_params)
                table_updates += 1
            except sqlite3.OperationalError as e:
                # Jeśli np. w tabeli jest kolumna _pl_PL, ale nie ma odpowiadającej _ru_RU
                print(f"    [-] Błąd zapisu do kolumn RU w tabeli {table}: {e}")
                break

        total_remapped += table_updates
        print(f"    -> Zremapowano i przekopiowano {table_updates} wpisów.")

    conn.commit()
    conn.close()
    print(f"\n[+] SUKCES! Zremapowano łącznie {total_remapped} wpisów we wszystkich tabelach.")
    print("[+] Tłumaczenie z _pl_PL zostało bezpiecznie skopiowane do _ru_RU z podmienionymi literami!")

if __name__ == "__main__":
    final_remap()

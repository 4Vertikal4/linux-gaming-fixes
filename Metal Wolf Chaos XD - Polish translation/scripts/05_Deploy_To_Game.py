#!/usr/bin/env python3
# overwrite_original_text.py

import sqlite3
import shutil
import sys
from pathlib import Path

# Import konfiguracji
try:
    import config_translator as cfg
except ImportError:
    print("❌ Błąd: Nie znaleziono pliku config_translator.py!")
    sys.exit(1)

# Kolory
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def main():
    print(f"{CYAN}=================================================={RESET}")
    print(f"{CYAN}   🔄 TRANSLATION INJECTOR (Overwrite Mode)       {RESET}")
    print(f"{CYAN}=================================================={RESET}")
    print(f"Gra: {cfg.GAME_NAME}")
    print(f"Baza robocza: {cfg.DB_PATH}")
    print(f"Baza gry: {cfg.GAME_DB_PATH}")
    print("-" * 50)
    print(f"{RED}UWAGA! Ten skrypt NADPISZE oryginalny angielski tekst w Twojej bazie roboczej")
    print(f"tekstem polskim. Następnie podmieni plik w katalogu gry.{RESET}")
    print("To operacja destrukcyjna dla języka angielskiego w bazie roboczej.")
    
    confirm = input(f"\n{YELLOW}Czy na pewno chcesz kontynuować? (wpisz 'TAK'): {RESET}")
    if confirm != 'TAK':
        print("Anulowano.")
        sys.exit(0)

    # 1. Backup bazy gry (jeśli jeszcze nie ma)
    if cfg.GAME_DB_PATH.exists():
        backup_path = cfg.GAME_DB_PATH.with_suffix('.db.original_backup')
        if not backup_path.exists():
            shutil.copy2(cfg.GAME_DB_PATH, backup_path)
            print(f"\n📁 Zrobiono backup oryginału gry: {backup_path}")
        else:
            print(f"\nℹ️  Backup oryginału gry już istnieje.")
    else:
        print(f"\n⚠️  Nie znaleziono pliku gry w {cfg.GAME_DB_PATH}. Tylko zaktualizuję bazę roboczą.")

    # 2. Nadpisywanie kolumn w bazie roboczej
    conn = sqlite3.connect(cfg.DB_PATH)
    cursor = conn.cursor()
    
    total_updates = 0
    
    print("\n🚀 Rozpoczynam nadpisywanie (EN <- PL)...")

    # Pobieramy strukturę tabel z CONFIGU (nie musisz wpisywać ręcznie!)
    for table_conf in cfg.TABLES_TO_TRANSLATE:
        table = table_conf['table_name']
        
        for col_en, col_pl in table_conf['columns']:
            try:
                # Sprawdź ile wierszy nadpiszemy
                query_count = f"SELECT COUNT(*) FROM {table} WHERE {col_pl} IS NOT NULL AND {col_pl} != ''"
                cursor.execute(query_count)
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # Wykonaj nadpisanie: SET English = Polish
                    query_update = f"UPDATE {table} SET {col_en} = {col_pl} WHERE {col_pl} IS NOT NULL AND {col_pl} != ''"
                    cursor.execute(query_update)
                    print(f"   ✅ {table}: {col_en} ZASTĄPIONO przez {col_pl} ({count} wierszy)")
                    total_updates += count
                else:
                    print(f"   ⚠️  {table}: Brak tłumaczeń w kolumnie {col_pl}")

            except Exception as e:
                print(f"   ❌ Błąd w tabeli {table}: {e}")

    conn.commit()
    conn.close()
    
    print(f"\n✅ Zaktualizowano łącznie {total_updates} wierszy w bazie roboczej.")

    # 3. Kopiowanie do folderu gry
    if cfg.GAME_DB_PATH.parent.exists():
        print(f"💾 Kopiowanie bazy roboczej do folderu gry...")
        try:
            shutil.copy2(cfg.DB_PATH, cfg.GAME_DB_PATH)
            print(f"{GREEN}🎉 SUKCES! Plik gry został podmieniony. Możesz odpalać grę!{RESET}")
        except Exception as e:
            print(f"{RED}❌ Błąd kopiowania do folderu gry: {e}{RESET}")
    else:
        print(f"{YELLOW}⚠️  Nie znaleziono folderu gry. Skopiuj plik {cfg.DB_PATH} ręcznie.{RESET}")

if __name__ == "__main__":
    main()

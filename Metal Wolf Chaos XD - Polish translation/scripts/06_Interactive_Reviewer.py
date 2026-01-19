#!/usr/bin/env python3
# 06_Interactive_Reviewer.py v1.9

import sqlite3
import sys
import os
from pathlib import Path

# Dodajemy ścieżkę bieżącego katalogu do sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Kolory i formatowanie
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

try:
    import config_translator as cfg
    
    # 🧠 INTELIGENTNY IMPORT SILNIKA
    mode = getattr(cfg, "TRANSLATION_MODE", "local").lower()
    
    try:
        if mode == "local":
            from engines.local_torch import translate_text
            engine_name = f"LOCAL ({cfg.MODEL_NAME})"
        else:
            from engines.cloud_api import translate_text
            engine_name = f"CLOUD ({cfg.API_PROVIDER})"
            
        AI_AVAILABLE = True
        
    except ImportError as e:
        print(f"{YELLOW}⚠️  AI niedostępne (błąd importu silnika: {e}). Działam w trybie ręcznym.{RESET}")
        AI_AVAILABLE = False
        engine_name = "NONE"

except ImportError:
    print("❌ Błąd: Nie znaleziono pliku config_translator.py!")
    sys.exit(1)

def print_diff(en, pl):
    """Wyświetla ładne porównanie tekstów."""
    print("-" * 60)
    disp_en = en if en is not None else f"{RED}[NULL]{RESET}"
    disp_pl = pl if pl is not None else f"{RED}[NULL]{RESET}"
    
    if en == "": disp_en = f"{YELLOW}[PUSTY]{RESET}"
    if pl == "": disp_pl = f"{YELLOW}[PUSTY]{RESET}"

    print(f"{BLUE}ORIG (EN):{RESET} {disp_en}")
    print(f"{YELLOW}CURR (PL):{RESET} {disp_pl}")
    print("-" * 60)

def print_menu():
    """Wyświetla dostępne komendy."""
    print(f"\n{BOLD}DOSTĘPNE KOMENDY:{RESET}")
    print(" [Enter] = Zatwierdź i idź dalej (Next)")
    print(f" [b]     = {YELLOW}Wróć do poprzedniego (Back){RESET}")
    print(" [n]     = Edytuj ręcznie (jedna linia)")
    print(f" [p]     = {GREEN}Wklej tekst wielolinijkowy (Paste){RESET}")
    print(f" [x]     = {RED}Wyczyść (ustaw puste pole){RESET}")
    print(" [a]     = Poproś AI o sugestię")
    print(" [c]     = Wygeneruj prompt do schowka")
    print(" [m]     = Pokaż to menu ponownie")
    print(" [q]     = Zapisz i wyjdź")
    print("-" * 30)

def generate_prompt_for_clipboard(row_id, en, pl):
    """Generuje prompt z instrukcją EOF dla tekstów wielolinijkowych."""
    base_prompt = f"""Proszę o poprawę tłumaczenia w grze (StringID: {row_id}).
Oryginał EN: "{en}"
Obecne PL: "{pl}"
Kontekst: Krótki tekst UI / Menu / Dialog.
"""
    # Sprawdzamy czy tekst jest wielolinijkowy
    is_multiline = '\n' in en or (pl and '\n' in pl)
    
    if is_multiline:
        base_prompt += "\nINSTRUKCJA FORMATOWANIA: Tekst jest wielolinijkowy. Proszę zwróć SAMO tłumaczenie, a w ostatniej linii dodaj słowo 'EOF' (wielkimi literami)."
    else:
        base_prompt += "\nINSTRUKCJA: Zwróć tylko poprawione tłumaczenie."

    base_prompt += "\n\nPoprawne tłumaczenie:"
    return base_prompt, is_multiline

def main():
    print(f"{CYAN}=================================================={RESET}")
    print(f"{CYAN}   🕵️  INTERACTIVE REVIEWER & FIXER v1.9 (Fixed)  {RESET}")
    print(f"{CYAN}=================================================={RESET}")
    if AI_AVAILABLE:
        print(f"✅ Silnik AI: {engine_name}")
    
    conn = sqlite3.connect(cfg.DB_PATH)
    cursor = conn.cursor()

    print("\nDostępne tabele w konfiguracji:")
    for i, t in enumerate(cfg.TABLES_TO_TRANSLATE):
        print(f"[{i+1}] {t['table_name']}")
    
    try:
        choice = int(input("\nWybierz tabelę do korekty (numer): ")) - 1
        table_conf = cfg.TABLES_TO_TRANSLATE[choice]
        table_name = table_conf['table_name']
        pk_col = table_conf['id_column']
        col_en = table_conf['columns'][0][0]
        col_pl = table_conf['columns'][0][1]
    except (ValueError, IndexError):
        print("Nieprawidłowy wybór.")
        return

    print("\nCo chcesz przeglądać?")
    print("[1] Wszystko po kolei")
    print("[2] Tylko konkretny StringID")
    print("[3] Wyszukaj frazę w PL (np. 'szotgun')")
    print("[4] Pokaż tylko PUSTE tłumaczenia")
    mode = input("Wybór: ")

    query = f"SELECT {pk_col}, {col_en}, {col_pl} FROM {table_name} WHERE {col_en} IS NOT NULL"
    params = []

    if mode == '2':
        sid = input("Podaj StringID: ")
        query += f" AND {pk_col} = ?"
        params.append(sid)
    elif mode == '3':
        phrase = input("Szukana fraza w PL: ")
        query += f" AND {col_pl} LIKE ?"
        params.append(f"%{phrase}%")
    elif mode == '4':
        query += f" AND ({col_pl} IS NULL OR {col_pl} = '')"
    
    query += f" ORDER BY {pk_col}"

    cursor.execute(query, params)
    rows = [list(row) for row in cursor.fetchall()]

    if not rows:
        print(f"{RED}Brak wyników.{RESET}")
        conn.close()
        return

    total_rows = len(rows)
    print(f"\nZnaleziono {total_rows} wierszy.")

    # --- SKOK DO REKORDU ---
    current_idx = 0
    if total_rows > 1:
        try:
            jump_input = input(f"Od którego numeru rekordu zacząć? (1-{total_rows}, Enter=1): ").strip()
            if jump_input:
                current_idx = int(jump_input) - 1
                if current_idx < 0: current_idx = 0
                if current_idx >= total_rows: current_idx = total_rows - 1
        except ValueError:
            current_idx = 0
    # -----------------------

    print("\nZaczynamy!")
    print_menu()
    
    # --- FIX: INICJALIZACJA LICZNIKA ---
    changes_count = 0
    # -----------------------------------
    
    while current_idx < total_rows:
        row = rows[current_idx]
        row_id = row[0]
        text_en = row[1]
        text_pl = row[2]

        print(f"\n{CYAN}Rekord [{current_idx + 1}/{total_rows}] | ID: {row_id}{RESET}")
        
        while True:
            print_diff(text_en, text_pl)
            action = input(f"{BOLD}Akcja? (m=menu) > {RESET}").strip()

            if action == 'q':
                print("Zapisywanie i wychodzenie...")
                conn.commit()
                conn.close()
                print(f"\n🎉 Koniec sesji. Wprowadzono {changes_count} zmian.")
                return

            elif action == '': # NEXT
                print(f"{GREEN}OK (Następny).{RESET}")
                current_idx += 1
                break
            
            elif action.lower() == 'b': # BACK
                if current_idx > 0:
                    print(f"{YELLOW}⏪ Cofanie...{RESET}")
                    current_idx -= 1
                    break
                else:
                    print(f"{RED}To jest pierwszy rekord, nie można cofnąć.{RESET}")

            elif action.lower() == 'm':
                print_menu()

            elif action.lower() == 'x':
                text_pl = "" 
                cursor.execute(f"UPDATE {table_name} SET {col_pl} = ? WHERE {pk_col} = ?", (text_pl, row_id))
                conn.commit()
                rows[current_idx][2] = text_pl
                print(f"{RED}Pole wyczyszczone.{RESET}")
                changes_count += 1

            elif action.lower() == 'c':
                prompt, is_multiline = generate_prompt_for_clipboard(row_id, text_en, text_pl)
                print(f"\n{YELLOW}--- SKOPIUJ DO CZATU ---{RESET}")
                print(prompt)
                print(f"{YELLOW}------------------------{RESET}")
                
                if is_multiline:
                    print(f"{GREEN}💡 WSKAZÓWKA: Odpowiedź AI będzie wielolinijkowa!")
                    print(f"   Do wklejenia odpowiedzi użyj komendy [p] (Paste).{RESET}")
                
                input("Naciśnij Enter po skopiowaniu...")

            elif action.lower() == 'a':
                if AI_AVAILABLE:
                    print("🤖 Generowanie sugestii...")
                    new_suggestion = translate_text(text_en) 
                    if new_suggestion:
                        print(f"Sugestia AI: {new_suggestion}")
                        confirm = input("Użyć tego? [t/n]: ")
                        if confirm.lower() == 't':
                            text_pl = new_suggestion
                            cursor.execute(f"UPDATE {table_name} SET {col_pl} = ? WHERE {pk_col} = ?", (text_pl, row_id))
                            conn.commit()
                            rows[current_idx][2] = text_pl
                            changes_count += 1
                    else:
                        print("AI nie zwróciło odpowiedzi.")
                else:
                    print("AI niedostępne.")

            elif action.lower() == 'n':
                print("Wpisz nową treść (DLA JEDNEJ LINII):")
                new_text = input("> ")
                if new_text.strip():
                    text_pl = new_text
                    cursor.execute(f"UPDATE {table_name} SET {col_pl} = ? WHERE {pk_col} = ?", (text_pl, row_id))
                    conn.commit()
                    rows[current_idx][2] = text_pl
                    print(f"{GREEN}Zapisano!{RESET}")
                    changes_count += 1
                else:
                    print("Anulowano.")

            elif action.lower() == 'p':
                print(f"{YELLOW}TRYB WKLEJANIA (MULTI-LINE){RESET}")
                print("1. Wklej tekst (zakończony EOF lub wciśnij Enter).")
                print("2. Wpisz 'EOF' w nowej linii aby zakończyć.")
                print("-" * 20)
                
                input_lines = []
                while True:
                    try:
                        line = input()
                        if line.strip().upper() == 'EOF':
                            break
                        input_lines.append(line)
                    except EOFError:
                        break
                
                if input_lines:
                    text_pl = "\n".join(input_lines)
                    cursor.execute(f"UPDATE {table_name} SET {col_pl} = ? WHERE {pk_col} = ?", (text_pl, row_id))
                    conn.commit()
                    rows[current_idx][2] = text_pl
                    print(f"{GREEN}Zapisano tekst wielolinijkowy!{RESET}")
                    changes_count += 1
                else:
                    print("Pusty wsad, anulowano.")
            
            else:
                print(f"{RED}Nieznana komenda. Wpisz 'm' aby zobaczyć listę.{RESET}")

    print(f"\n🎉 Koniec listy. Wprowadzono {changes_count} zmian.")
    conn.close()

if __name__ == "__main__":
    main()
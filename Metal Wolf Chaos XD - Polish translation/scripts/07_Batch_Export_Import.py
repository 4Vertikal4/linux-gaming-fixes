#!/usr/bin/env python3
# 07_Batch_Export_Import.py v1.7 (Fix: Return Tuple)

import sqlite3
import sys
import os
from pathlib import Path

# Dodajemy ścieżkę bieżącego katalogu do sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Kolory
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'
GRAY = '\033[90m'

try:
    import config_translator as cfg
except ImportError:
    print("❌ Błąd: Nie znaleziono pliku config_translator.py!")
    sys.exit(1)

def generate_batch_prompt(rows):
    """Tworzy sformatowany tekst do wklejenia do AI."""
    prompt = """Jesteś tłumaczem gry "Metal Wolf Chaos XD".
Przetłumacz poniższe linie tekstu na język polski.

ZASADY FORMATOWANIA (BARDZO WAŻNE):
1. Każda linia musi mieć format: ID ||| Oryginał ||| Tłumaczenie
2. Nie zmieniaj ID. Nie usuwaj separatorów "|||".
3. NA SAMYM KOŃCU ODPOWIEDZI, w nowej linii, napisz słowo: EOF

TEKSTY DO PRZETŁUMACZENIA:
"""
    for row_id, text_en, text_pl in rows:
        clean_en = text_en.replace('\n', ' ')
        prompt += f"{row_id} ||| {clean_en} ||| \n"
    
    return prompt

def parse_and_save(response_text, table_name, pk_col, col_pl, cursor):
    """Parsuje odpowiedź AI i zapisuje do bazy."""
    lines = response_text.strip().split('\n')
    success_count = 0
    last_id = None  # Śledzimy ostatnie ID
    
    print(f"\n{CYAN}Przetwarzanie odpowiedzi...{RESET}")
    
    for line in lines:
        if "|||" not in line: continue
            
        parts = line.split("|||")
        if len(parts) < 3: continue
            
        row_id = parts[0].strip()
        translation = parts[2].strip()
        
        if translation.upper() == 'EOF' or not translation: continue

        try:
            cursor.execute(f"UPDATE {table_name} SET {col_pl} = ? WHERE {pk_col} = ?", (translation, row_id))
            print(f" ✅ ID {row_id}: {translation[:60]}...")
            success_count += 1
            last_id = row_id # Aktualizujemy ostatnie udane ID
        except Exception as e:
            print(f"{RED} ❌ Błąd SQL dla ID {row_id}: {e}{RESET}")

    # NAPRAWA: Zwracamy dwie wartości (krotkę)
    return success_count, last_id

def main():
    print(f"{CYAN}=================================================={RESET}")
    print(f"{CYAN}   📦 BATCH TRANSLATOR v1.7 (Stable Loop)         {RESET}")
    print(f"{CYAN}=================================================={RESET}")
    
    conn = sqlite3.connect(cfg.DB_PATH)
    cursor = conn.cursor()

    # 1. Wybór tabeli
    print("\nDostępne tabele:")
    for i, t in enumerate(cfg.TABLES_TO_TRANSLATE):
        print(f"[{i+1}] {t['table_name']}")
    
    try:
        choice_input = input("\nWybierz tabelę (numer) lub 'q' aby wyjść: ")
        if choice_input.lower() == 'q': return
        choice = int(choice_input) - 1
        
        table_conf = cfg.TABLES_TO_TRANSLATE[choice]
        table_name = table_conf['table_name']
        pk_col = table_conf['id_column']
        col_en = table_conf['columns'][0][0]
        col_pl = table_conf['columns'][0][1]
    except (ValueError, IndexError):
        print("Nieprawidłowy wybór.")
        return

    # 2. Konfiguracja filtrów
    print("\n--- Tryb pracy ---")
    print("[1] Tylko puste (domyślne - uzupełnianie braków)")
    print("[2] WSZYSTKIE (nadpisywanie istniejących tłumaczeń)")
    mode_input = input("Wybór (Enter=1): ").strip()
    include_translated = (mode_input == '2')

    # 3. Konfiguracja startowa
    print(f"\n{YELLOW}Wskazówka: Wpisz konkretny StringID (np. 1408), a nie numer wiersza.{RESET}")
    start_id_input = input(f"Zacznij od ID (opcjonalnie): ").strip()
    
    current_min_id = start_id_input if start_id_input else None
    is_first_manual_batch = True if current_min_id else False

    # 4. Wielkość paczki
    try:
        batch_size = int(input("Ile rekordów w paczce? (Enter=20): ") or 20)
    except ValueError:
        batch_size = 20

    # === GŁÓWNA PĘTLA CIĄGŁA ===
    while True:
        sql = f"""
            SELECT {pk_col}, {col_en}, {col_pl} FROM {table_name} 
            WHERE {col_en} IS NOT NULL AND {col_en} != ''
        """
        
        if not include_translated:
            sql += f" AND ({col_pl} IS NULL OR {col_pl} = '')"
        
        params = []
        
        if current_min_id is not None:
            if is_first_manual_batch:
                sql += f" AND {pk_col} >= ?"
            else:
                sql += f" AND {pk_col} > ?"
            params.append(current_min_id)
            
        sql += f" ORDER BY {pk_col} LIMIT ?"
        params.append(batch_size)

        cursor.execute(sql, params)
        rows = cursor.fetchall()

        if not rows:
            print(f"\n{GREEN}🎉 Brak kolejnych rekordów do tłumaczenia!{RESET}")
            break

        print(f"\n{BLUE}=== PODGLĄD PACZKI: {len(rows)} rekordów (od ID {rows[0][0]}) ==={RESET}")
        
        print(f"{GRAY}Oto co jest obecnie w bazie (AI dostanie tylko oryginał):{RESET}")
        for r_id, r_en, r_pl in rows:
            pl_preview = r_pl if r_pl else f"{RED}[BRAK]{RESET}"
            en_preview = r_en.replace('\n', ' ')[:50]
            print(f" ID: {r_id:<5} | PL: {pl_preview:<30} | EN: {en_preview}...")

        prompt = generate_batch_prompt(rows)
        
        print(f"\n{YELLOW}--- SKOPIUJ PONIŻSZY TEKST DO CZATU AI ---{RESET}")
        print(prompt)
        print(f"{YELLOW}---------------------------------------------{RESET}")
        
        print(f"\n{BOLD}Co dalej?{RESET}")
        print(" [t] - Mam odpowiedź, wklejam (Enter)")
        print(" [s] - Pomiń tę paczkę (idź do następnych ID)")
        print(" [q] - Zakończ pracę")
        action = input("> ").strip().lower()
        
        if action == 'q':
            break
        
        if action == 's':
            current_min_id = rows[-1][0]
            is_first_manual_batch = False
            print("Pomijam...")
            continue

        print(f"\n{GREEN}Wklej odpowiedź AI poniżej (zakończoną EOF):{RESET}")
        print("-" * 40)

        input_lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'EOF':
                    break
                input_lines.append(line)
            except EOFError:
                break
        
        full_response = "\n".join(input_lines)

        if full_response:
            # TU BYŁ BŁĄD - TERAZ JEST OK
            saved_count, last_processed_id = parse_and_save(full_response, table_name, pk_col, col_pl, cursor)
            conn.commit()
            
            # Aktualizacja paginacji - jeśli coś zapisano, używamy ostatniego ID
            if last_processed_id:
                current_min_id = last_processed_id
            else:
                # Jeśli nic nie zapisano, ale pobraliśmy rekordy, bierzemy ostatni z pobranych
                current_min_id = rows[-1][0]
                
            is_first_manual_batch = False
            
            print(f"\n💾 Zapisano {saved_count} tłumaczeń.")
            cont = input(f"\n{CYAN}Naciśnij ENTER aby pobrać kolejną paczkę (lub 'q' aby wyjść)...{RESET}")
            if cont.lower() == 'q':
                break
        else:
            print("Pusty wsad.")

    conn.close()
    print("\n👋 Zakończono sesję.")

if __name__ == "__main__":
    main()
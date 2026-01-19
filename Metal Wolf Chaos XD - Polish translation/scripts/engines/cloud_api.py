#!/usr/bin/env python3
# engines/cloud_api.py

import sys
import time
import sqlite3
import os

# Próba importu bibliotek API - nieobowiązkowe jeśli używasz local,
# ale wymagane dla tego modułu.
try:
    from anthropic import Anthropic
    from openai import OpenAI
except ImportError:
    pass # Obsłużymy to przy uruchomieniu

# Dodajemy ścieżkę rodzica, żeby widzieć config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config_translator as cfg

# Zmienne globalne klienta
client = None

def init_api():
    """Inicjalizuje klienta API na podstawie configu."""
    global client
    
    if cfg.API_PROVIDER == "anthropic":
        if "anthropic" not in sys.modules:
            print("❌ Brak biblioteki 'anthropic'. Zainstaluj: pip install anthropic")
            sys.exit(1)
        client = Anthropic(api_key=cfg.API_KEY)
        print(f"☁️  Silnik: Anthropic (Claude) | Model: {cfg.API_MODEL}")
        
    elif cfg.API_PROVIDER == "openai" or cfg.API_PROVIDER == "deepseek":
        if "openai" not in sys.modules:
            print("❌ Brak biblioteki 'openai'. Zainstaluj: pip install openai")
            sys.exit(1)
        
        base_url = "https://api.deepseek.com" if cfg.API_PROVIDER == "deepseek" else None
        client = OpenAI(api_key=cfg.API_KEY, base_url=base_url)
        print(f"☁️  Silnik: OpenAI/DeepSeek | Model: {cfg.API_MODEL}")
    
    else:
        print(f"❌ Nieznany API_PROVIDER: {cfg.API_PROVIDER}")
        sys.exit(1)

def translate_text(text_en, context_hint=""):
    """Uniwersalna funkcja tłumacząca dla Cloud API."""
    if not client: init_api()
    if not text_en or not text_en.strip(): return None

    # System Prompt (Wspólny)
    system_prompt = """Jesteś tłumaczem gier wideo (lokalizacja EN -> PL).
ZASADY:
1. Styl: Naturalny, gamingowy, dopasowany do kontekstu.
2. Nie dodawaj komentarzy ("Oto tłumaczenie"). Zwróć SAM tekst.
3. Zachowaj tagi i zmienne (%s, <br>) nienaruszone.
4. Pamiętaj o polskiej gramatyce."""

    try:
        # Obsługa Anthropic (Claude)
        if cfg.API_PROVIDER == "anthropic":
            msg = client.messages.create(
                model=cfg.API_MODEL,
                max_tokens=1000,
                temperature=0.1,
                system=system_prompt,
                messages=[{"role": "user", "content": f"Tłumacz: {text_en}"}]
            )
            return msg.content[0].text.strip()

        # Obsługa OpenAI / DeepSeek
        else:
            resp = client.chat.completions.create(
                model=cfg.API_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text_en}
                ],
                temperature=0.1
            )
            return resp.choices[0].message.content.strip()

    except Exception as e:
        print(f"❌ API Error: {e}")
        time.sleep(1)
        return None

def process_database():
    """Główna pętla przetwarzania (Skopiowana logika iteracji)."""
    print("🚀 Uruchamianie tłumaczenia w chmurze...")
    
    if not cfg.DB_PATH.exists():
        print("❌ Baza nie istnieje.")
        return

    conn = sqlite3.connect(cfg.DB_PATH)
    cursor = conn.cursor()
    init_api() # Upewnij się, że klient jest gotowy
    
    total_count = 0

    for table_conf in cfg.TABLES_TO_TRANSLATE:
        table = table_conf['table_name']
        pk = table_conf['id_column']
        print(f"\n📊 Tabela: {table}")

        # Sprawdź czy tabela istnieje
        try: cursor.execute(f"SELECT COUNT(*) FROM {table}")
        except: continue

        for col_en, col_pl in table_conf['columns']:
            try: cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_pl} TEXT")
            except: pass

            query = f"""
                SELECT {pk}, {col_en} FROM {table}
                WHERE {col_en} IS NOT NULL AND {col_en} != ''
                AND length({col_en}) >= ?
                AND ({col_pl} IS NULL OR {col_pl} = '')
            """
            cursor.execute(query, (table_conf['min_length'],))
            rows = cursor.fetchall()
            
            if not rows: continue
            print(f"   📝 {col_en} -> {col_pl}: {len(rows)} wierszy.")

            for i, (row_id, text_en) in enumerate(rows, 1):
                clean_en = text_en.replace('\n', ' ').strip()
                print(f"     [{i}/{len(rows)}] EN: {clean_en[:50]}...")
                
                translated = translate_text(text_en)
                
                if translated:
                    print(f"       ✅ PL: {translated[:50]}...")
                    cursor.execute(f"UPDATE {table} SET {col_pl} = ? WHERE {pk} = ?", (translated, row_id))
                    total_count += 1
                
                if i % 5 == 0: conn.commit()
                
                # Rate limit (bezpiecznik)
                time.sleep(0.2)

            conn.commit()
    conn.close()
    print(f"\n🎉 Zakończono. Przetłumaczono: {total_count}")

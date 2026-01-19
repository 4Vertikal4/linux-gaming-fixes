#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# engines/local_torch.py

import torch
import os
import sys
import time
import re
import sqlite3
import gc
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import transformers

# Import konfiguracji
# Dodajemy ścieżkę rodzica, żeby widzieć config, jeśli uruchamiamy z podkatalogu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import config_translator as cfg
except ImportError:
    print("❌ Błąd: Nie znaleziono pliku config_translator.py!")
    sys.exit(1)

# Fix encoding & threads
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ["OMP_NUM_THREADS"] = "1"
torch.set_num_threads(1)
transformers.logging.set_verbosity_error()

print(f"🎮 AI Game Translator Engine (Local) - {cfg.GAME_NAME}")

# =============================================================================
# 💤 LAZY LOADING (Zmienne globalne puste na starcie)
# =============================================================================
model = None
tokenizer = None
device = None

def ensure_model_loaded():
    """
    Ładuje model do VRAM tylko wtedy, gdy jest to absolutnie konieczne.
    Dzięki temu skrypt importuje się w 0.1s, a ładuje dopiero przy pierwszym tłumaczeniu.
    """
    global model, tokenizer, device
    
    if model is not None:
        return # Już załadowany, wychodzimy

    print("==================================================")
    print(f"🚀 {cfg.MODEL_NAME}: Budzenie bestii... (Ładowanie do VRAM)")
    print("⏳ To potrwa kilka-kilkanaście sekund...")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    bnb_config = BitsAndBytesConfig(
        load_in_8bit=not cfg.USE_4BIT_QUANTIZATION,
        load_in_4bit=cfg.USE_4BIT_QUANTIZATION,
        bnb_4bit_compute_dtype=torch.float16 if cfg.USE_4BIT_QUANTIZATION else None,
        bnb_8bit_compute_dtype=torch.float16 if not cfg.USE_4BIT_QUANTIZATION else None,
    )

    tokenizer = AutoTokenizer.from_pretrained(cfg.MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        cfg.MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        low_cpu_mem_usage=True,
        torch_dtype=torch.float16,
    )
    print("✅ Model gotowy do pracy!")
    print("==================================================")

# 2. FUNKCJE POMOCNICZE

def clean_ai_response(text):
    """Czyści odpowiedź AI ze śmieci zdefiniowanych w configu."""
    if not text: return ""
    
    for pattern in cfg.PATTERNS_TO_REMOVE:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Podstawowe czyszczenie spacji
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def translate_text(english_text, context_hint=""):
    """Wysyła zapytanie do modelu."""
    if not english_text or not english_text.strip():
        return None

    # KLUCZOWA ZMIANA: Ładujemy model dopiero tutaj!
    ensure_model_loaded()

    # Prompt inżynieria
    prompt = f"""Przetłumacz poniższy tekst z gry wideo z angielskiego na polski.
ZASADY:
1. Zachowaj klimat gry.
2. Nie dodawaj komentarzy typu "Oto tłumaczenie".
3. Zachowaj znaki specjalne (np. %s, <br>).

Tekst: "{english_text}"
Tłumaczenie:"""

    messages = [
        {"role": "user", "content": prompt}
    ]
    
    try:
        input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                max_new_tokens=min(150, len(english_text) * 3),
                do_sample=False, # Deterministycznie
                temperature=cfg.TEMPERATURE,
                pad_token_id=tokenizer.eos_token_id,
            )
        
        generated_ids = outputs[0][len(input_ids[0]):]
        raw_translation = tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        return clean_ai_response(raw_translation)

    except Exception as e:
        print(f"❌ Błąd generowania: {e}")
        return None
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# 3. GŁÓWNA PĘTLA PRZETWARZANIA

def process_database():
    if not cfg.DB_PATH.exists():
        print(f"❌ Błąd: Baza danych nie istnieje: {cfg.DB_PATH}")
        return

    # Jeśli uruchamiamy pełne tłumaczenie automatem, ładujemy model od razu na początku
    ensure_model_loaded()

    conn = sqlite3.connect(cfg.DB_PATH)
    cursor = conn.cursor()

    total_stats = {'success': 0, 'failed': 0, 'skipped': 0}

    for table_conf in cfg.TABLES_TO_TRANSLATE:
        table = table_conf['table_name']
        pk = table_conf['id_column']
        
        print(f"\n📊 Przetwarzanie tabeli: {table}")
        print("-" * 40)

        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
        except sqlite3.OperationalError:
            print(f"⚠️  Tabela {table} nie istnieje w bazie! Pomijam.")
            continue

        for col_en, col_pl in table_conf['columns']:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_pl} TEXT")
                print(f"   ➕ Dodano kolumnę: {col_pl}")
            except sqlite3.OperationalError:
                pass 

            query = f"""
                SELECT {pk}, {col_en} FROM {table}
                WHERE {col_en} IS NOT NULL AND {col_en} != ''
                AND length({col_en}) >= ? AND length({col_en}) <= ?
                AND ({col_pl} IS NULL OR {col_pl} = '')
            """
            cursor.execute(query, (table_conf['min_length'], table_conf['max_length']))
            rows = cursor.fetchall()
            
            print(f"   📝 Kolumna {col_en} -> {col_pl}: {len(rows)} wierszy do zrobienia.")

            if not rows:
                continue

            for i, (row_id, text_en) in enumerate(rows, 1):
                print(f"     [{i}/{len(rows)}] ID: {row_id} | EN: {text_en[:50]}...")
                
                translated = None
                for attempt in range(cfg.MAX_ATTEMPTS):
                    translated = translate_text(text_en)
                    if translated and len(translated) > 0 and translated != text_en:
                        break 
                    time.sleep(0.5) 
                
                if translated:
                    print(f"       ✅ PL: {translated[:50]}...")
                    cursor.execute(f"UPDATE {table} SET {col_pl} = ? WHERE {pk} = ?", (translated, row_id))
                    total_stats['success'] += 1
                    if i % 10 == 0: conn.commit()
                else:
                    print(f"       ❌ Niepowodzenie.")
                    total_stats['failed'] += 1

            conn.commit()

    conn.close()
    print("\n" + "="*50)
    print(f"🎉 Zakończono! Statystyki: ✅ {total_stats['success']} | ❌ {total_stats['failed']}")

if __name__ == "__main__":
    process_database()
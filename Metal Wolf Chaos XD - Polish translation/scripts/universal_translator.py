#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 03_Run_Translator.py (dawniej universal_translator.py)

import torch
import os
import sys
import time
import re
import sqlite3
import gc
from datetime import datetime
# Importy ML robimy na górze, ale inicjalizację później
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import transformers

try:
    import config_translator as cfg
except ImportError:
    print("❌ Błąd: Nie znaleziono pliku config_translator.py!")
    sys.exit(1)

# Konfiguracja środowiska
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ["OMP_NUM_THREADS"] = "1"
torch.set_num_threads(1)
transformers.logging.set_verbosity_error()

# Zmienne globalne (Lazy Loading)
model = None
tokenizer = None
device = None

def ensure_model_loaded():
    """Ładuje model tylko wtedy, gdy jest potrzebny."""
    global model, tokenizer, device
    
    if model is not None:
        return # Już załadowany

    print(f"\n🤖 Inicjalizacja AI ({cfg.MODEL_NAME})... Proszę czekać...")
    
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
    print("✅ Model gotowy do pracy!\n")

def clean_ai_response(text):
    if not text: return ""
    for pattern in cfg.PATTERNS_TO_REMOVE:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def translate_text(english_text):
    """Główna funkcja tłumacząca."""
    if not english_text or not english_text.strip():
        return None

    # 1. Upewnij się, że model jest załadowany
    ensure_model_loaded()

    prompt = f"""Przetłumacz poniższy tekst z gry wideo z angielskiego na polski.
ZASADY:
1. Zachowaj klimat gry.
2. Nie dodawaj komentarzy typu "Oto tłumaczenie".
3. Zachowaj znaki specjalne (np. %s, <br>).

Tekst: "{english_text}"
Tłumaczenie:"""

    messages = [{"role": "user", "content": prompt}]
    
    try:
        input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True).to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                max_new_tokens=min(150, len(english_text) * 3),
                do_sample=False,
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

# --- Logika uruchamiania jako skrypt główny ---
def process_database():
    if not cfg.DB_PATH.exists():
        print(f"❌ Błąd: Baza danych nie istnieje: {cfg.DB_PATH}")
        return

    conn = sqlite3.connect(cfg.DB_PATH)
    cursor = conn.cursor()
    
    # Załaduj model raz na początku przy masowym tłumaczeniu
    ensure_model_loaded()

    total_stats = {'success': 0, 'failed': 0}

    for table_conf in cfg.TABLES_TO_TRANSLATE:
        table = table_conf['table_name']
        pk = table_conf['id_column']
        
        print(f"\n📊 Przetwarzanie tabeli: {table}")
        
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
        except sqlite3.OperationalError:
            continue

        for col_en, col_pl in table_conf['columns']:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_pl} TEXT")
            except sqlite3.OperationalError: pass

            query = f"""
                SELECT {pk}, {col_en} FROM {table}
                WHERE {col_en} IS NOT NULL AND {col_en} != ''
                AND length({col_en}) >= ? AND length({col_en}) <= ?
                AND ({col_pl} IS NULL OR {col_pl} = '')
            """
            cursor.execute(query, (table_conf['min_length'], table_conf['max_length']))
            rows = cursor.fetchall()
            
            if not rows: continue
            print(f"   📝 {col_en} -> {col_pl}: {len(rows)} linii.")

            for i, (row_id, text_en) in enumerate(rows, 1):
                print(f"     [{i}/{len(rows)}] ID: {row_id}")
                
                translated = None
                for attempt in range(cfg.MAX_ATTEMPTS):
                    translated = translate_text(text_en)
                    if translated and translated != text_en: break
                    time.sleep(0.2)
                
                if translated:
                    cursor.execute(f"UPDATE {table} SET {col_pl} = ? WHERE {pk} = ?", (translated, row_id))
                    total_stats['success'] += 1
                    if i % 5 == 0: conn.commit()
                else:
                    total_stats['failed'] += 1

            conn.commit()
    conn.close()

if __name__ == "__main__":
    print(f"🎮 AI Game Translator - {cfg.GAME_NAME}")
    process_database()

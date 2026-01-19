#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# translate_metal_wolf_chaos_1.8_FIXED.py

import torch
import os
import sys
import time
import re
import sqlite3
import shutil
from pathlib import Path
import gc
import unicodedata
from datetime import datetime

# Fix encoding for console output
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'

# CPU PROTECTION
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
torch.set_num_threads(1)
torch.set_num_interop_threads(1)

print("🎮 Metal Wolf Chaos XD - Complete Polish Translation (FIXED)")
print("🛡️ CPU Protection: ACTIVE")
print("="*50)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import transformers
transformers.logging.set_verbosity_error()

model_name = "speakleash/Bielik-4.5B-v3.0-Instruct"

print("Loading Bielik model...")

bnb_config = BitsAndBytesConfig(
    load_in_8bit=True,
    bnb_8bit_compute_dtype=torch.float16,
    bnb_8bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    low_cpu_mem_usage=True,
    torch_dtype=torch.float16,
)

# OPTIMIZATION: Cache for repeated translations
translation_cache = {}
CACHE_MAX_SIZE = 1000

def extract_pure_translation(text):
    """Aggressive extraction - remove all meta-commentary"""
    if not text:
        return ""
    
    patterns_to_remove = [
        r'^\s*\*+\s*Tłumaczenie:\s*\*+\s*',
        r'^Tłumaczenie:\s*',
        r'^Oto tłumaczenie:\s*',
        r'^Tłumaczenie na język polski[^:]*:\s*',
        r'\s*–\s*\([^)]*\)\s*',
        r'\s*\([^)]*\)\s*',
        r'\s*\[[^\]]*\]\s*',
        r'\s*–[^"]*$',
        r'\s*😊\s*', r'\s*😄\s*', r'\s*✨\s*',
        r'^\s*"\s*|\s*"\s*$',
        r'\s*\*\*[^*]*\*\*\s*',
        r'\s*\*[^*]*\*\s*',
    ]
    
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    unwanted_phrases = [
        'żartobliwie',
        'z nutą pewności siebie', 
        'w stylu gry akcji',
        'zachowując styl',
        'Albo bardziej potocznie',
        'z polskim dubbingiem',
        'z użyciem potocznego stylu'
    ]
    
    for phrase in unwanted_phrases:
        text = text.replace(phrase, '')
    
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^\s*[.,!?;:\-–]\s*', '', text)
    
    return text

def validate_translation(polish_text, english_text):
    """Optimized validation"""
    if not polish_text or len(polish_text.strip()) < 2:
        return False
    
    pure_polish = extract_pure_translation(polish_text)
    if not pure_polish or len(pure_polish.strip()) < 2:
        return False
    
    invalid_patterns = [
        r'^\s*\[/INST\]', r'^\s*\[OUT\]', r'^Original text',
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, pure_polish, re.IGNORECASE):
            return False
    
    if len(pure_polish) < len(english_text) * 0.3:
        return False
    
    return True

def clean_translation(text):
    """Fast cleaning"""
    text = extract_pure_translation(text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > 1:
        text = text[0].upper() + text[1:]
    return text

def translate_deterministic(english_text):
    """Translation using strict translation-only prompt"""
    
    cache_key = english_text.strip().lower()
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    if not english_text or not english_text.strip():
        return None

    strict_prompt = """Przetłumacz poniższy tekst z angielskiego na polski. 
ZASADY:
1. Tylko tłumaczenie, bez żadnych dodatkowych tekstów
2. Żadnych prefiksów jak "Tłumaczenie:", "**Tłumaczenie:**", "Oto tłumaczenie:"
3. Żadnych opisów w nawiasach jak "(żartobliwie)", "(z nutą pewności siebie)"
4. Żadnych emotikon, żadnych symboli
5. Żadnych komentarzy, żadnych wyjaśnień
6. Tylko czyste tłumaczenie

Tekst do przetłumaczenia:"""

    messages = [
        {"role": "system", "content": strict_prompt},
        {"role": "user", "content": f'"{english_text}"'}
    ]
    
    try:
        input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt", add_generation_prompt=True)
        input_ids = input_ids.to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                max_new_tokens=min(100, len(english_text) * 2),
                do_sample=False,
                temperature=0.1,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1,
            )
        
        generated_ids = outputs[0][len(input_ids[0]):]
        translation = tokenizer.decode(generated_ids, skip_special_tokens=True)
        
        if len(translation_cache) >= CACHE_MAX_SIZE:
            translation_cache.pop(next(iter(translation_cache)))
        translation_cache[cache_key] = translation
        
        return translation

    except Exception as e:
        print(f"❌ Translation error: {e}")
        return None
    finally:
        torch.cuda.empty_cache()
        gc.collect()

def translate_with_validation(english_text, max_attempts=2):
    """Optimized validation pipeline"""
    
    for attempt in range(max_attempts):
        polish = translate_deterministic(english_text)
        
        if polish:
            clean_polish = clean_translation(polish)
            if clean_polish and validate_translation(clean_polish, english_text):
                return clean_polish
        
        if attempt < max_attempts - 1:
            time.sleep(0.2)
    
    return None

def get_table_translation_config():
    """FIXED configuration based on actual database structure"""
    
    return [
        # maps table - dialogues (already working well)
        {
            'table_name': 'maps',
            'en_columns': ['Value_en_US'],
            'pl_columns': ['Value_pl_PL'],
            'id_column': 'StringID',
            'min_length': 5,
            'max_length': 100
        },
        
        # game table - game text
        {
            'table_name': 'game', 
            'en_columns': ['Value_en_US'],
            'pl_columns': ['Value_pl_PL'],
            'id_column': 'StringID',
            'min_length': 5,
            'max_length': 100
        },
        
        # item table - item names and descriptions (FIXED: Description_en_US instead of Short/Full)
        {
            'table_name': 'item',
            'en_columns': ['Name_en_US', 'Description_en_US'],
            'pl_columns': ['Name_pl_PL', 'Description_pl_PL'],
            'id_column': 'StringID',
            'min_length': 3,
            'max_length': 200
        },
        
        # magic table - magic/spell names and descriptions  
        {
            'table_name': 'magic',
            'en_columns': ['Name_en_US', 'ShortDescription_en_US', 'FullDescription_en_US'],
            'pl_columns': ['Name_pl_PL', 'ShortDescription_pl_PL', 'FullDescription_pl_PL'],
            'id_column': 'StringID',
            'min_length': 3,
            'max_length': 200
        },
        
        # menu table - UI text
        {
            'table_name': 'menu',
            'en_columns': ['Value_en_US'],
            'pl_columns': ['Value_pl_PL'], 
            'id_column': 'StringID',
            'min_length': 3,
            'max_length': 50
        },
        
        # stage table - stage names and descriptions (FIXED: correct column names)
        {
            'table_name': 'stage',
            'en_columns': ['Name_en_US', 'MissionOverview_en_US', 'WorldMapText_en_US'],
            'pl_columns': ['Name_pl_PL', 'MissionOverview_pl_PL', 'WorldMapText_pl_PL'],
            'id_column': 'StringID', 
            'min_length': 3,
            'max_length': 150
        },
        
        # weapon table - weapon names and descriptions
        {
            'table_name': 'weapon',
            'en_columns': ['Name', 'ShortDescription_en_US', 'FullDescription_en_US', 'Category_en_US'],
            'pl_columns': ['Name_pl_PL', 'ShortDescription_pl_PL', 'FullDescription_pl_PL', 'Category_pl_PL'],
            'id_column': 'StringID',
            'min_length': 3,
            'max_length': 150
        },
        
        # accessory table - accessory items (FIXED: correct column names)
        {
            'table_name': 'accessory',
            'en_columns': ['Name_en_US', 'ShortDescription_en_US', 'FullDescription_en_US'],
            'pl_columns': ['Name_pl_PL', 'ShortDescription_pl_PL', 'FullDescription_pl_PL'],
            'id_column': 'StringID', 
            'min_length': 3,
            'max_length': 200
        },
        
        # creature table - creature names (FIXED: complex structure)
        {
            'table_name': 'creature', 
            'en_columns': [
                'AbbreviatedName_en_US', 
                'FormalName_en_US', 
                'Description_en_US', 
                'Category_en_US'
            ],
            'pl_columns': [
                'AbbreviatedName_pl_PL', 
                'FormalName_pl_PL', 
                'Description_pl_PL', 
                'Category_pl_PL'
            ],
            'id_column': 'StringID',
            'min_length': 3,
            'max_length': 200
        }
    ]

def ensure_polish_columns(cursor, table_config):
    """Create Polish columns if they don't exist"""
    table_name = table_config['table_name']
    pl_columns = table_config['pl_columns']
    
    # Get existing columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    columns_added = 0
    for pl_col in pl_columns:
        if pl_col not in existing_columns:
            print(f"   ➕ Adding Polish column: {pl_col}")
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {pl_col} TEXT")
            columns_added += 1
    
    return columns_added

def process_table_column(cursor, table_config, en_column, pl_column):
    """Process a single column in a table"""
    
    table_name = table_config['table_name']
    id_column = table_config['id_column']
    min_length = table_config['min_length']
    max_length = table_config['max_length']
    
    print(f"   📝 Processing: {en_column} → {pl_column}")
    
    # Check what needs to be translated
    cursor.execute(f"""
        SELECT COUNT(*) FROM {table_name} 
        WHERE {pl_column} IS NOT NULL 
        AND {pl_column} != {en_column}
        AND {pl_column} != ''
    """)
    already_translated = cursor.fetchone()[0]

    cursor.execute(f"""
        SELECT COUNT(*) FROM {table_name} 
        WHERE {en_column} IS NOT NULL 
        AND {en_column} != ''
        AND length({en_column}) BETWEEN ? AND ?
        AND ({pl_column} IS NULL OR {pl_column} = {en_column} OR {pl_column} = '')
    """, (min_length, max_length))
    
    remaining_to_translate = cursor.fetchone()[0]

    print(f"     ✅ Already translated: {already_translated}")
    print(f"     📋 Remaining: {remaining_to_translate}")

    if remaining_to_translate == 0:
        print("     ⏩ Skipping - no text to translate")
        return 0, 0

    # Get all translatable content
    cursor.execute(f"""
        SELECT {id_column}, {en_column} 
        FROM {table_name} 
        WHERE {en_column} IS NOT NULL 
        AND {en_column} != ''
        AND length({en_column}) BETWEEN ? AND ?
        AND ({pl_column} IS NULL OR {pl_column} = {en_column} OR {pl_column} = '')
        ORDER BY {id_column}
    """, (min_length, max_length))
    
    all_texts = cursor.fetchall()
    print(f"     📋 Loaded {len(all_texts)} lines to translate")

    success = 0
    failed = 0
    start_time = time.time()
    
    for i, (row_id, english) in enumerate(all_texts, 1):
        english = english.strip()
        
        if i % 10 == 0 or i <= 3:
            print(f"     [{i}/{len(all_texts)}] EN: {english[:60]}...")
        
        # Dynamic sleep based on line complexity
        sleep_time = max(0.5, min(2.0, len(english) / 50))
        time.sleep(sleep_time)
        
        # Translate using proven function
        polish = translate_with_validation(english)
        
        if polish:
            success += 1
            cursor.execute(
                f"UPDATE {table_name} SET {pl_column} = ? WHERE {id_column} = ?",
                (polish, row_id)
            )
            if i <= 3:  # Show first few translations
                print(f"       PL: {polish}")
        else:
            failed += 1
            # Leave as English if translation fails
            cursor.execute(
                f"UPDATE {table_name} SET {pl_column} = ? WHERE {id_column} = ?", 
                (english, row_id)
            )
        
        # Progress tracking
        if i % 20 == 0:
            elapsed = time.time() - start_time
            if i < len(all_texts):
                eta = (elapsed / i) * (len(all_texts) - i) / 60
                print(f"     💾 Progress: {i}/{len(all_texts)} | ✅ {success} | ❌ {failed}")
                print(f"     ⏱️  ETA: {eta:.1f} minutes")
            
            # Clear cache periodically
            translation_cache.clear()
            torch.cuda.empty_cache()
            gc.collect()
    
    total_time = time.time() - start_time
    print(f"     ✅ Column complete: {success} successful, {failed} failed")
    print(f"     ⏱️  Time: {total_time/60:.1f} minutes")
    
    return success, failed

def process_table(cursor, table_config):
    """Process all columns in a table"""
    
    table_name = table_config['table_name']
    en_columns = table_config['en_columns']
    pl_columns = table_config['pl_columns']
    
    print(f"\n📊 Processing table: {table_name}")
    
    # Ensure Polish columns exist
    columns_added = ensure_polish_columns(cursor, table_config)
    if columns_added > 0:
        print(f"   ✅ Added {columns_added} Polish columns")
    
    table_success = 0
    table_failed = 0
    
    # Process each column pair
    for en_col, pl_col in zip(en_columns, pl_columns):
        success, failed = process_table_column(cursor, table_config, en_col, pl_col)
        table_success += success
        table_failed += failed
    
    return table_success, table_failed

def main():
    # Database setup
    game_db = Path("/home/vertikal/Games/Heroic/Metal Wolf Chaos XD/Media/Texts/texts_may30.db")
    work_dir = Path("../work")
    work_dir.mkdir(exist_ok=True)
    work_db = work_dir / "texts_may30_PL.db"

    print(f"📂 Database: {work_db}")

    conn = sqlite3.connect(work_db)
    cursor = conn.cursor()
    
    # Get translation configuration
    table_configs = get_table_translation_config()
    
    print(f"\n🔍 Found {len(table_configs)} tables to process:")
    for config in table_configs:
        print(f"   • {config['table_name']}: {config['en_columns']} → {config['pl_columns']}")
    
    # Process each table
    total_success = 0
    total_failed = 0
    processed_tables = 0
    
    for table_config in table_configs:
        try:
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_config['table_name'],))
            if not cursor.fetchone():
                print(f"\n⚠️  Table {table_config['table_name']} not found, skipping...")
                continue
                
            success, failed = process_table(cursor, table_config)
            total_success += success
            total_failed += failed
            processed_tables += 1
            conn.commit()  # Commit after each table
            
        except Exception as e:
            print(f"❌ Error processing table {table_config['table_name']}: {e}")
            conn.rollback()
            continue
    
    conn.close()
    
    print("\n" + "="*60)
    print(f"🎉 TRANSLATION COMPLETE!")
    print(f"✅ Total successful: {total_success}")
    print(f"❌ Total failed: {total_failed}") 
    print(f"📊 Tables processed: {processed_tables}/{len(table_configs)}")
    print(f"💾 Database saved: {work_db}")

if __name__ == "__main__":
    main()

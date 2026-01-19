# config_translator.py
import os
import sqlite3
from pathlib import Path

# =============================================================================
# 🎛️ WYBÓR SILNIKA (ENGINE)
# =============================================================================
# "local" = Twój Bielik/Llama na GPU (korzysta z engines/local_torch.py)
# "cloud" = API Claude/DeepSeek (korzysta z engines/cloud_api.py)

TRANSLATION_MODE = "local" 

# =============================================================================
# 🏠 USTAWIENIA DLA TRYBU: LOCAL (GPU)
# =============================================================================
# Rekomendowany model na 8GB VRAM: "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"
# Twój obecny model na <6GB VRAM: "speakleash/Bielik-4.5B-v3.0-Instruct"

MODEL_NAME = "speakleash/Bielik-4.5B-v3.0-Instruct"
USE_4BIT_QUANTIZATION = True

# =============================================================================
# ☁️ USTAWIENIA DLA TRYBU: CLOUD (API)
# =============================================================================
# Dostawcy: "anthropic" (Claude), "deepseek", "openai"

API_PROVIDER = "anthropic"
API_KEY = "sk-ant-..."  # Tutaj wkleisz klucz, gdy zdecydujesz się na chmurę
API_MODEL = "claude-3-5-sonnet-20241022" 

# =============================================================================
# 🔧 GŁÓWNA KONFIGURACJA (WSPÓLNA)
# =============================================================================

GAME_NAME = "Metal Wolf Chaos XD"

# Ścieżki
DB_PATH = Path("../work/texts_may30_PL.db")
GAME_DB_PATH = Path("/home/vertikal/Games/Heroic/Metal Wolf Chaos XD/Media/Texts/texts_may30.db")

# Parametry tłumaczenia
MAX_ATTEMPTS = 2        # Ile razy ponawiać próbę
TEMPERATURE = 0.1       # Kreatywność (0.1 = niska/precyzyjna)

# =============================================================================
# 🧠 AUTOMATYCZNE WYKRYWANIE TABEL (AUTO-DISCOVERY)
# =============================================================================

def discover_translation_config(database_path):
    """
    Skanuje bazę SQLite i automatycznie tworzy pary kolumn do tłumaczenia
    na podstawie nazewnictwa (np. szuka _en_US i paruje z _pl_PL).
    """
    if not database_path.exists():
        print(f"⚠️  Config Warning: Baza danych nie istnieje w {database_path}")
        return []

    config_list = []
    
    try:
        # Otwieramy połączenie tylko do odczytu struktury
        conn = sqlite3.connect(f"file:{database_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        # 1. Pobierz wszystkie tabele
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Tabele techniczne, które ignorujemy (np. systemowe SQLite lub nasze backupy)
        ignored_tables = ['sqlite_sequence', 'encoding_test']

        for table in tables:
            if table in ignored_tables or table.endswith('_backup'):
                continue

            # 2. Pobierz kolumny dla danej tabeli
            cursor.execute(f"PRAGMA table_info({table})")
            columns_info = cursor.fetchall() # (id, name, type, notnull, dflt_value, pk)
            
            column_names = [col[1] for col in columns_info]
            
            # Próbujemy zgadnąć Primary Key (zazwyczaj StringID lub ID)
            pk_column = "StringID" # Domyślnie w tej grze
            for col in column_names:
                if col.lower() == 'id': pk_column = col
                if col.lower() == 'stringid': pk_column = col

            pairs = []
            
            # 3. Logika parowania (Heurystyka)
            for col in column_names:
                # Wariant A: Kolumny z sufiksem _en_US
                if col.endswith('_en_US'):
                    target_col = col.replace('_en_US', '_pl_PL')
                    pairs.append((col, target_col))
                
                # Wariant B: Wyjątek dla kolumny "Name" (często w tabeli items/weapons)
                # Jeśli jest "Name", a nie ma "Name_en_US", to tłumaczymy "Name" -> "Name_pl_PL"
                elif col == 'Name' and 'Name_en_US' not in column_names:
                    pairs.append(('Name', 'Name_pl_PL'))

            # Jeśli znaleźliśmy jakieś pary do tłumaczenia w tej tabeli, dodajemy do configu
            if pairs:
                config_list.append({
                    'table_name': table,
                    'id_column': pk_column,
                    'columns': pairs,
                    'min_length': 2,    # Ignoruj pojedyncze litery
                    'max_length': 600   # Limit długości tekstu
                })

        conn.close()
        
    except Exception as e:
        print(f"⚠️  Config Error: Nie udało się automatycznie wykryć tabel: {e}")
        return []

    # Sortujemy, żeby kolejność była stała (np. alfabetycznie po nazwie tabeli)
    return sorted(config_list, key=lambda x: x['table_name'])

# =============================================================================
# 🚀 GENEROWANIE LISTY
# =============================================================================

# To się wykonuje w momencie importu pliku config
TABLES_TO_TRANSLATE = discover_translation_config(DB_PATH)

# Debug: Jeśli uruchomisz ten plik bezpośrednio, pokaże co znalazł
if __name__ == "__main__":
    print(f"🔍 Znaleziono {len(TABLES_TO_TRANSLATE)} tabel do tłumaczenia:")
    for t in TABLES_TO_TRANSLATE:
        print(f"\n📋 Tabela: {t['table_name']} (PK: {t['id_column']})")
        for src, tgt in t['columns']:
            print(f"   - {src} -> {tgt}")


# =============================================================================
# 🚫 CZYSZCZENIE ODPOWIEDZI AI
# =============================================================================
PATTERNS_TO_REMOVE = [
    r'^\s*\*+\s*Tłumaczenie:\s*\*+\s*',
    r'^Tłumaczenie:\s*',
    r'^Oto tłumaczenie:\s*',
    r'^Tłumaczenie na język polski[^:]*:\s*',
    r'\s*–\s*\([^)]*\)\s*',
    r'^\s*"\s*|\s*"\s*$',
]

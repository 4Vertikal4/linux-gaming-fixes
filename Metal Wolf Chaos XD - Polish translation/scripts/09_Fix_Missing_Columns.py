import sqlite3
from pathlib import Path

# ŚCIEŻKA DO BAZY GRY
GAME_DB = Path("/home/vertikal/Games/Heroic/Metal Wolf Chaos XD/Media/Texts/texts_may30.db")

def fix_structure():
    print("🏗️  Rozpoczynam structuralny upgrade bazy gry...")
    
    if not GAME_DB.exists():
        print("❌ Nie znaleziono bazy gry!")
        return

    conn = sqlite3.connect(GAME_DB)
    cursor = conn.cursor()

    # List tabel do sprawdzenia
    tables = ["game", "weapon", "accessory", "magic", "stage"]

    for table in tables:
        try:
            # Sprawdzamy istniejące kolumny
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [c[1] for c in cursor.fetchall()]

            # Jeśli tabela ma Value_en_US ale nie ma Value_ru_RU - dodajemy!
            if "Value_en_US" in columns and "Value_ru_RU" not in columns:
                print(f"➕ Dodaję kolumnę Value_ru_RU do tabeli: {table}")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN Value_ru_RU TEXT")
            
            # Dla tabel typu weapon/stage, gdzie nazwy są w 'Name'
            if "Name" in columns and "Name_ru_RU" not in columns:
                print(f"➕ Dodaję kolumnę Name_ru_RU do tabeli: {table}")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN Name_ru_RU TEXT")

            # Dodajmy też kolumny opisu jeśli ich nie ma
            if "ShortDescription_en_US" in columns and "ShortDescription_ru_RU" not in columns:
                 cursor.execute(f"ALTER TABLE {table} ADD COLUMN ShortDescription_ru_RU TEXT")
            if "FullDescription_en_US" in columns and "FullDescription_ru_RU" not in columns:
                 cursor.execute(f"ALTER TABLE {table} ADD COLUMN FullDescription_ru_RU TEXT")

        except Exception as e:
            print(f"  ⚠️ Błąd w tabeli {table}: {e}")

    conn.commit()
    conn.close()
    print("\n✅ Struktura bazy zaktualizowana. Teraz możemy wgrać tłumaczenie!")

if __name__ == "__main__":
    fix_structure()

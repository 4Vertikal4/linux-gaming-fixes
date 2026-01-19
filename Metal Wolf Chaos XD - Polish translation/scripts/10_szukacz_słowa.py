import sqlite3
from pathlib import Path

# POPRAWIONA ŚCIEŻKA (Plik został w głównym folderze Texts)
DB_PATH = Path("/home/vertikal/Games/Heroic/Metal Wolf Chaos XD/Media/Texts/texts_may30.db.original_backup")

def deep_search():
    if not DB_PATH.exists():
        print(f"❌ Błąd: Nadal nie widzę pliku w {DB_PATH}")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall() if not t[0].startswith('sqlite')]

    # Szukamy kluczowych fraz menu
    search_terms = ["NEW GAME", "LOAD GAME", "SETTINGS", "EXIT", "OPTIONS"]
    
    print(f"🔍 Przeszukuję oryginał ({DB_PATH.name}) w poszukiwaniu menu...")
    found_any = False
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cursor.fetchall()]
        for col in cols:
            for term in search_terms:
                try:
                    # Szukamy dokładnego dopasowania
                    cursor.execute(f"SELECT StringID, {col} FROM {table} WHERE {col} = ?", (term,))
                    res = cursor.fetchone()
                    if res:
                        print(f"🎯 TRAFIONY! [{term}] -> Tabela: {table}, Kolumna: {col}, ID: {res[0]}")
                        found_any = True
                except: continue
    
    if not found_any:
        print("\n❌ WYNIK: Nie znaleziono fraz menu w bazie danych.")
        print("💡 WNIOSEK: Przyciski menu (Nowa Gra, Wyjście) to OBRAZKI (.dds).")
    else:
        print("\n✅ WYNIK: Menu JEST w bazie danych.")
        print("💡 WNIOSEK: Musimy po prostu poprawnie wypełnić kolumny rosyjskie.")
        
    conn.close()

if __name__ == "__main__":
    deep_search()

import os
import json
import shutil
import sys

# === KONFIGURACJA ===
WORK_DIR = os.path.join(os.path.dirname(__file__), "../phyre_work")
SOURCE_FILE = os.path.join(WORK_DIR, "menu_common_en_US.phyre") # Źródło (tylko do odczytu/kopii)
TARGET_FILE = os.path.join(WORK_DIR, "menu_common_ru_RU.phyre") # Cel (ten plik modyfikujemy)
MODIFIED_DIR = os.path.join(WORK_DIR, "modified")
MAP_FILE = os.path.join(WORK_DIR, "texture_map.json")

def inject_texture(target_id_str):
    print(f"--- 12_Phyre_Texture_Inject v1.0 ---")

    # Konwersja argumentu na int
    try:
        target_id = int(target_id_str)
    except ValueError:
        print("BŁĄD: Podaj numer ID tekstury jako argument (np. 5).")
        return

    # Sprawdzenie środowiska
    if not os.path.exists(MAP_FILE):
        print(f"BŁĄD: Brak mapy {MAP_FILE}. Uruchom najpierw skrypt 11.")
        return

    # Jeśli nie ma pliku docelowego, tworzymy go z kopii oryginału
    if not os.path.exists(TARGET_FILE):
        if os.path.exists(SOURCE_FILE):
            print(f"Tworzenie pliku roboczego: {os.path.basename(TARGET_FILE)}...")
            shutil.copy2(SOURCE_FILE, TARGET_FILE)
        else:
            print(f"BŁĄD: Brak pliku źródłowego {SOURCE_FILE} do utworzenia kopii.")
            return

    # Wczytanie mapy
    with open(MAP_FILE, "r") as f:
        mapping = json.load(f)

    # Szukanie wpisu dla danego ID
    target_info = next((item for item in mapping if item["id"] == target_id), None)
    if not target_info:
        print(f"BŁĄD: ID {target_id} nie istnieje w mapie.")
        return

    # Szukanie zmodyfikowanego pliku
    # Skrypt szuka pliku zaczynającego się od "tex_ID..." w folderze modified
    mod_files = [f for f in os.listdir(MODIFIED_DIR) if f.startswith(f"tex_{target_id:03d}")] if os.path.exists(MODIFIED_DIR) else []
    
    if not mod_files:
        print(f"BŁĄD: Nie znaleziono pliku dla ID {target_id} w katalogu: {MODIFIED_DIR}")
        print(f"Upewnij się, że nazwa pliku zaczyna się od 'tex_{target_id:03d}'")
        return
    
    # Bierzemy pierwszy pasujący (zakładamy, że jest jeden)
    mod_filename = mod_files[0]
    mod_filepath = os.path.join(MODIFIED_DIR, mod_filename)

    offset = target_info['original_offset']
    max_size = target_info['max_size']
    
    print(f"Cel: ID {target_id} ({mod_filename})")
    print(f"Offset w pliku: {hex(offset)}")
    print(f"Dostępne miejsce: {max_size} bajtów")

    with open(mod_filepath, "rb") as f:
        new_data = f.read()

    new_size = len(new_data)
    print(f"Rozmiar nowego pliku: {new_size} bajtów")

    # SAFETY CHECK: Rozmiar
    if new_size > max_size:
        diff = new_size - max_size
        print(f"❌ KRYTYCZNY BŁĄD: Nowy plik jest za duży o {diff} bajtów!")
        print("Modyfikacja musi być mniejsza lub równa oryginałowi.")
        print("Spróbuj zapisać bez mipmap lub zmień kompresję, jeśli to możliwe.")
        return

    # WSTRZYKIWANIE
    print("Wstrzykiwanie danych...")
    with open(TARGET_FILE, "r+b") as f:
        f.seek(offset)
        f.write(new_data)
        
        # Padding zerami (czyszczenie starych śmieci, jeśli nowy plik jest mniejszy)
        remaining = max_size - new_size
        if remaining > 0:
            f.write(b'\x00' * remaining)
            print(f"Dodano {remaining} bajtów paddingu.")

    print(f"✅ SUKCES: Zaktualizowano {os.path.basename(TARGET_FILE)}.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Użycie: python3 12_Phyre_Texture_Inject.py <ID_TEKSTURY>")
        print("Przykład: python3 12_Phyre_Texture_Inject.py 5")
    else:
        inject_texture(sys.argv[1])

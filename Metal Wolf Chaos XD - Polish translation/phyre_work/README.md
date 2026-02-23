📂 MWC XD - PHYRE WORKSPACE (Centrum Operacyjne)

Cel: Spolszczenie tekstur Menu Głównego i UI gry Metal Wolf Chaos XD.
System: Fedora Linux / Heroic Games Launcher.
Metoda: Iniekcja surowych danych BC7 do kontenerów .phyre.
⚠️ ZŁOTA ZASADA BEZPIECZEŃSTWA

    NIGDY nie pracujemy na plikach w 00_CLEAN_BACKUP. To jest "święty graal".

    Do pracy ZAWSZE kopiujemy plik z 00_... do głównego katalogu phyre_work.

    Przed testem w grze ZAWSZE robimy backup pliku w folderze gry (cp file.phyre file.phyre.bak).

🗺️ MAPA KATALOGÓW
Katalog	Opis i Przeznaczenie
00_CLEAN_BACKUP	Tylko do odczytu. Tutaj leżą czyste, oryginalne pliki menu_common_en_US.phyre (GOG). Jeśli coś zepsujesz, stąd bierzesz nową kopię.
01_WORKSPACE_GIMP	Pliki robocze. Tutaj trzymamy projekty .xcf (GIMP), paski .png i tymczasowe pliki .dds przed finalizacją.
02_READY_TO_INJECT	Gotowe wsady. Tutaj lądują sfinalizowane pliki .dds (z paddingiem) oraz mapy JSON, gotowe do wstrzyknięcia skryptem.
03_LOGS	Dokumentacja. Dzienniki misji, raporty błędów, ten plik README.
_ARCHIVE_OLD	Śmietnik historyczny. Stare ekstrakcje, nieudane próby, pliki z poprzednich sesji. Nie usuwać, ale nie używać.
🕵️‍♂️ ROZPOZNANIE CELÓW (ID Tekstur)

To jest kluczowa wiedza zdobyta metodą prób i błędów. Nie pomyl ich!
ID Pliku (wewn.)	Opis Zawartości	Status	Uwagi
MENUTEX_130_01	PRZYCISKI MENU	🎯 GŁÓWNY CEL	Tutaj są napisy "NEW GAME", "LOAD GAME", "OPTIONS". Rozmiar ok. 1024x1024 (do weryfikacji).
MENUTEX_130_02	RAMKI / TŁA	❌ ZROBIONE	To nie są przyciski. Edycja tego powoduje artefakty w Menu Opcji. (Plik 1.3 MB, 1152x1152).
MENUTEX_150_00	Ekrany Opcji	❓ Do zbadania	Prawdopodobnie napisy wewnątrz menu ustawień.
🛠️ PROCEDURA OPERACYJNA (Workflow)
KROK 1: Przygotowanie Stołu
code Bash

# Będąc w phyre_work/
cp 00_CLEAN_BACKUP/menu_common_en_US.phyre .

KROK 2: Namierzanie i Ekstrakcja

Użyj skryptu do wygenerowania mapy JSON i wyciągnięcia tekstury.
code Bash

# Generowanie mapy
python3 ../scripts/11_Phyre_Extract_v2.py menu_common_en_US.phyre
# (LUB użycie dedykowanego ekstraktora dla konkretnej tekstury)

KROK 3: Edycja (GIMP)

    Otwórz wyciągnięty plik (jeśli RAW -> użyj Alignment_Tool).

    Edytuj w GIMP (Zamaluj angielski, napisz polski).

    Eksport: BC7 / Compression / No Mipmaps.

    Zapisz wynik w 02_READY_TO_INJECT/.

KROK 4: Weryfikacja Rozmiaru (Padding)

Plik .dds musi być idealnie dopasowany do dziury w kontenerze.

    Jeśli za mały -> Skrypt iniekcyjny sam doda zera.

    Jeśli za duży -> STOP. Musisz zmniejszyć kompresję lub przyciąć dane.

KROK 5: Iniekcja (Wstrzyknięcie)

Użyj najnowszego, inteligentnego skryptu V3:
code Bash

python3 ../scripts/20_Phyre_Smart_Injector.py \
    menu_common_en_US.phyre \
    02_READY_TO_INJECT/Map_Menu_Common_En.json \
    MENUTEX_130_01 \
    02_READY_TO_INJECT/twoj_plik_przyciskow.dds

KROK 6: Deployment (Wdrożenie)
code Bash

# Kopiowanie do gry (nadpisanie en_US, bo gra w trybie RU i tak z niego czyta)
cp menu_common_en_US.phyre "$HOME/Games/Heroic/Metal Wolf Chaos XD/Media/D3D11/"

🧰 SKRYPTY (Opis Narzędzi)

Znajdują się w katalogu ../scripts/.

    20_Phyre_Smart_Injector.py – GŁÓWNE NARZĘDZIE. Automatycznie oblicza offsety, sprawdza rozmiar i dodaje padding. Używać tego zamiast starszych wersji (12, 19).

    18_Phyre_Alignment_Tool.py – Do naprawy "tęczy" (usuwa/dodaje 12 bajtów paddingu w nagłówku). Przydatne przy ręcznej edycji RAW.

    15_Phyre_Precision_Extract.py – Do wycinania tekstur o niestandardowych wymiarach (np. 1152x1152).

    11_Phyre_Extract_v2.py – Skanuje plik .phyre i tworzy mapę JSON potrzebną dla iniektora.

Ostatnia aktualizacja: 16.02.2026 - Po incydencie z nadpisaniem backupu.

# Log 05: Edycja tekstur UI (GIMP 3.0) - Metoda Brute Force

**Data:** $(date +'%Y-%m-%d')
**Status:** W toku
**Plik:** `menu_clean_stripes.dds`
**Format:** DDS (BC7 / BPTC), 1152x1152 px

## 1. Analiza Geometrii
Tekstura wyciągnięta z PhyreEngine wykazuje specyficzne cechy dla systemów konsolowych:
- **Vertical Flip:** Obraz jest odwrócony lustrzanie w pionie.
- **Swizzling (Strips):** Obraz jest pocięty na poziome pasy o wysokości 128 px ($1152 / 9$ segmentów).
- **BC7 Noise:** Tło nie jest jednolite; zawiera artefakty kompresji BC7, co uniemożliwia proste zamalowywanie pędzlem (wymagane klonowanie tekstury).

## 2. Środowisko pracy (GIMP 3.0 - Fedora 42)
Skonfigurowano narzędzia w celu minimalizacji ryzyka błędu przesunięcia pikseli:
- **Siatka (Grid):** Poziomo 1152 px, Pionowo 128 px (kolor Cyan: `#00fffd`).
- **Podgląd:** Zastosowano `Widok -> Obróć i odbij -> Odbij pionowo` w celu uzyskania czytelności tekstów bez fizycznej ingerencji w orientację warstw (Virtual Mirroring).
- **Struktura warstw:**
    1. `NAPISY_PL` (Tekst, 100% krycia)
    2. `ZAMALOWYWANIE` (Przezroczysta, rekonstrukcja tła narzędziem Klonowanie)
    3. `ORYGINAŁ` (Base layer, zablokowana)

## 3. Strategia Edycji
Zrezygnowano ze skryptowej rekonstrukcji obrazu (Unswizzle) na rzecz edycji "na żywo" na pociętych segmentach. 
- **Wyzwanie:** Linie podziału siatki przechodzą przez środek napisów (np. `OPTIONS`).
- **Rozwiązanie:** Nałożenie polskiego tekstu z 50% przezroczystością, dopasowanie do oryginalnego "rozcięcia" i ewentualne ręczne przesunięcie segmentów tekstu, aby zachować zgodność z logiką składania tekstur przez silnik gry.

## 4. Parametry Eksportu (Planowane)
- **Format:** DDS
- **Kompresja:** BC7 (BPTC)
- **Mipmapy:** Brak (No Mipmaps) - kluczowe dla tekstur UI.
--------------------------
# Log 06: Przełom w edycji - Pierwszy polski napis (NOWA GRA)

**Data:** 2024-02-11
**Status:** Etap testowy (Pre-alpha UI)
**Narzędzie:** GIMP 3.0

## Co zostało zrobione:
1.  **Konfiguracja Próbkowania:** Rozwiązano problem nieaktywnego klonowania przez włączenie opcji "Próbkowanie wszystkich warstw" w narzędziu Klonowanie (C). Dzięki temu szum tła z oryginału jest kopiowany bezpośrednio na przezroczystą warstwę `ZAMALOWYWANIE`.
2.  **Rekonstrukcja Tła:** Skutecznie usunięto napis `NEW GAME` przy użyciu klonowania, zachowując specyficzną ziarnistość tekstury BC7, co zapobiegnie powstawaniu "plam" w menu gry.
3.  **Implementacja Tekstu:**
    - Dodano warstwę tekstową `Nowa Gra` (Czcionka: Cantarell Extra Bold, Rozmiar: 60 px).
    - Zastosowano fizyczne **Odbicie Pionowe (Shift+F)** na warstwie tekstu. Jest to niezbędne, ponieważ plik DDS jest odwrócony, a my pracujemy w trybie lustrzanego podglądu (View Mirroring).
4.  **Weryfikacja Geometrii:** Napis został wycentrowany wewnątrz paska wyznaczonego przez siatkę 128 px, co powinno zapobiec "rozjechaniu się" liter w silniku gry.

## Co zamierzamy zrobić (Następne kroki):
1.  **Eksport Testowy:** Wykonanie eksportu do formatu DDS z kompresją BC7 (BPTC) przy wyłączonych Mipmapach.
2.  **Weryfikacja In-Game:** Uruchomienie Metal Wolf Chaos XD i sprawdzenie, czy napis `NOWA GRA` wyświetla się prosto, czy ma zachowaną przezroczystość (kanał alfa) i czy pozycja jest zgodna z oryginałem.
3.  **Kontynuacja Translacji:** Po potwierdzeniu poprawności eksportu, powtórzenie procedury (Klonowanie + Odwrócony Tekst) dla pozostałych pozycji:
    - `LOAD GAME` -> `WCZYTAJ`
    - `OPTIONS` -> `OPCJE`
    - `CREDITS` -> `TWÓRCY`
    - `EXIT` -> `WYJŚCIE`

## Uwagi techniczne:
Pamiętać o zresetowaniu obrotu widoku (`Widok -> Obróć i odbij -> Zresetuj`) przed finalnym eksportem, aby upewnić się, że wszystko w pliku fizycznie znajduje się "do góry nogami" przed zapisem do DDS.
------------------------
Log 06: Zmiana strategii eksportu i przygotowanie master-pliku PNG

Data: 2024-02-12
Status: Etap przygotowania źródła (Source Ready)
Narzędzia: GIMP 3.0 (Fedora 42), GIMP Python Console (weryfikacja)
1. Problemy techniczne (Post-mortem)

Podczas próby bezpośredniego zapisu do DDS BC7 z poziomu GIMP-a wykryto krytyczny błąd:

    Nieprawidłowy rozmiar pliku: Wynikowy DDS ważył jedynie 59 KB (oczekiwany rozmiar dla 1152x1152 BC7 to ok. 1.3 - 1.7 MB).

    Brak natywnego wsparcia BC7: Wersja GIMP-a/wtyczki nie udostępniała poprawnego profilu kompresji BPTC (BC7) na liście eksportu.

    Ryzyko crashu: Wstrzyknięcie tak małego pliku do kontenera PhyreEngine spowodowałoby błąd silnika.

2. Rozwiązanie: Metoda pośrednia (Intermediate PNG)

Zmieniono strategię na "Metodę Profesjonalną" – GIMP służy jako edytor graficzny, a konwersja do finalnego DDS zostanie wykonana zewnętrznym narzędziem terminalowym.
Wykonane kroki w GIMP 3.0:

    Weryfikacja warstw: Złączono wizualnie warstwy Nowa Gra (odwróconą pionowo), ZAMALOWYWANIE (wyklonowane tło) oraz oryginał.

    Konfiguracja eksportu PNG:

        Nazwa pliku: menu_work.png

        Pixel Format: Ustawiono na 8 bpc RGBA (Kluczowe dla zachowania 8-bitowego kanału Alfa).

        Przeplatanie (Adam7): Wyłączone.

        Parametry dodatkowe: Włączono "Zapisywanie wartości kolorów dla przezroczystych pikseli" (zapobiega artefaktom na krawędziach czcionek).

    Zapis projektu: Zaktualizowano plik roboczy menu_clean_stripes_work.xcf ze wszystkimi warstwami tekstowymi.

3. Plan działań (Następne kroki)

    Konwersja zewnętrzna: Użycie narzędzia terminalowego (np. texconv przez Wine lub nvcompress) do zamiany menu_work.png na menu_clean_stripes.dds z flagami:

        Format: BC7_UNORM

        Mipmaps: None

    Weryfikacja wagi pliku: Plik po konwersji musi mieć rozmiar zbliżony do oryginału (~1.7 MB).

    Test In-Game: Podmiana tekstury w plikach gry i weryfikacja wyświetlania napisu "NOWA GRA".

    Batch Processing: Po sukcesie testu – edycja pozostałych napisów w GIMP-ie i masowa konwersja.
----------------
AKTUALIZACJA STATUSU: Faza Graficzna - Przełom techniczny

    Sukces konwersji: Omijając ograniczenia GIMP-a, wdrożono zewnętrzny workflow konwersji przy użyciu nvcompress (NVIDIA Texture Tools).

    Parametry pliku: Wygenerowano plik menu_clean_stripes.dds w formacie BC7 (BPTC) o rozdzielczości 1152x1152.

    Weryfikacja danych:

        Rozmiar: 1,3 MB (zgodny co do bajta z modelem matematycznym BC7 dla tej rozdzielczości).

        Mipmapy: Wyłączone zgodnie ze specyfikacją UI PhyreEngine.

        Geometria: Napis "NOWA GRA" został poprawnie wkomponowany w "poswizzlowany" układ pasów (strips) na warstwie źródłowej.

    Gotowość: Plik jest gotowy do wstrzyknięcia do kontenera .phyre i testów bezpośrednio w silniku gry.

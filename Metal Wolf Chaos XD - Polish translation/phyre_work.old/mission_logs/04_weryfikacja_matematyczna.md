# 📝 Raport Operacyjny: ZŁAMANY SZYFR ROZDZIELCZOŚCI
**Data:** 21.01.2026 (Wieczór)
**Status:** PRZEŁOM KRYTYCZNY
**Cel:** Eliminacja "cyfrowego szumu" w wyeksportowanych teksturach BC7.

## 🕵️‍♂️ Analiza Śledcza
Poprzednie próby (zakładające standardowe rozdzielczości 1024/2048) kończyły się wyświetlaniem przesuniętego obrazu (skośne pasy/szum).
Użyto skryptu `13b_Deep_Header_Inspector` do analizy bajtów nagłówka silnika Phyre.

### Znalezisko (Hex Dump):
Na offsecie `+016` od nazwy pliku znaleziono wartości:
`00 80 04 00` (Little Endian) -> **`0x0480`** -> **1152 dec**.

### 🧮 Weryfikacja Matematyczna
Dla pliku `MENUTEX_130_02` (rozmiar danych ~1.76 MB):
- Hipoteza 2048x2048: Wymaga 4.19 MB (Brak danych -> Szum).
- Hipoteza **1152x1152**:
  - Format BC7 (1 bajt/px): 1152 * 1152 = 1,327,104 bajtów.
  - Z Mipmapami (+33%): ~1,769,472 bajtów.
  - **WYNIK:** Idealne dopasowanie do wielkości wyciętego bloku!

## 🛠️ Podjęte Działania
Stworzono skrypt `15_Phyre_Precision_Extract.py`, który:
1. Ignoruje zgadywanie.
2. Wymusza precyzyjne wymiary dla kluczowych plików:
   - `MENUTEX_130_01` -> **576 x 576**
   - `MENUTEX_130_02` -> **1152 x 1152** (Główne Menu)
3. Generuje poprawny nagłówek DDS DX10 (BC7).

## 🚀 Oczekiwania
Otwarcie pliku `final_01_MENUTEX_130_02_1152x1152.dds` w GIMP powinno skutkować **idealnym obrazem** bez przesunięć.

Gotowy do weryfikacji wizualnej.

-------------

# 📝 Raport Operacyjny: WERYFIKACJA MATEMATYCZNA & SWIZZLING
**Data:** 21.01.2026
**Status:** CZĘŚCIOWY SUKCES (Treść widoczna / Artefakty graficzne)
**Cel:** Weryfikacja niestandardowej rozdzielczości 1152x1152.

## 🔬 Wynik Eksperymentu
Użyto skryptu `15_Phyre_Precision_Extract` wymuszającego rozdzielczość **1152x1152** i nagłówek **BC7**.

**Obserwacje (Screenshoty):**
1. **POZYTYWNE:** W pliku `final_01` wyraźnie widać napisy: "NEW GAME", "LOAD GAME", "OPTIONS", "CREDITS". Napisy są ułożone poziomo, co **potwierdza poprawność szerokości 1152px**.
2. **NEGATYWNE:** Kolory są zniekształcone (efekt tęczy/RGB split), a bloki graficzne są przemieszane (pocięte w paski).

## 🕵️‍♂️ Diagnoza: SWIZZLING
Obraz nie jest uszkodzony, jest **"poswizzlowany"** (zapisany w układzie kafelkowym/blokowym zamiast liniowym). Jest to typowa optymalizacja dla GPU w silniku PhyreEngine.
GIMP interpretuje dane liniowo, stąd efekt wizualnego "szumu" mimo poprawnego dekodowania kształtów.

## 🚀 Plan Naprawczy (Następna Sesja)
Musimy zaimplementować algorytm **"De-swizzle"** (Linearize):
1. Zidentyfikować wzór kafelkowania (prawdopodobnie standardowy Morton Order / Z-Curve lub Tile Linear).
2. Napisać skrypt, który przestawi bajty w kolejności czytelnej dla człowieka przed otwarciem w GIMP.
3. Po edycji: wykonać operację odwrotną (Re-swizzle) przed wstrzyknięciem do gry.

**Wniosek:** Jesteśmy w posiadaniu surowych danych tekstury. Przeszkodą pozostała jedynie permutacja bloków danych.

----------------

Data: 1 Lutego 2026
Cel: Spolszczenie głównych tekstur UI (Menu Główne).
1. STATUS BIEŻĄCY

    Dialogi/Napisy: 100% Spolszczone (Metoda: Injection + Font Remapping).

    Tekstury UI: W trakcie prac nad plikiem menu_common_en_US.phyre.

2. DANE TECHNICZNE (Hard Data)

    Format pliku: BC7 (Block Compression 7, DirectX 11).

    Rozdzielczość: 1152x1152 pikseli.

    Struktura pliku (Extracted): Plik .dds wyciągnięty z kontenera Phyre.

    Nagłówek: DX10 Header (148 bajtów).

    Blok danych: 16 bajtów (4x4 piksele).

3. DIAGNOZA "SWIZZLINGU" (Układu pamięci)

    Objaw: Obraz w GIMP jest czytelny, ale "pocięty" w paski i ma przekłamane kolory ("tęcza").

    Próba 1 (Tile Linear): Skrypt 16_Phyre_Swizzler.py.

        Wynik: Widoczne napisy "NEW GAME", "OPTIONS", ale obraz pocięty i zaszumiony kolorystycznie.

        Wniosek: Jesteśmy blisko struktury, ale mamy przesunięcie danych (Alignment).

    Próba 2 (Morton/Z-Curve): Skrypt 17_Phyre_Morton.py.

        Wynik: Totalny szum (kasza).

        Wniosek: Silnik NIE używa standardowego Mortona. Ślepa uliczka.

4. GLÓWNY PROBLEM (Alignment/Przesunięcie)

    Przyczyna "Tęczy": Nagłówek ma 148 bajtów. Blok BC7 ma 16 bajtów.

        148 / 16 = 9.25 (reszta 4 bajty).

        Komputer czyta dane od połowy bloku. To powoduje, że kolory są błędne.

    Wymagane działanie: Musimy przesunąć start odczytu o 12 bajtów (padding), aby trafić w początek bloku (148 + 12 = 160, co dzieli się przez 16).
--------------------
aport Operacyjny: ODZYSKANIE KOLORÓW (ALIGNMENT FIX)

Data: 1 Lutego 2026 (Koniec sesji)
Status: PRZEŁOM TECHNICZNY (Kolory naprawione / Tekst czytelny)
Cel: Eliminacja błędów renderowania tekstur UI (efekt "Tęczy/Szumu").
🛑 Problem

Poprzednie próby "odkręcania" (Deswizzling) tekstury MENUTEX_130_02 (1152x1152) kończyły się generowaniem obrazu o zniekształconych kolorach i strukturze (cyfrowa kasza), mimo teoretycznie poprawnych algorytmów.
🕵️‍♂️ Analiza Śledcza (Przyczyna Źródłowa)

Zidentyfikowano błąd WYRÓWNANIA DANYCH (Data Alignment).

    Struktura BC7: Dane są zapisywane w blokach po 16 bajtów.

    Nagłówek DX10: Ma rozmiar 148 bajtów.

    Matematyka Błędu: 148 / 16 = 9, reszta 4.

        Silnik/Skrypt czytał dane zaczynając od 4. bajtu bloku, co powodowało przesunięcie bitowe i całkowite zniszczenie kolorów.

    Wymagany Padding: Aby wyrównać start danych do wielokrotności 16, silnik gry dodaje 12 bajtów zer po nagłówku (148 + 12 = 160, co dzieli się przez 16).

🛠️ Podjęte Działania

Stworzono narzędzie diagnostyczne 18_Phyre_Alignment_Tool.py.

    Tryb CLEAN: Wyciął nagłówek, usunął 12 bajtów paddingu (z przesunięcia 148-160) i dokleił nagłówek z powrotem.

🔬 Wynik Wizualny (Dowód)

Plik menu_clean_stripes.dds otwarty w GIMP:

    KOLORY: Idealne (Czysta czerwień, biel, szarość). Brak szumu RGB.

    TREŚĆ: Wyraźnie czytelne napisy "NEW GAME", "LOAD GAME", "OPTIONS".

    STRUKTURA: Obraz nadal jest "poszatkowany" (Tile Linear) i odwrócony lustrzanie (Mirror), co jest naturalnym stanem surowej tekstury w pamięci konsoli.

🚀 Plan na następną sesję

Mamy już napisany skrypt 18_Phyre_Final_Tile.py, który łączy naprawę alignmentu z algorytmem deswizzlingu.

    Unswizzle: Użyć 18_Phyre_Final_Tile.py (łączy usunięcie paddingu + poukładanie kafelków).

    GIMP: Odbić obraz lustrzanie (Flip Horizontal).

    Edycja: Podmienić tekst na POLSKI.

    Reswizzle: Odwrócić proces (Flip -> Reswizzle -> Dodanie paddingu dla silnika).
------------
----------------

# 📝 Raport Operacyjny: FIASKO AUTOMATYKI I ZMIANA TAKTYKI
**Data:** 10.02.2026
**Status:** TAKTYCZNY ODWROT DO METODY "BRUTE FORCE"
**Cel:** Finalizacja strategii edycji tekstury menu głównego.

## 💥 Analiza Porażki (Incident Report)
Podjęto próbę użycia skryptu `18_Phyre_Final_Tile.py`, który miał jednocześnie naprawić kolory (Alignment) i poskładać pocięty obraz (Unswizzle).
- **Wynik:** Obraz wyjściowy (`menu_combo_fix.dds`) był całkowicie nieczytelny ("cyfrowa kasza").
- **Przyczyna:** Algorytm zakładał standardowe kafelkowanie GPU 64x64 piksele. Rzeczywisty układ pamięci w tym pliku jest inny (prawdopodobnie proste paski poziome lub niestandardowe makrobloki), przez co skrypt pomieszał poprawne dane.

## ✅ Potwierdzony Sukces (Alignment)
Narzędzie `18_Phyre_Alignment_Tool.py` (tryb `clean`) zadziałało poprawnie.
- Usunięcie **12 bajtów paddingu** (wyrównanie nagłówka 148 -> 160 bajtów) całkowicie naprawiło błędy kolorów (zniknęła "tęcza").
- **Stan obecny:** Mamy plik `menu_clean_stripes.dds`, który jest:
  1. **Kolorystycznie poprawny** (RGB OK).
  2. **Czytelny** (widać tekst).
  3. **Pocięty w pasy** (Strips).
  4. **Odwrócony lustrzanie** (Mirrored).

## 🗺️ Plan Działania: Metoda "Na Paski" (Strip Surgery)
Rezygnujemy z prób zgadywania algorytmu "De-swizzle". Przechodzimy do ręcznej edycji na poziomie surowych pasków.

1. **Przygotowanie:**
   - `Alignment_Tool.py clean` -> Uzyskanie pliku z poprawnymi kolorami.
2. **Edycja (GIMP):**
   - Odbicie lustrzane poziome (dla czytelności).
   - Zamalowanie angielskich napisów bezpośrednio na paskach.
   - Nałożenie polskiego tekstu ("NOWA GRA", "OPCJE") z uwzględnieniem cięć (jeśli litera wypada na łączeniu pasków – dopasowanie ręczne).
   - Ponowne odbicie lustrzane (przywrócenie stanu surowego).
3. **Wstrzyknięcie:**
   - `Alignment_Tool.py restore` -> Przywrócenie 12 bajtów paddingu.
   - Wgranie do kontenera `.phyre`.

**Konkluzja:** Mamy pełną kontrolę nad pikselami. Algorytm układania nie jest nam już potrzebny do sukcesu.

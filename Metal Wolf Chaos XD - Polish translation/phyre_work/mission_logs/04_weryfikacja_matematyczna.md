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

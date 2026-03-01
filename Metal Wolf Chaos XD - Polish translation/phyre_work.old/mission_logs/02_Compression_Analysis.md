# 📝 Raport Operacyjny: LZ4 CONFIRMED
**Data:** 20.01.2026
**Cel:** Potwierdzenie kompresji i próba dekompresji
**Plik cel:** `menu_common_en_US.phyre` -> `MENUTEX_130_02`

## 🔍 Wnioski z fazy "Frankenstein"
Otwarcie plików z "surowymi" danymi i sztucznym nagłówkiem DXT5 ukazało charakterystyczny "kolorowy szum".
**Diagnoza:** Dane są skompresowane algorytmem bezstratnym (najprawdopodobniej LZ4, standard dla PhyreEngine).

## 🛠️ Plan Działania (Skrypt 12)
Zamiast zgadywać nagłówki, używamy metody "Brute Force Decompression":
1. Szukamy nazwy pliku w kontenerze.
2. Skanujemy obszar po nazwie pliku bajt po bajcie.
3. Każdy punkt traktujemy jako potencjalny początek strumienia LZ4.
4. Próbujemy wykonać `lz4.block.decompress` z oczekiwanym rozmiarem wyjściowym **4,194,304 bajtów** (dla tekstury 2048x2048 DXT5).

## 📊 Oczekiwane Wyniki
- **Sukces:** Skrypt wypluje plik `DECOMPRESSED_MENU.dds`, który w GIMP pokaże czytelne przyciski.
- **Porażka:** Skrypt nie znajdzie prawidłowego strumienia (błąd LZ4 Error). Może to oznaczać inny algorytm (Zlib?) lub inny rozmiar docelowy.

## 🚀 Status
Uruchamianie skryptu `12_Phyre_LZ4_Test.py`...

## 🛑 Próba LZ4 nieudana
**Status:** Fail
**Analiza:** Skrypt Brute Force nie znalazł prawidłowego bloku LZ4 w pobliżu nazwy pliku.
**Nowa Hipoteza:** Możliwe użycie Zlib (standard Deflate) lub niestandardowy offset danych.
**Akcja:** Uruchomienie `13_Phyre_Hex_Inspector.py` w celu wizualnej inspekcji nagłówka danych. Szukamy sygnatury `78 9C` (Best Compression) lub `78 DA` (Default Compression).

## 🛑 PRZEŁOM: Identyfikacja Formatu (Hex Inspector)
**Status:** SUKCES DIAGNOSTYCZNY
**Wynik:** Skrypt `13_Phyre_Hex_Inspector` ujawnił w nagłówku silnika ciąg znaków ASCII: **`BC7`**.
**Wnioski:**
1. Tekstury NIE są skompresowane algorytmem LZ4/Zlib (brak sygnatur `78 9C` itp.).
2. Tekstury są zapisane w formacie **DirectX 11 BC7 (BPTC)**.
3. Poprzednie próby otwarcia (jako DXT5) skutkowały "szumem", ponieważ GIMP błędnie interpretował bloki danych.

**Plan na następną sesję:**
- Modyfikacja skryptu ekstrakcji (`11d`), aby generował **nagłówek DDS z rozszerzeniem DX10 (FourCC: 'DX10', DXGI Format: BC7_UNORM)**.
- Otwarcie plików w GIMP jako BC7. To powinno dać krystalicznie czysty obraz bez żadnej dekompresji.

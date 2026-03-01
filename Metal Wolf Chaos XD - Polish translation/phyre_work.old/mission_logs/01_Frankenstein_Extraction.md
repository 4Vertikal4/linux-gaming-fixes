# 📝 Raport Operacyjny: FRANKENSTEIN BREAKTHROUGH
**Data:** 20.01.2026, 06:35
**Cel:** Ekstrakcja tekstur UI bez nagłówków DDS (Raw Data)
**Plik cel:** `menu_common_en_US.phyre`
**Metoda:** Skrypt `11c_Phyre_Raw_Extract.py` (Heurystyka nazw plików + sztuczne nagłówki)

## 🔍 Przebieg Sesji
1. **Analiza:** 
   - Standardowy skan (`11_Extract`) zawiódł (0 wyników).
   - `Deep Scan` wykrył nazwy plików (`MENUTEX...`) i sygnatury `PTex`, ale brak nagłówków `DDS `.
   - Struktura pliku: [Nazwa Pliku] -> [Metadane/Padding] -> [Surowe Pixele].
2. **Działanie:**
   - Zastosowano metodę "Frankenstein": cięcie pliku w miejscach występowania nazw tekstur.
   - Skrypt automatycznie oszacował rozdzielczość na podstawie rozmiaru bloku danych.
   - Doklejono sztuczne nagłówki DXT5, aby pliki były czytelne dla GIMP-a.

## 🛠️ Wyniki Techniczne (Extracted Raw)
Znaleziono 6 głównych bloków tekstur.

| ID | Nazwa pliku (w silniku) | Estymacja Rozdz. | Rozmiar (Bajty) | Zawartość (Przypuszczalna) |
|----|-------------------------|------------------|-----------------|----------------------------|
| 00 | `MENUTEX_130_01.dds`    | 1024x1024        | ~443 KB         | Małe elementy UI? |
| 01 | `MENUTEX_130_02.dds`    | 2048x2048        | ~1.76 MB        | **Główny cel?** (Przyciski Menu) |
| 02 | `story_tex01.dds`       | 4096x4096        | ~14.1 MB        | Tło fabularne / Atlas |
| 03 | `MENUTEX_900_02.dds`    | 2048x2048        | ~3.5 MB         | Elementy HUD? |
| 04 | `MENUTEX_150_00.dds`    | 2048x2048        | ~1.76 MB        | Ekrany Opcji? |
| 05 | `MENUTEX_510_50.dds`    | 2048x2048        | ~3.5 MB         | Inne elementy interfejsu |

*Uwaga: Rozmiary bajtowe obejmują potencjalny padding i metadane wciągnięte do obrazu.*

## ⚠️ Problemy i Obserwacje
- Pliki otwierają się w GIMP, ale mogą zawierać "cyfrowe śmieci" na górnej krawędzi (pozostałości nagłówka silnika). Jest to efekt zamierzony przy tej metodzie ekstrakcji.
- Należy zachować ostrożność przy edycji, aby nie naruszyć struktury danych, jeśli śmieci nachodzą na grafikę (mało prawdopodobne, zazwyczaj to tylko kilka pierwszych linii).

## 🚀 Plan na następną sesję
1. **Weryfikacja Wizualna:** Przegląd plików w GIMP w celu znalezienia przycisków "NEW GAME", "OPTIONS", "EXIT".
2. **Edycja Graficzna:** Podmiana tekstów na polskie w wybranym pliku.
3. **Iniekcja:** Dostosowanie skryptu `12_Inject` do obsługi trybu RAW (odcinanie nagłówka DDS przed zapisem).

## 🔄 Aktualizacja: Metoda Safe Padding (11d)
**Status:** Wykonano
**Wynik:** Skrypt 11d dodał brakujące bajty (zera) do plików, aby zgadzały się ze standardem DXT5.
- `MENUTEX_130_02` (Menu Główne?): Dopełniono +2.4 MB zerami.
- `story_tex01`: Dopełniono +2.6 MB zerami.
**Cel:** Umożliwienie otwarcia plików w GIMP bez crasha wtyczki `file-dds`.
**Następny krok:** Weryfikacja wizualna – czy to surowe piksele (Sukces) czy skompresowane dane (Szum).

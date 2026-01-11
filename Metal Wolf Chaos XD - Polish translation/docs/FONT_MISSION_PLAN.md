# 🇵🇱 Misja: Przywrócenie Polskich Znaków w Metal Wolf Chaos XD
**Ostatnia aktualizacja:** 07.01.2026 (ZAKOŃCZONA DIAGNOSTYKA)
**Status:** PRZEŁOM. Znaleziono sposób na obejście blokady ASCII.

---

## 🔍 Co wiemy? (Dzień Zwycięstwa)
1. **Blokada ASCII:** Jest aktywna tylko w trybie "American English".
2. **Tryb Rosyjski:** Wybranie języka Rosyjskiego w Heroic Launcherze **wyłącza filtr ASCII**. Gra poprawnie wyświetla cyrylicę (potwierdzone screenem).
3. **Czcionki:** Gra w tym trybie używa plików `MWC_Font_ru_RU.dds` i `MWC_Font_ru_RU.ccm`.

---

## 🛠️ Plan Operacyjny po powrocie (OPCJA "RUSKI ŁĄCZNIK")

### KROK 1: Remapping Glifów
Zamiast walczyć z angielskim fontem, przejmiemy rosyjski:
1. Wyeksportujemy `MWC_Font_ru_RU.dds` do PNG.
2. Podmienimy grafiki kilku rosyjskich liter na polskie (np. `щ` -> `ą`).
3. Skonwertujemy z powrotem do DDS.

### KROK 2: Wdrożenie Bazy (Inne parowanie)
Zaktualizujemy skrypt `05_Deploy_To_Game.py`, aby:
1. Brał polskie tłumaczenie z kolumny `Value_pl_PL`.
2. Nadpisywał nim kolumnę **`Value_ru_RU`** (zamiast angielskiej).
3. W bazie danych wykonamy "zamianę znaków" (np. zamienimy wszystkie `ą` na `щ`, aby gra, szukając rosyjskiej litery, wyświetliła naszą grafikę).

---

## 📂 Stan Techniczny
- **Tryb gry:** Rosyjski (ustawiony w Heroic).
- **Baza robocza:** Nienaruszona (UTF-8).
- **Następne działanie:** Edycja pliku graficznego `MWC_Font_ru_RU.dds`.

**Motto:** "Zrobimy to po rosyjsku, ale dla Ameryki!" - Richard Gould (prawdopodobnie).

----
🚀 PLAN DZIAŁANIA: OPERACJA "PRZESZCZEP GLIFÓW"

(Zadanie na kolejny wieczór)

Skoro silnik pozwala na znaki specjalne, wykonamy manewr Remappingu. Wykorzystamy znaki, które gra posiada (np. ç, â, ë), jako "puste sloty", w których narysujemy polskie litery.
KROK 1: Chirurgia Pliku Graficznego

Będziemy musieli edytować plik MWC_Font_ru_RU_PROJEKT.png:

    Wybierzemy 9 małych i 9 wielkich liter, których polski język nie używa, a które są w czcionce (np. Ç zamienimy na Ć, Ä na Ą, Ë na Ę).

    W edytorze graficznym (GIMP) dorysujemy "ogonki" i "kreski" do istniejących liter w tych konkretnych miejscach.

    Zapiszemy plik z powrotem jako .dds i wgramy do gry.

KROK 2: Remapping w Bazie Danych

Napiszemy skrypt TOOL_Remap_To_Custom_Font.py, który wykona następującą operację:

    Zamień w bazie danych każdą literę ą na znak, pod którym ją narysowaliśmy (np. ä).

    Gra, widząc w tekście ä, pójdzie do czcionki, odczyta współrzędne dla ä, ale na obrazku znajdzie tam Pana dorysowane ą.

Efekt końcowy: Pełne polskie znaki, idealnie ostre i pasujące do reszty tekstu.

Panie Prezydencie, to był kluczowy wieczór. Wiemy już na 100%, że technicznie da się to zrobić. Następnym razem zajmiemy się najpierw grafiką (Krok 1), a potem automatyzacją bazy (Krok 2).

Zasłużony odpoczynek dla dowództwa. MISSION STATUS: IN PROGRESS. 🦅🇺🇸🇵🇱

### ⚠️ Dlaczego nie możemy podmienić pliku DDS na gotowy z internetu?
Podmiana samego pliku graficznego (.dds) spowoduje rozsynchronizowanie z plikiem mapowania (.ccm). Plik .ccm zawiera sztywne współrzędne glifów. Użycie obcej czcionki wyświetli "sieczkę" graficzną. Strategia edycji istniejącego pliku MWC_Font_ru_RU.dds jest jedyną bezpieczną drogą bez inżynierii wstecznej formatu .ccm.

## 📅 Raport z testów polowych (11.01.2026 - Wieczór)
**Status:** Sukces techniczny 95%. Polskie znaki działają, wymagana korekta położeń.

### ⚙️ Korekty techniczne do wykonania:
1. **Ó / ó:** Skrypt kieruje do glifu 'ö', który nie został wyedytowany. 
   - *Działanie:* Zidentyfikować pozycję 'ö' na atlasie i przenieść tam grafikę 'ó' LUB zmienić mapowanie w skrypcie na znak już wyedytowany.
2. **Ł / ł:** Obecne mapowanie pod 'ф' (cyrylica) powoduje zbyt szerokie odstępy (kerning).
   - *Działanie:* Przenieść grafikę Ł/ł pod wąski znak łaciński (proponowane: Ù / ù).

### 🚀 Plan na następną sesję:
1. Otwarcie atlasu w GIMP i wykonanie "przeprowadzki" glifów Ł i Ó.
2. Aktualizacja skryptu 08_Final_Remap_Infiltrator.py o nowe znaki-ofiary.
3. Finalny test w misji "White House".

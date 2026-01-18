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

-------------------

## 📅 Raport z testów (13.01.2026)
**Status:** Ó i Ż naprawione. Problem kerningu przy Ł nadal występuje.

### ⚙️ Ostatnia korekta techniczna:
- **Problem:** Slot 'ú' jest zbyt szeroki dla litery 'ł', co powoduje sztuczne przerwy w tekście (np. "pok ł ad").
- **Rozwiązanie:** Przeniesienie glifów Ł/ł pod sloty Í/í (I-acute). Są to najwęższe sloty w atlasie, co powinno wyeliminować niepożądane odstępy.

### 🚀 Następne kroki:
1. Przeniesienie grafiki w GIMP (Ł -> Í, ł -> í).
2. Aktualizacja mapowania w skrypcie 08.
3. Masowe wstrzyknięcie tekstów do brakujących tabel (weapon, item itp.) poprzez stworzenie brakujących kolumn RU.
--------------------
📝 RAPORT OPERACYJNY: "ZŁOTY GLIF" (15.01.2026)

Status projektu: Faza wizualna zakończona sukcesem (100% polskich znaków aktywnych i czytelnych).

Kluczowe osiągnięcia:

    Likwidacja błędu kerningu: Litera Ł/ł została przeniesiona ze zbyt szerokich slotów rosyjskich pod wąskie sloty łacińskie (Í/í). Efektem jest całkowite wyeliminowanie nienaturalnych przerw w tekście (np. w słowie „pokład”).

    Naprawa Ó/ó: Poprawnie zsynchronizowano mapowanie skryptu z atlasem czcionek (slot Ö/ö). Wszystkie polskie litery diakrytyczne wyświetlają się zgodnie z polską ortografią.

    Weryfikacja "Rosyjskiego Łącznika": Potwierdzono, że tryb języka rosyjskiego w połączeniu z naszym zmodyfikowanym atlasem jest stabilny i oferuje najwyższą jakość lokalizacji.

Stan techniczny:

    Font: MWC_Font_ru_RU.dds – Wersja V3 (Slim L).

    Baza: texts_may30.db – Przebudowana, zawiera remapping pod 18 unikalnych glifów.

    Skrypt: 08_Final_Remap_Infiltrator.py – Wersja v3 (Final).

---------------------------------

## 📅 Raport: Pełna Inwentaryzacja Tabel (17.01.2026)
**Status:** Zidentyfikowano 9 kluczowych tabel wymagających remappingu.

### 🔍 Analiza struktury:
Baza gry posiada niespójną strukturę kolumn rosyjskich (niektóre tabele jak 'game' ich nie mają).
Lista zidentyfikowanych tabel: accessory, creature, game, item, magic, maps, menu, stage, weapon.

### 🚀 Nowy Plan:
1. Uruchomienie uniwersalnego skryptu 09 (v2) w celu wyrównania struktur wszystkich 9 tabel.
2. Uruchomienie uniwersalnego skryptu 08 (v4) w celu masowego wstrzyknięcia zremapowanych tekstów.
3. Weryfikacja wizualna Menu (tabela 'game') oraz nazw broni (tabela 'weapon').
--------------------------
Data: 18.01.2026
Status: Wywiad odnalazł lokalizację zasobów interfejsu (UI).
🔍 Kluczowe znalezisko:

Zidentyfikowano folder Media/D3D11/, zawierający binaria silnika PhyreEngine. Kluczowe dla lokalizacji są pliki:

    menu_common_ru_RU.phyre (Prawdopodobnie główne przyciski menu)

    menu_MWC_Brief_ru_RU.phyre (Odprawy przed misją)

    menu_MWC_MainGame_ru_RU.phyre (Interfejs w trakcie gry / HUD)

    gauge_ru_RU.phyre (Elementy liczników i wskaźników)

💡 Wnioski:

Silnik gry nie pobiera wszystkich tekstów z bazy SQLite. Główne elementy wizualne interfejsu są pobierane z dedykowanych kontenerów .phyre. To dlatego baza danych była „pusta” w zakresie przycisku „WYJŚCIE” – ten napis fizycznie siedzi wewnątrz skompilowanego pliku binarnego.
🚀 PROPONOWANY PLAN DZIAŁANIA (Następna sesja)

Będziemy musieli przeprowadzić „inżynierię wsteczną” lub sprytny sabotaż tych plików.
KROK 1: Test "Podmiany Tożsamości" (Łatwy)

Zanim zaczniemy je wypakowywać, sprawdzimy, czy możemy „wymusić” język angielski dla samych przycisków, zostawiając polskie dialogi.

    Backup plików _ru_RU.phyre.

    Skopiowanie menu_common_en_US.phyre i zmiana nazwy na menu_common_ru_RU.phyre.

    Cel: Jeśli to zadziała, przyciski menu staną się angielskie (zrozumiałe), a dialogi zostaną polskie.

KROK 2: Test "String Search" (Średni)

Użyjemy narzędzi linuxowych (strings), aby zobaczyć, czy wewnątrz plików .phyre teksty są zapisane jako zwykły tekst, czy są teksturami (obrazkami).
code Bash

strings menu_common_ru_RU.phyre | grep -i "EXIT"

KROK 3: Ekstrakcja PhyreEngine (Zaawansowany)

Jeśli Krok 1 i 2 nie dadzą pełnej satysfakcji, będziemy musieli użyć narzędzi do wypakowywania plików .phyre (np. PhyreUnpacker), aby wyciągnąć z nich tekstury .dds, edytować je w GIMP-ie (podobnie jak czcionkę) i zapakować z powrotem.

---------------------
Data: 18.01.2026 – Raport Nocny
Status: Cele zidentyfikowane (Zasoby UI).
📡 Dane wywiadowcze (strings):

Wewnątrz menu_common_en_US.phyre zlokalizowano ścieżki do tekstur przycisków:

    Textures/menu/MENUTEX_130_01.dds – Prawdopodobnie główny arkusz przycisków.

    Textures/menu/MENUTEX_130_02.dds – Elementy dodatkowe interfejsu.

    Textures/menu/MENUTEX_150_00.dds – Ekrany opcji.

💡 Wnioski:

Wiemy, jak nazywają się „ofiary” do podmiany graficznej. Nie musimy błądzić po całym pliku – naszym celem jest wyciągnięcie i edycja tych konkretnych arkuszy .dds.
🚀 Plan na sesję "REKONSTRUKCJA":

    Zastosowanie narzędzia QuickBMS ze skryptem phyre.bms lub dedykowanego PhyreUnpacker, aby wypakować powyższe tekstury z kontenera.

    Manualna polonizacja napisów w GIMP-ie (zachowanie stylu metalic/glow).

    Re-import (repack) zmodyfikowanych tekstur do pliku .phyre.

-------------------
📝 AKTUALIZACJA DZIENNIKA (FONT_MISSION_PLAN.md)

Data: 18.01.2026 – Raport z frontu binarnego
Status: Cele namierzone, wymagana zmiana narzędzi ekstrakcji.
🔍 Analiza techniczna (Co wiemy?):

    Struktura kontenera: Pliki .phyre w wersji XD Remaster zaczynają się od nagłówka RYHPT (odwrócone PHYR + T) i zawierają unikalny znacznik 11XD (DirectX 11 XD).

    Błąd offsetu: Próba skoku pod adres 0x8D7 (pobrany z nagłówka) nie napotkała sygnatury PHYR. Zamiast tego znaleziono ciąg r.m_ (72 00 6d 5f), co sugeruje, że wskaźniki w nagłówku prowadzą do tablicy nazw plików, a nie do samych danych.

    Weryfikacja strings: Narzędzie strings potwierdziło, że wewnątrz są pliki .dds (np. MENUTEX_130_01.dds), ale są one „pogrzebane” głębiej niż standardowy skrypt BMS przewiduje.

🚀 Plan na następną sesję (Operacja „Brute Force”):

Ponieważ struktura nagłówka General Arcade jest nietypowa, przejdziemy do metod niezależnych od formatu kontenera:

    Metoda Binwalk: Użycie narzędzia binwalk (natywne na Fedorze), aby przeszukać plik bajt po bajcie i „wyciąć” wszystkie nagłówki DDS.

        Zaleta: Nie potrzebuje skryptu BMS, wyciągnie wszystko, co jest obrazkiem.

    Metoda Raw Scan: Zmodyfikujemy skrypt BMS, aby skanował cały plik w poszukiwaniu ciągu PHYR zamiast polegać na błędnych wskaźnikach z nagłówka.

    GIMP Runda 2: Edycja graficzna przycisków po udanej ekstrakcji.

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

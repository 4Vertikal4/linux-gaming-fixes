# 🇵🇱 Misja: Przywrócenie Polskich Znaków w Metal Wolf Chaos XD
**Data aktualizacji:** 07.01.2026
**Status projektu:** Tłumaczenie bazy danych 100% (READY).
**Główny problem:** Gra wyświetla "?" zamiast polskich znaków (ą, ć, ę...).

---

## 🔍 Co już wiemy?
1. **Baza danych:** Tłumaczenie w SQLite jest poprawne (UTF-8).
2. **Silnik gry:** Korzysta z czcionek bitmapowych (DDS + CCM) w folderze \`rom/font/\`.
3. **Próba EU/RU:** Podmiana plików \`MWC_Font_EU.dds\` i \`MWC_Font_ru_RU.dds\` nie przyniosła efektu. Gra w trybie angielskim ignoruje te pliki.
4. **Wniosek:** Gra wczytuje wyłącznie GŁÓWNY plik: \`MWC_Font.dds\` i \`MWC_Font.ccm\`.

---

## 🛠️ Plan Działania (Kolejne Kroki)

### KROK 1: Test "Rosyjski Granat" (Diagnostyka)
Musimy sprawdzić, czy gra w ogóle potrafi wyświetlić inne znaki niż ASCII w trybie angielskim.
1. Zrób backup: \`MWC_Font.dds.bak\` i \`MWC_Font.ccm.bak\`.
2. Podmień główne pliki na rosyjskie:
   - \`cp MWC_Font_ru_RU.dds MWC_Font.dds\`
   - \`cp MWC_Font_ru_RU.ccm MWC_Font.ccm\`
3. Odpal grę.
   - **Jeśli widzisz cyrylicę:** Silnik jest otwarty na modyfikacje. Przejdź do KROKU 2.
   - **Jeśli nadal widzisz "?"**: Silnik ma "twardy" limit znaków ASCII w kodzie. Przejdź do KROKU 3.

### KROK 2: Strategia "Podmiana Glifów" (Hardcore Modding)
Jeśli test rosyjski zadziałał:
1. Należy edytować plik \`MWC_Font.dds\` (ten duży, japoński).
2. Wyeksportować go do PNG za pomocą \`magick\`.
3. W miejscu rzadko używanych znaków (np. japońskich symboli lub greckich liter) dorysować polskie litery \`ą, ć, ę\` zachowując ten sam styl (biały obrys).
4. Przekonwertować PNG z powrotem do DDS i wgrać do gry.
5. Napisać skrypt "Remapper", który zamieni w bazie danych polskie litery na kody tych podmienionych znaków.

### KROK 3: Strategia "Biała Flaga" (Fallback)
Jeśli modyfikacja fontów okaże się niemożliwa (silnik odrzuca wszystko poza ASCII):
1. Uruchom skrypt \`07_TOOL_Fix_ASCII.py\` na bazie danych.
2. Skrypt zamieni: \`ą -> a\`, \`ć -> c\`, \`ę -> e\` itd.
3. Wgraj bazę ponownie przez \`05_Deploy_To_Game.py\`.
4. Tekst będzie w 100% czytelny, choć bez polskich ogonków.

---

## 📂 Lokalizacja Plików
- **Baza danych:** \`work/texts_may30_PL.db\`
- **Skrypty:** \`scripts/\`
- **Fonty w grze:** \`Games/Heroic/Metal Wolf Chaos XD/rom/font/\`

**Motto:** "Because I'm the President of the United States of America!" - Michael Wilson (i my też się nie poddamy).
------------------------------
# 🇵🇱 Misja: Przywrócenie Polskich Znaków w Metal Wolf Chaos XD
**Ostatnia aktualizacja:** 07.01.2026 (Po nieudanym teście "Rosyjskiego Granatu")
**Status:** Diagnostyka zakończona. Blokada techniczna silnika.

---

## 🔍 Wnioski z Diagnostyki (CO WIEMY?)
1. **Baza danych:** Tłumaczenie SQLite jest w 100% gotowe (UTF-8).
2. **Silnik (General Arcade):** Posiada "twardy" filtr ASCII dla wersji angielskiej.
3. **Wynik Testu Głównego (07.01):** Podmiana GŁÓWNYCH plików czcionek (`MWC_Font.dds` oraz `.ccm`) na wersję rosyjską **NIE WYŚWIETLIŁA cyrylicy**.
4. **Ostateczna Diagnoza:** Gra w trybie angielskim ignoruje wszystko powyżej kodu ASCII 127. Nawet jeśli dorysujemy litery w pliku graficznym, silnik i tak ich nie wyświetli, dopóki "myśli", że operuje na standardowym alfabecie łacińskim.

---

## 🛠️ Plan Działania na przyszłość (Eksperymentalny)

### OPCJA A: "Infiltracja Językowa" (Nowy pomysł)
Zamiast nadpisywać angielski, moglibyśmy spróbować wgrać polskie tłumaczenie w miejsce **Języka Rosyjskiego** lub **Chińskiego** (które natywnie obsługują szerokie zestawy znaków).
- **Zadanie:** Sprawdzić, jak wymusić w grze język rosyjski (np. przez SteamID/GOG config) i sprawdzić, czy wtedy polskie znaki w bazie zostaną "przepuszczone".
- **Ryzyko:** Gra może mieć osobne fonty dla UI i napisów.

### OPCJA B: "Podmiana wewnątrz-ASCII" (Brute Force)
Jeśli opcja A zawiedzie, można spróbować podmienić znaki specjalne, które *są* w ASCII (np. `^`, `~`, `[`, `{`), na grafiki polskich liter w pliku DDS.
- **Zadanie:** Sprawdzić w `MWC_Font.dds`, które znaki ASCII 0-127 są najmniej używane.
- **Zadanie:** Skryptowo zamienić w bazie `ą` -> `[` i sprawdzić, czy w grze pojawi się `[`.

### OPCJA C: "Biała Flaga" (Czytelność ponad estetykę)
Jeśli powyższe zawiodą, pozostaje uruchomienie `TOOL_Fix_ASCII.py`.
- **Zaleta:** 100% czytelności, brak znaków zapytania.
- **Wada:** Brak "ogonków" (ą, ć, ę...).

---

## 📂 Stan Techniczny
- **Oryginalne czcionki:** Przywrócone (MWC_Font.dds).
- **Baza robocza:** `work/texts_may30_PL.db` (zachowuje polskie znaki).
- **GitHub:** Zaktualizowany o logi i plan.

**Prezydenckie podsumowanie:** Bitwa o fonty nie została wygrana, ale wywiad zebrał kluczowe dane. Wilson wróci do walki innym razem.

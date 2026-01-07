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

# ☢️ Strefa Robocza PhyreEngine (Work Zone)

Ten katalog służy jako **brudnopis operacyjny** do modyfikacji plików binarnych gry (`.phyre`).

## ⚠️ ZASADY BEZPIECZEŃSTWA
1. **NIE WRZUCAJ DO GIT-a:** Pliki w tym folderze (tekstury, kontenery .phyre) są duże i chronione prawem autorskim. Git powinien ignorować wszystko poza tym README i logami.
2. **BACKUP:** Zawsze pracuj na kopii pliku (np. `_ru_RU.phyre`), trzymając oryginał (`_en_US.phyre`) jako nienaruszony wzorzec.

## 📂 Struktura folderu
* **`mission_logs/`** - Dziennik operacyjny (raporty z sesji, znaleziska offsetów).
* **`extracted/`** - (Generowany automatycznie) Surowe pliki .dds wyciągnięte skryptem `11_Extract`.
* **`modified/`** - Tu wrzucasz edytowane w GIMP pliki .dds gotowe do wstrzyknięcia.
* **`*.phyre`** - Pliki kontenerów gry (kopiowane ręcznie z folderu gry).
* **`texture_map.json`** - Mapa offsetów generowana przez skrypt ekstrakcji.

## 🔧 Procedura Modyfikacji (Szybki Start)

1. **RECON:** Wrzuć `menu_common_en_US.phyre` do tego folderu.
2. **EXTRACT:** Uruchom `python3 ../scripts/11_Phyre_Texture_Extract.py`.
3. **EDIT:** Znajdź plik w `extracted/`, edytuj w GIMP, wyeksportuj jako **DXT5** do `modified/` (zachowaj początek nazwy np. `tex_005_...`).
4. **INJECT:** Uruchom `python3 ../scripts/12_Phyre_Texture_Inject.py <ID>`, np. `5`.
5. **DEPLOY:** Skopiuj wynikowy plik `menu_common_ru_RU.phyre` do gry.

---
*Niech chaos będzie z Tobą, ale porządek w plikach.*

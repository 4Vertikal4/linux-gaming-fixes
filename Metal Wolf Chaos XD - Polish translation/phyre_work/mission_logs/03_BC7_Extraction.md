# 📝 Raport Operacyjny: OPERACJA BC7
**Data:** 21.01.2026
**Cel:** Poprawna wizualizacja tekstur menu
**Metoda:** Ekstrakcja z doklejeniem nagłówka DDS DX10 (BC7_UNORM)

## 🛠️ Przebieg
1. Skrypt `14_Phyre_BC7_Extract.py` generuje nagłówek z `FourCC = 'DX10'` i dodatkową strukturą `DDS_HEADER_DXT10`.
2. Format DXGI ustawiony na `98` (BC7_UNORM).
3. Padding danych zastosowany tak samo jak w próbie DXT5.

## 🔍 Weryfikacja
Pliki wyeksportowane do `phyre_work/extracted_bc7`.
Oczekiwany rezultat w GIMP:
- Czysty obraz przycisków (może być lekko przesunięty/ucięty na górze przez metadane).
- Brak "kolorowego szumu".

## 🚀 Status
Testowanie w GIMP...

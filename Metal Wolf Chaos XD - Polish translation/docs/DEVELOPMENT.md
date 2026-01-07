# 🦅 Metal Wolf Chaos XD - Polish Localization Project

## 💻 My Setup
- **OS:** Fedora 42 (Linux)
- **Hardware:** RTX 3060 Ti (8GB VRAM)
- **Environment:** Python 3.13.7 + VENV
- **Platform:** Heroic Games Launcher (GOG version)

## 🛠️ Technology Stack
- **Engine:** Modified PhyreEngine (General Arcade remaster)
- **Database:** SQLite3 (`texts_may30.db`)
- **Fonts:** Bitmap Fonts (DDS textures + CCM character maps)
- **AI Models:** Bielik-4.5B / Llama-3.1-8B (via local PyTorch or API)

## 📂 Key Game Locations
- **Main Path:** `~/Games/Heroic/Metal Wolf Chaos XD/`
- **Texts:** `Media/Texts/texts_may30.db`
- **Fonts:** `rom/font/` (MWC_Font.dds, MWC_Font.ccm)

## 🔄 Current Translation Pipeline
1. **Extraction:** No extraction needed - game uses standard SQLite databases.
2. **Translation:** 
   - `07_Batch_Export_Import.py` for bulk AI translation.
   - `config_translator.py` for auto-discovery of tables (maps, menu, weapon).
3. **Review:** `06_Interactive_Reviewer.py` for manual polish and context correction.
4. **Injection:** `05_Deploy_To_Game.py` - copies translated columns over English ones to trick the engine.

## 🚧 Known Challenges
- **Font Support:** The engine ignores `_EU` and `_ru_RU` font suffixes in English mode.
- **Missing Glyphs:** Polish characters (ą, ć, ę...) are missing in the main `MWC_Font.dds` file.
- **Current Mission:** Testing if the main font can be remapped or if ASCII fallback is required.

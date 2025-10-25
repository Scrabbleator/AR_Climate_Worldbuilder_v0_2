
# AR.Climate World-Builder (v0.2)

A ready-to-run Streamlit app that produces:
- Climate Profile Sheet (derived physics-lite logic)
- Human-friendly **Climate Prompt**
- Machine-friendly **Climate Syntax**
- **Save/Load JSON** and text summary export

## 🏃‍♂️ Run locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## ☁️ Deploy on Streamlit Cloud (via GitHub)
1. Push this folder to a new GitHub repo.
2. On Streamlit Cloud: *New app* → point to your repo → pick `streamlit_app.py` as the entry point.
3. No secrets required.

## 📁 Project layout
```
AR_Climate_Worldbuilder_v0_2/
  ├─ streamlit_app.py         # UI + app orchestration
  ├─ climate_logic.py         # core climate logic helpers
  ├─ requirements.txt
  ├─ sample_profiles/
  │    └─ founders_basin.json
  ├─ .gitignore
  └─ README.md
```

## 🔗 Bridge to AR.Architectural Style Builder
The JSON contains `derived` and `adaptations` keys. Load that JSON in your Architecture app and apply:
- `biome_guess`, `humidity_regime`, `seasonality_index`, `diurnal`
- `adaptations` sub-keys (envelope/openings/ventilation/roof/urban)

## 📝 License
MIT

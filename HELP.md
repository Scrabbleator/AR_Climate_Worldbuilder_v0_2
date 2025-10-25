
# AR.Climate World-Builder — Help

**Goal:** turn a few grounded, physics-lite inputs into a believable **climate profile** that your architecture and scenes can react to.

---

## Sections

### 1) Location & Sun
- **Latitude:** Solar angle driver. Lower = hotter, smaller seasonal swings.
- **Hemisphere:** Controls the direction of prevailing winds shown in examples.
- **Axial Tilt Severity:** How strong your seasons are (mild/earth-like/strong).
- **Daylength Bias:** Optional override if your world has unusual daylight cycles.

### 2) Landform & Elevation
- **Topography:** Basins trap heat/cold, mountains unlock rain-shadow logic, archipelagos boost humidity.
- **Mean Elevation:** Applies a standard lapse rate (~–0.65°C per 100 m).

### 3) Water & Currents
- **Distance to Ocean:** Closer → smaller temperature swings, more humidity.
- **Dominant Ocean Current:** Warm = more moisture/instability; Cold = fog/stability.

### 4) Wind & Orography
- **Prevailing Wind:** Trades (E→W), Westerlies (W→E), Polar Easterlies, or Local/Monsoon.
- **If Mountain Range:** Leeward = drier (rain shadow), Windward = wetter.

### 5) Air & Sky
- **Atmospheric Quirks:** Dust/aerosol, volcanic ash, humidity haze, thin air — these tint the light and mood.

### 6) Moisture System
- **Pattern:** Maritime year‑round, summer monsoon, winter westerlies, convectional storms, or rain‑shadowed.
- **Annual Precipitation (mm):** Rough ranges: Arid (0–250), Semi‑arid (251–500), Temperate (501–1,000), Humid (1,001+).

### 7) Temperature Character
- **Warm/Cool Season Means:** Guideposts for the feel of the place.
- **Diurnal Swing:** High in deserts (clear skies), low near coasts/cloud.

### 8) Extreme Events
- Tick what’s common. This adds protective details (e.g., sand baffles, flood routing).

### Outputs
- **Derived Overview:** Lat band, continentality, humidity, **biome guess**, palette.
- **Adaptation Pack:** Envelope, openings, ventilation, roof, and urban rules you can pipe into architecture.
- **Prompt & Syntax:** Human‑readable prompt + machine‑friendly block for your AR apps.

---

## Quick Workflow
1. Fill top‑to‑bottom.  
2. Click **Generate Climate Profile**.  
3. Download **JSON** and load it inside **Architectural Style Builder** to pre‑fill climate constraints.  
4. Use the **Prompt** as a seed for creative rendering.

---

## Notes
- This is deliberately *stylised*. It won’t replace a climate model, but it will keep your worldbuilding coherent.
- The **Biome** is a best‑fit suggestion — you can override it later on, inside the Architecture app if you expose a manual toggle.

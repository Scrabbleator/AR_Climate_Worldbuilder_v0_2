
# streamlit_app.py
# AR.Climate World-Builder — v0.3 (Help-enabled)
import json
from datetime import datetime
import streamlit as st
from climate_logic import (
    band_from_lat, seasonality_from_tilt, continentality_from_distance,
    current_bias_from_radio, rain_shadow_factor, humidity_regime_from_precip,
    adjust_humidity_for_modifiers, biome_lookup, sky_palette, adaptation_pack,
    to_prompt, to_syntax
)

st.set_page_config(page_title="AR.Climate World-Builder", page_icon="🌍", layout="wide")

# ===== Header =====
col_head_l, col_head_r = st.columns([1,1])
with col_head_l:
    st.title("🌍 AR.Climate World-Builder")
    st.caption("Physics-lite climate logic → Biome → Architectural adaptations → Prompt & Syntax")
with col_head_r:
    with st.expander("ℹ️ About & Help (quick)", expanded=False):
        st.markdown("""
**Goal:** Turn a few grounded inputs into a believable **climate profile** that downstream tools can react to.

**Workflow:** Fill sections 1→8 · Generate · Download JSON · Load in **AR.Architectural Style Builder**.

See full docs in **Help** → sidebar.
""")

# ===== Sidebar =====
st.sidebar.title("📦 Save / Load")
world_name = st.sidebar.text_input("World / Region Name", placeholder="e.g., Overmorrow — Founders Basin")
uploaded = st.sidebar.file_uploader("Load JSON", type=["json"])
if uploaded:
    data = json.load(uploaded)
    st.session_state["loaded"] = data
    st.sidebar.success("Loaded settings from JSON.")

save_label = st.sidebar.text_input("Export filename", value="climate_profile.json")

st.sidebar.markdown("---")
with st.sidebar.expander("❓ Help (full)"):
    with open("HELP.md","r") as f:
        st.markdown(f.read())

# ===== Q&A =====
colA, colB, colC = st.columns([1.2,1,1])
with colA:
    st.subheader("1) Location & Sun")
    with st.expander("What is this section doing?"):
        st.markdown("- **Latitude** sets solar angle and season size.\n- **Tilt** controls seasonality.\n- **Daylength bias** is an optional worldbuilding override.")
    latitude_deg = st.number_input("Latitude (0–85°)", min_value=0.0, max_value=85.0, value=18.0, step=0.5)
    hemisphere = st.selectbox("Hemisphere", ["N","S"])
    tilt_choice = st.radio("Axial Tilt Severity", ["Mild","Earth-like","Strong"], index=1, horizontal=True)
    day_override = st.selectbox("Daylength bias (optional)", ["Use latitude default","Lower than default","Higher than default"], index=0)

with colB:
    st.subheader("2) Landform & Elevation")
    with st.expander("What is this section doing?"):
        st.markdown("- **Topography** unlocks basin/orographic effects.\n- **Elevation** applies lapse rate (~–0.65°C/100 m).")
    topography = st.selectbox("Topography", ["Coastal plain","Plateau","Basin","Mountain range","Archipelago"])
    elevation_m = st.number_input("Mean elevation (m)", min_value=0, max_value=5000, value=350)
    st.subheader("3) Water & Currents")
    with st.expander("What is this section doing?"):
        st.markdown("- **Ocean distance** controls continentality (temp swings).\n- **Currents** bias humidity: warm = wetter; cold = fog/stability.")
    ocean_distance = st.radio("Distance to Ocean", ["Coastal (≤50 km)","Near-coastal (50–200 km)","Interior (>200 km)"], index=2)
    ocean_current = st.radio("Dominant Ocean Current (if coastal)", ["Warm","Cold","Neutral"], index=2)

with colC:
    st.subheader("4) Wind & Orography")
    with st.expander("What is this section doing?"):
        st.markdown("- **Prevailing wind** sets moisture advection.\n- **Windward/Leeward** (mountains) add/remove rainfall via rain shadow.")
    prevailing_wind = st.selectbox("Prevailing Wind", ["Trade (E→W)","Westerly (W→E)","Polar Easterly","Local/Monsoon"])
    orog_pos = st.selectbox("If Mountain range", ["Windward","Leeward","Cross-valley mixed"])
    st.subheader("5) Air & Sky")
    with st.expander("What is this section doing?"):
        st.markdown("- **Atmospheric quirks** tint your sky and light palette for scenes.")
    atmo_quirks = st.multiselect("Atmospheric quirks (optional)", ["High dust/aerosol","Volcanic ash periods","High humidity haze","Thin air"])

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("6) Moisture System")
    with st.expander("What is this section doing?"):
        st.markdown("- Choose a **moisture pattern** and set **annual precipitation**.\n- Output classifies humidity: arid, semi‑arid, temperate, humid.")
    moisture_pattern = st.selectbox("Moisture source pattern", ["Year-round maritime","Summer monsoon","Winter westerlies","Convectional storms only","Rain-shadowed"])
    precip_mm = st.slider("Annual precipitation (mm)", 0, 3000, 320, step=10)

with col2:
    st.subheader("7) Temperature Character")
    with st.expander("What is this section doing?"):
        st.markdown("- Set warm/cool season means.\n- **Diurnal swing** is high in deserts & clear‑sky climates.")
    t_warm_high_c = st.number_input("Mean warm-season high (°C)", value=38.0, step=0.5)
    t_cool_low_c = st.number_input("Mean cool-season low (°C)", value=6.0, step=0.5)
    diurnal_swing = st.radio("Diurnal swing", ["Low (coastal/cloudy)","Medium","High (desert/clear)"], index=2)

with col3:
    st.subheader("8) Extreme Events")
    with st.expander("What is this section doing?"):
        st.markdown("- Tick frequently occurring extremes; we add protective details in the **Adaptation Pack**.")
    extremes = st.multiselect(
        "Extreme weather frequency",
        ["Sand/dust storms","Cyclones/Typhoons","Flash floods","Heatwaves","Blizzards","Hail","Rare"],
        default=["Sand/dust storms","Flash floods"]
    )
    building_uses = st.multiselect("Building use focus", ["Residential","Civic","Industrial","Sacred","Market"], default=["Residential","Market"])

st.markdown("---")
generate = st.button("🚀 Generate Climate Profile", use_container_width=True, type="primary")

# ===== Compute & Output =====
if generate:
    meta = {"app": "AR.ClimateWorldBuilder", "version":"0.3", "timestamp": datetime.utcnow().isoformat()+"Z"}
    inputs = {
        "world_name": (world_name or "Untitled").strip(),
        "latitude_deg": latitude_deg, "hemisphere": hemisphere,
        "tilt": tilt_choice, "daylength_override": (day_override if day_override!="Use latitude default" else None),
        "elevation_m": elevation_m, "topography": topography,
        "ocean_distance": ocean_distance, "ocean_current": ocean_current,
        "prevailing_wind": prevailing_wind, "orography_position": orog_pos,
        "atmo_quirks": atmo_quirks,
        "moisture_pattern": moisture_pattern, "precip_mm": int(precip_mm),
        "t_warm_high_c": float(t_warm_high_c), "t_cool_low_c": float(t_cool_low_c),
        "diurnal_swing": diurnal_swing, "extremes": extremes, "building_uses": building_uses
    }

    lat_band = band_from_lat(inputs["latitude_deg"])
    seasonality = seasonality_from_tilt(inputs["tilt"], inputs["daylength_override"])
    continentality = continentality_from_distance(inputs["ocean_distance"])
    current_bias = current_bias_from_radio(inputs["ocean_current"])
    rshadow = rain_shadow_factor(inputs["topography"], inputs["orography_position"])
    base_humidity = humidity_regime_from_precip(inputs["precip_mm"])
    humidity_final = adjust_humidity_for_modifiers(base_humidity, current_bias, rshadow)
    lapse_c = round(-0.0065 * inputs["elevation_m"], 1)

    biome = biome_lookup(lat_band, humidity_final, seasonality, continentality)
    has_dust = "High dust/aerosol" in inputs["atmo_quirks"]
    palette = sky_palette(humidity_final, has_dust, current_bias, inputs["diurnal_swing"])
    tags = [f"#{humidity_final}", f"#{lat_band}", f"#{continentality}", f"#diurnal-{inputs['diurnal_swing'].split(' ')[0].lower()}"]
    if rshadow != "none": tags.append("#rainshadow")
    if current_bias != "none": tags.append(f"#current-{current_bias}")

    derived = {
        "lat_band": lat_band,
        "seasonality_index": seasonality,
        "continentality_index": continentality,
        "elevation_lapse_adjust": f"{lapse_c:+.1f}C",
        "current_bias": current_bias,
        "rain_shadow_factor": rshadow,
        "humidity_regime": humidity_final,
        "biome_guess": biome,
        "palette": palette,
        "tags": tags
    }

    adaptations = adaptation_pack(biome, inputs["diurnal_swing"], inputs["extremes"])
    prompt = to_prompt(inputs, derived, adaptations)
    syntax = to_syntax(meta, inputs, derived, adaptations)

    st.success("Climate Profile generated.")
    left, right = st.columns([1.2,1])
    with left:
        st.subheader("📄 Climate Prompt")
        st.write(prompt)
        st.subheader("🧬 Climate Syntax")
        st.code(syntax, language="yaml")
    with right:
        st.subheader("🔎 Derived Overview")
        st.json(derived, expanded=False)
        st.subheader("🏛️ Adaptation Pack")
        st.json(adaptations, expanded=False)

    st.markdown("---")
    dcol1, dcol2 = st.columns(2)
    with dcol1:
        st.download_button("⬇️ Download JSON", data=json.dumps({
            "meta": meta, "inputs": inputs, "derived": derived,
            "adaptations": adaptations, "prompt": prompt, "syntax": syntax
        }, indent=2), file_name=save_label or "climate_profile.json", mime="application/json", use_container_width=True)
    with dcol2:
        st.download_button("⬇️ Download Summary (.txt)", data=(f"{prompt}\n\n{syntax}").encode("utf-8"),
                           file_name="climate_profile.txt", mime="text/plain", use_container_width=True)

# one-time reload if JSON loaded
if "loaded" in st.session_state and st.session_state["loaded"]:
    st.session_state["loaded"] = None
    st.experimental_rerun()

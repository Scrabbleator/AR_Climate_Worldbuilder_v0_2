
# streamlit_app.py
# AR.Climate World-Builder — v0.2
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

st.title("🌍 AR.Climate World-Builder")
st.caption("Physics-lite climate logic → Biome → Architectural adaptations → Prompt & Syntax")

# ---------- Sidebar (Save/Load) ----------
st.sidebar.title("📦 Save / Load")
world_name = st.sidebar.text_input("World / Region Name", placeholder="e.g., Overmorrow — Founders Basin")

uploaded = st.sidebar.file_uploader("Load JSON", type=["json"])
if uploaded:
    data = json.load(uploaded)
    st.session_state["loaded"] = data
    st.sidebar.success("Loaded settings from JSON.")

save_label = st.sidebar.text_input("Export filename", value="climate_profile.json")

# ---------- Q&A Flow ----------
colA, colB, colC = st.columns([1.2,1,1])
with colA:
    st.subheader("1) Location & Sun")
    latitude_deg = st.number_input("Latitude (0–85°)", min_value=0.0, max_value=85.0, value=18.0, step=0.5)
    hemisphere = st.selectbox("Hemisphere", ["N","S"])
    tilt_choice = st.radio("Axial Tilt Severity", ["Mild","Earth-like","Strong"], index=1, horizontal=True)
    day_override = st.selectbox("Daylength bias (optional)", ["Use latitude default","Lower than default","Higher than default"], index=0)

with colB:
    st.subheader("2) Landform & Elevation")
    topography = st.selectbox("Topography", ["Coastal plain","Plateau","Basin","Mountain range","Archipelago"])
    elevation_m = st.number_input("Mean elevation (m)", min_value=0, max_value=5000, value=350)
    st.subheader("3) Water & Currents")
    ocean_distance = st.radio("Distance to Ocean", ["Coastal (≤50 km)","Near-coastal (50–200 km)","Interior (>200 km)"], index=2)
    ocean_current = st.radio("Dominant Ocean Current (if coastal)", ["Warm","Cold","Neutral"], index=2)

with colC:
    st.subheader("4) Wind & Orography")
    prevailing_wind = st.selectbox("Prevailing Wind", ["Trade (E→W)","Westerly (W→E)","Polar Easterly","Local/Monsoon"])
    orog_pos = st.selectbox("If Mountain range", ["Windward","Leeward","Cross-valley mixed"])
    st.subheader("5) Air & Sky")
    atmo_quirks = st.multiselect("Atmospheric quirks (optional)", ["High dust/aerosol","Volcanic ash periods","High humidity haze","Thin air"])

st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("6) Moisture System")
    moisture_pattern = st.selectbox("Moisture source pattern", ["Year-round maritime","Summer monsoon","Winter westerlies","Convectional storms only","Rain-shadowed"])
    precip_mm = st.slider("Annual precipitation (mm)", 0, 3000, 320, step=10)

with col2:
    st.subheader("7) Temperature Character")
    t_warm_high_c = st.number_input("Mean warm-season high (°C)", value=38.0, step=0.5)
    t_cool_low_c = st.number_input("Mean cool-season low (°C)", value=6.0, step=0.5)
    diurnal_swing = st.radio("Diurnal swing", ["Low (coastal/cloudy)","Medium","High (desert/clear)"], index=2)

with col3:
    st.subheader("8) Extreme Events")
    extremes = st.multiselect(
        "Extreme weather frequency",
        ["Sand/dust storms","Cyclones/Typhoons","Flash floods","Heatwaves","Blizzards","Hail","Rare"],
        default=["Sand/dust storms","Flash floods"]
    )
    building_uses = st.multiselect("Building use focus", ["Residential","Civic","Industrial","Sacred","Market"], default=["Residential","Market"])

st.markdown("---")
generate = st.button("🚀 Generate Climate Profile", use_container_width=True, type="primary")

# ---------- Compute & Output ----------
if generate:
    meta = {"app": "AR.ClimateWorldBuilder", "version":"0.2", "timestamp": datetime.utcnow().isoformat()+"Z"}
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

    lat_band = band_from_lat(latitude_deg)
    seasonality = seasonality_from_tilt(tilt_choice, inputs["daylength_override"])
    continentality = continentality_from_distance(ocean_distance)
    current_bias = current_bias_from_radio(ocean_current)
    rshadow = rain_shadow_factor(topography, orog_pos)
    base_humidity = humidity_regime_from_precip(inputs["precip_mm"])
    humidity_final = adjust_humidity_for_modifiers(base_humidity, current_bias, rshadow)
    lapse_c = round(-0.0065 * elevation_m, 1)  # °C per m

    biome = biome_lookup(lat_band, humidity_final, seasonality, continentality)
    has_dust = "High dust/aerosol" in atmo_quirks
    palette = sky_palette(humidity_final, has_dust, current_bias, diurnal_swing)
    tags = [f"#{humidity_final}", f"#{lat_band}", f"#{continentality}", f"#diurnal-{diurnal_swing.split(' ')[0].lower()}"]
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

    adaptations = adaptation_pack(biome, diurnal_swing, extremes)
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

# Preload from sidebar if present
if "loaded" in st.session_state and st.session_state["loaded"]:
    data = st.session_state["loaded"]
    st.session_state["loaded"] = None
    st.experimental_rerun()

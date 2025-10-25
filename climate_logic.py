
"""
AR.Climate World-Builder — core logic helpers
v0.2
"""

from typing import List

def band_from_lat(lat_deg: float) -> str:
    if lat_deg <= 10:  return "tropical"
    if lat_deg <= 23:  return "subtropical"
    if lat_deg <= 45:  return "temperate"
    if lat_deg <= 66:  return "subpolar"
    return "polar"

def seasonality_from_tilt(tilt_choice: str, day_override: str|None) -> str:
    mapping = {"Mild":"low", "Earth-like":"medium", "Strong":"high"}
    s = mapping.get(tilt_choice, "medium")
    if day_override == "Lower than default":
        return "low"
    if day_override == "Higher than default":
        return "high"
    return s

def continentality_from_distance(dist: str) -> str:
    return {"Coastal (≤50 km)":"low", "Near-coastal (50–200 km)":"medium", "Interior (>200 km)":"high"}[dist]

def current_bias_from_radio(r: str) -> str:
    return {"Warm":"warm", "Cold":"cold", "Neutral":"none"}[r]

def rain_shadow_factor(topography: str, orog_pos: str) -> str:
    if topography != "Mountain range":
        return "none"
    return {"Windward":"none", "Leeward":"strong", "Cross-valley mixed":"moderate"}[orog_pos]

def humidity_regime_from_precip(mm: int) -> str:
    if mm <= 250:   return "arid"
    if mm <= 500:   return "semi-arid"
    if mm <= 1000:  return "temperate"
    return "humid"

def adjust_humidity_for_modifiers(base: str, current_bias: str, rainshadow: str) -> str:
    order = ["arid","semi-arid","temperate","humid"]
    idx = order.index(base)
    if current_bias == "warm" and idx < len(order)-1:
        idx += 1
    # cold currents tend to stabilise/cool SSTs; we keep same bracket for simplicity
    if rainshadow == "strong" and idx > 0:
        idx -= 1
    if rainshadow == "moderate" and base in ["temperate","humid"]:
        idx -= 1
    return order[idx]

def biome_lookup(lat_band: str, humidity: str, seasonality: str, continentality: str) -> str:
    if lat_band in ["polar","subpolar"]:
        return "Tundra / Ice (ET/EF)" if lat_band == "polar" else "Boreal / Subpolar (Dfc/Dfd)"
    if humidity == "arid":
        return "Hot Desert (BWh)" if lat_band in ["tropical","subtropical"] else "Cold Desert (BWk)"
    if humidity == "semi-arid":
        return "Steppe (BSh)" if lat_band in ["tropical","subtropical","temperate"] else "Steppe (BSk)"
    if humidity == "humid" and lat_band == "tropical":
        return "Tropical Rain/Monsoon (Af/Am/Aw)"
    if lat_band in ["temperate","subtropical"]:
        if continentality == "low":
            return "Marine Temperate (Cfb/Csb)"
        if seasonality == "high" and continentality == "high":
            return "Humid Continental (Dfa/Dfb)"
        return "Warm Temperate (Cfa/Cwa)"
    return "Mixed / Transitional"

def sky_palette(humidity: str, dust: bool, current_bias: str, diurnal: str) -> str:
    parts = []
    if humidity in ["arid","semi-arid"]:
        parts.append("clear high-contrast light")
    elif humidity == "humid":
        parts.append("diffuse, saturated light")
    else:
        parts.append("tempered daylight")

    if dust:
        parts.append("frequent dust haze")
    if current_bias == "cold":
        parts.append("milk-blue overcast episodes")
    if diurnal == "High (desert/clear)":
        parts.append("indigo-violet twilight, strong golden hour")
    elif diurnal == "Low (coastal/cloudy)":
        parts.append("soft transitions, narrow golden hour")
    return ", ".join(parts)

def adaptation_pack(biome: str, diurnal: str, extremes: List[str]) -> dict:
    pack = {}
    if "Hot Desert" in biome or "Steppe" in biome:
        pack["envelope"] = "thick mass walls; light exterior albedo; exterior shading"
        pack["openings"] = "small recessed windows; shutters; dust seals/filters"
        pack["ventilation"] = "stack effect + courtyards; optional wind-catchers"
        pack["roof"] = "moderate pitch; reflective; oversized scuppers for cloudbursts"
        pack["urban"] = "narrow shaded streets; arcades; retention basins in wadis"
    elif "Tropical" in biome:
        pack["envelope"] = "lightweight, permeable walls; mould-resistant finishes"
        pack["openings"] = "large operable windows; screens; deep overhangs"
        pack["ventilation"] = "cross-ventilation; ventilated ridges"
        pack["roof"] = "steep roof; rain-screens; generous gutters"
        pack["urban"] = "permeable grid; shaded walkways; storm channels"
    elif "Marine Temperate" in biome or "Warm Temperate" in biome:
        pack["envelope"] = "moderate insulation; rain-screen facades; capillary breaks"
        pack["openings"] = "balanced glazing; wind-bracing details"
        pack["ventilation"] = "mixed-mode (natural + mechanical fallback)"
        pack["roof"] = "30–45° pitched; robust flashing"
        pack["urban"] = "rain gardens; bioswales; salt-resistant metals near coast"
    elif "Humid Continental" in biome or "Boreal" in biome:
        pack["envelope"] = "super-insulation; thermal bridges minimised"
        pack["openings"] = "compact window-to-wall; triple glazing; vestibules"
        pack["ventilation"] = "mechanical with heat recovery"
        pack["roof"] = "steep roofs for snow shed; dark absorptive finishes"
        pack["urban"] = "windbreaks; compact massing; enclosed links"
    elif "Tundra" in biome:
        pack["envelope"] = "elevated structures; permafrost-compatible foundations"
        pack["openings"] = "small apertures; storm shutters"
        pack["ventilation"] = "mechanical with heat recovery"
        pack["roof"] = "low wind profiles; snow fencing"
        pack["urban"] = "enclosed walkways; service tunnels"
    if "Sand/dust storms" in extremes:
        pack["openings"] = (pack.get("openings","") + "; sand baffles").strip("; ")
    if "Flash floods" in extremes:
        pack["urban"] = (pack.get("urban","") + "; raised thresholds; flood routing").strip("; ")
    if diurnal == "High (desert/clear)":
        pack["envelope"] = (pack.get("envelope","") + "; internal thermal mass").strip("; ")
    return pack

def clean_list(x):
    return [i for i in x if i and i != "None"]

def to_syntax(meta, inputs, derived, adaptations):
    lines = []
    lines.append("CLIMATE {")
    lines.append(f"  world: {inputs.get('world_name','Untitled')!r}")
    lines.append(f"  lat_band: {derived['lat_band']}")
    lines.append(f"  seasonality: {derived['seasonality_index']}")
    lines.append(f"  continentality: {derived['continentality_index']}")
    lines.append(f"  humidity: {derived['humidity_regime']}")
    lines.append(f"  biome: {derived['biome_guess']!r}")
    lines.append(f"  current_bias: {derived['current_bias']}")
    lines.append(f"  rain_shadow: {derived['rain_shadow_factor']}")
    lines.append(f"  elevation_lapse_adjust: {derived['elevation_lapse_adjust']}")
    lines.append(f"  diurnal: {inputs['diurnal_swing']}")
    lines.append(f"  extremes: {clean_list(inputs['extremes'])}")
    lines.append(f"  palette: {derived['palette']!r}")
    lines.append("  adaptations: {")
    for k,v in adaptations.items():
        lines.append(f"    {k}: {v!r}")
    lines.append("  }")
    lines.append("  tags: " + str(derived['tags']))
    lines.append("}")
    return "\n".join(lines)

def to_prompt(inputs, derived, adaptations):
    ex_list = clean_list(inputs.get('extremes', []))
    ex = ", ".join(ex_list) if ex_list else "rare extremes"
    return (
        f"A {derived['biome_guess']} region at {inputs['latitude_deg']}°{inputs['hemisphere']} "
        f"with {derived['humidity_regime']} humidity and {derived['continentality_index']} continentality. "
        f"Seasonality is {derived['seasonality_index']}; diurnal swing is {inputs['diurnal_swing']}. "
        f"Ocean current bias: {derived['current_bias']}; rain shadow: {derived['rain_shadow_factor']}. "
        f"Sky: {derived['palette']}. Extremes: {ex}. "
        f"Architectural adaptations include: envelope [{adaptations.get('envelope','n/a')}], openings [{adaptations.get('openings','n/a')}], "
        f"ventilation [{adaptations.get('ventilation','n/a')}], roof [{adaptations.get('roof','n/a')}], urban [{adaptations.get('urban','n/a')}]."
    )

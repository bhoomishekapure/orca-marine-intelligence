import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from backend.llm.base_provider import LLMProvider

def is_marathi_text(text: str) -> bool:
    marathi_words = ["उद्या", "सकाळी", "दुपारी", "रत्नागिरी", "मासेमारी", "सुरक्षित", "समुद्र", "लाटा", "वारा", "आहे", "का", "बंदर"]
    return any(w in text for w in marathi_words) or bool(re.search(r"[\u0900-\u097F]", text) and ("का" in text or "आहे" in text or "मासेमारी" in text))

def is_hindi_text(text: str) -> bool:
    hindi_words = ["कल", "सुबह", "मछली", "सुरक्षित", "समुद्र", "हवा", "क्या", "है"]
    return any(w in text for w in hindi_words)

class MockRuleBasedProvider(LLMProvider):
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return "ORCA AI response generated from verified marine observations."

    async def extract_intent_and_entities(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        q_lower = query.lower()
        context = context or {}

        # 1. Detect Language
        lang = "en"
        if is_marathi_text(query):
            lang = "mr"
        elif is_hindi_text(query):
            lang = "hi"

        # 2. Extract Location
        location_name = context.get("location_name", "Ratnagiri")
        lat = context.get("latitude", 16.99)
        lon = context.get("longitude", 73.30)

        if "mirya" in q_lower or "मिऱ्या" in query:
            location_name = "Mirya Bandar, Ratnagiri"
            lat, lon = 17.0251, 73.2755
        elif "mirkarwada" in q_lower or "मिरकरवाडा" in query:
            location_name = "Mirkarwada, Ratnagiri"
            lat, lon = 17.0019, 73.2842
        elif "bhatye" in q_lower or "भाट्ये" in query:
            location_name = "Bhatye, Ratnagiri"
            lat, lon = 16.9754, 73.2951
        elif "jaigad" in q_lower or "जयगड" in query:
            location_name = "Jaigad"
            lat, lon = 17.3052, 73.2184
        elif "malvan" in q_lower or "मालवण" in query:
            location_name = "Malvan"
            lat, lon = 16.0624, 73.4651
        elif "devgad" in q_lower or "देवगड" in query:
            location_name = "Devgad"
            lat, lon = 16.3751, 73.3752
        elif "ratnagiri" in q_lower or "रत्नागिरी" in query:
            location_name = "Ratnagiri"
            lat, lon = 16.99, 73.30

        # 3. Extract Date
        date_expr = context.get("date_expression", "today")
        if "tomorrow" in q_lower or "उद्या" in query or "कल" in query:
            date_expr = "tomorrow"
        elif "today" in q_lower or "आज" in query:
            date_expr = "today"

        # 4. Extract Time
        time_expr = context.get("time_expression", "06:00")
        if "9 am" in q_lower or "9:00" in q_lower or "९ वाजता" in query or "९" in query:
            time_expr = "09:00"
        elif "6 am" in q_lower or "6:00" in q_lower or "६ वाजता" in query or "६" in query:
            time_expr = "06:00"
        elif "morning" in q_lower or "सकाळी" in query or "सुबह" in query:
            time_expr = "06:00"
        elif "afternoon" in q_lower or "दुपारी" in query or "दोपहर" in query:
            time_expr = "14:00"

        # 5. Classify Intent
        intent = "MARINE_SAFETY"
        if any(w in q_lower for w in ["pfz", "fishing zone", "nearest fishing", "where is the nearest", "zone"]):
            intent = "PFZ_DISCOVERY"
        elif any(w in q_lower for w in ["condition", "conditions", "sea condition", "wave", "wind speed", "हवामान", "स्थिती"]):
            if "safe" not in q_lower and "सुरक्षित" not in query:
                intent = "OCEAN_CONDITIONS"
            else:
                intent = "MARINE_SAFETY"
        elif "safe" in q_lower or "safety" in q_lower or "सुरक्षित" in query:
            intent = "MARINE_SAFETY"
        elif context.get("intent"):
            intent = context.get("intent")

        # 6. Map Required Agents
        required_agents = ["weather", "ocean", "geospatial"]
        if intent == "MARINE_SAFETY":
            required_agents = ["weather", "ocean", "marine_pfz", "geospatial"]
        elif intent == "PFZ_DISCOVERY":
            required_agents = ["marine_pfz", "geospatial", "ocean"]
        elif intent == "OCEAN_CONDITIONS":
            required_agents = ["ocean", "weather", "geospatial"]

        return {
            "language": lang,
            "intent": intent,
            "location": {
                "name": location_name,
                "latitude": lat,
                "longitude": lon
            },
            "date_expression": date_expr,
            "time_expression": time_expr,
            "activity": context.get("activity", "fishing"),
            "required_agents": required_agents
        }

    async def synthesize_response(
        self,
        query: str,
        language: str,
        intent: str,
        risk_data: Dict[str, Any],
        evidence_list: list,
        agent_data: Dict[str, Any]
    ) -> str:
        weather = agent_data.get("weather", {})
        ocean = agent_data.get("ocean", {})
        pfz = agent_data.get("marine_pfz", {})
        geo = agent_data.get("geospatial", {})

        wave_h = ocean.get("data", {}).get("significant_wave_height_m", 1.4)
        wave_p = ocean.get("data", {}).get("wave_period_s", 8.0)
        wind_s = weather.get("data", {}).get("wind_speed_kmh", 24.0)
        wind_dir = weather.get("data", {}).get("wind_direction_cardinal", "WSW")
        risk_level = risk_data.get("risk_level", "SAFE")
        loc_name = geo.get("data", {}).get("origin", {}).get("name", "Ratnagiri")

        nearest_pfz = geo.get("data", {}).get("nearest_pfz")
        
        # Multilingual Generation based on language detected
        if language == "mr":
            if intent == "PFZ_DISCOVERY" and nearest_pfz:
                return (
                    f"{nearest_pfz.get('reference_centre', 'रत्नागिरी')} येथून सर्वात जवळचे संभाव्य मासेमारी क्षेत्र (PFZ) "
                    f"{nearest_pfz.get('distance_km')} किमी अंतरावर {nearest_pfz.get('bearing_deg')}° {nearest_pfz.get('direction')} दिशेला आहे. "
                    f"पाण्याची खोली {nearest_pfz.get('depth_range_m')} असून सागरी पृष्ठभागाचे तापमान {nearest_pfz.get('sst_celsius')}°C आहे. "
                    f"येथे बांगडा, तारली आणि रिबनफिशचे चांगले थवे मिळण्याची शक्यता आहे. (स्रोत: INCOIS)"
                )
            elif intent == "OCEAN_CONDITIONS":
                return (
                    f"{loc_name} जवळ समुद्राची स्थिती शांत ते मध्यम आहे. "
                    f"लाटांची उंची {wave_h} मीटर (कालावधी {wave_p} सेकंद) आणि वाऱ्याचा वेग {wind_s} किमी/तास ({wind_dir} दिशेकडून) आहे. "
                    f"हवामान प्रामुख्याने निरभ्र ते अंशतः ढगाळ राहील."
                )
            else: # MARINE_SAFETY
                safety_text = "होय, मासेमारीसाठी समुद्रात जाणे सुरक्षित आहे." if risk_level == "SAFE" else "सावधगिरी बाळगा."
                return (
                    f"{safety_text} {loc_name} किनारपट्टीजवळ लाटांची उंची {wave_h} मीटर आणि वाऱ्याचा वेग {wind_s} किमी/तास ({wind_dir}) राहील. "
                    f"IMD किंवा INCOIS कडून कोणताही चक्रीवादळ अथवा तीव्र वादळाचा इशारा नाही. "
                    f"नेहमीची मासेमारी सुरक्षित मानली जाते."
                )

        elif language == "hi":
            if intent == "PFZ_DISCOVERY" and nearest_pfz:
                return (
                    f"{nearest_pfz.get('reference_centre', 'रत्नागिरी')} से सबसे नजदीकी संभावित मछली क्षेत्र (PFZ) "
                    f"{nearest_pfz.get('distance_km')} किमी दूरी पर {nearest_pfz.get('bearing_deg')}° {nearest_pfz.get('direction')} दिशा में स्थित है। "
                    f"पानी की गहराई {nearest_pfz.get('depth_range_m')} और समुद्री तापमान {nearest_pfz.get('sst_celsius')}°C है।"
                )
            else:
                safety_text = "हाँ, मछली पकड़ने के लिए समुद्र में जाना सुरक्षित है।" if risk_level == "SAFE" else "सतर्कता आवश्यक है।"
                return (
                    f"{safety_text} {loc_name} तट के पास लहरों की ऊँचाई {wave_h} मीटर और हवा की गति {wind_s} किमी/घंटा है। "
                    f"IMD द्वारा कोई प्रतिकूल मौसम चेतावनी जारी नहीं की गई है।"
                )

        else: # English
            if intent == "PFZ_DISCOVERY" and nearest_pfz:
                return (
                    f"The nearest Potential Fishing Zone (PFZ) relative to {nearest_pfz.get('reference_centre', loc_name)} "
                    f"is located {nearest_pfz.get('distance_km')} km ({nearest_pfz.get('distance_nm')} nm) away at bearing "
                    f"{nearest_pfz.get('bearing_deg')}° {nearest_pfz.get('direction')}. "
                    f"Water depth is {nearest_pfz.get('depth_range_m')} with sea surface temperature at {nearest_pfz.get('sst_celsius')}°C "
                    f"and chlorophyll concentration of {nearest_pfz.get('chlorophyll_mg_m3')} mg/m³. "
                    f"Target species include {nearest_pfz.get('target_species')}."
                )
            elif intent == "OCEAN_CONDITIONS":
                return (
                    f"Sea conditions near {loc_name} are slight to moderate. "
                    f"Significant wave height is {wave_h} m (period {wave_p} s) with swell height of "
                    f"{ocean.get('data', {}).get('swell_wave_height_m', 1.1)} m. "
                    f"Wind is blowing from {wind_dir} at {wind_s} km/h (gusting to {weather.get('data', {}).get('wind_gusts_kmh', 32.0)} km/h). "
                    f"Sea surface temperature is {ocean.get('data', {}).get('sea_surface_temperature_c', 28.5)}°C."
                )
            else: # MARINE_SAFETY
                safety_desc = "generally safe for normal fishing operations" if risk_level == "SAFE" else "subject to caution"
                return (
                    f"Conditions near {loc_name} are {safety_desc}. "
                    f"The significant wave height is {wave_h} m (below the 1.8 m threshold) and wind speed is "
                    f"{wind_s} km/h from {wind_dir}. No active IMD squally weather or cyclone warnings are currently in effect "
                    f"for the South Maharashtra coastline."
                )

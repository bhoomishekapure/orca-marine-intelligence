from typing import Dict, Any, List
from backend.config import settings
from backend.models.schemas import RiskAssessment, RiskFactor, RiskLevelEnum

class DeterministicRiskEngine:
    @staticmethod
    def evaluate(
        weather_data: Dict[str, Any],
        ocean_data: Dict[str, Any],
        geospatial_data: Dict[str, Any],
        evidence_ids: List[str]
    ) -> RiskAssessment:
        factors: List[RiskFactor] = []
        recommendations: List[str] = []
        risk_score = 10  # Base nominal score
        
        # 1. Wave Height Evaluation
        wave_h = float(ocean_data.get("significant_wave_height_m", 1.4))
        if wave_h > settings.WAVE_HEIGHT_CAUTION_M:
            wave_status = "UNSAFE"
            risk_score += 45
            recommendations.append(f"Significant wave height ({wave_h:.1f} m) exceeds rough sea limit ({settings.WAVE_HEIGHT_CAUTION_M} m). Avoid venturing into open sea.")
        elif wave_h > settings.WAVE_HEIGHT_SAFE_M:
            wave_status = "CAUTION"
            risk_score += 25
            recommendations.append(f"Moderate sea swell ({wave_h:.1f} m). Small crafts should exercise caution.")
        else:
            wave_status = "SAFE"
            recommendations.append(f"Favourable sea state ({wave_h:.1f} m). Suitable for normal fishing operations.")
            
        factors.append(RiskFactor(
            parameter="Significant Wave Height",
            value=f"{wave_h:.1f} m",
            threshold=f"< {settings.WAVE_HEIGHT_SAFE_M:.1f} m (Low Risk)",
            status=wave_status
        ))

        # 2. Wind Speed Evaluation
        wind_s = float(weather_data.get("wind_speed_kmh", 24.0))
        if wind_s > settings.WIND_SPEED_CAUTION_KMH:
            wind_status = "UNSAFE"
            risk_score += 40
            recommendations.append(f"High wind speeds ({wind_s:.1f} km/h). Severe drift hazard.")
        elif wind_s > settings.WIND_SPEED_SAFE_KMH:
            wind_status = "CAUTION"
            risk_score += 20
            recommendations.append(f"Fresh onshore breeze ({wind_s:.1f} km/h). Monitor choppy water.")
        else:
            wind_status = "SAFE"
            
        factors.append(RiskFactor(
            parameter="Wind Speed",
            value=f"{wind_s:.1f} km/h",
            threshold=f"< {settings.WIND_SPEED_SAFE_KMH:.0f} km/h (Low Risk)",
            status=wind_status
        ))

        # 3. Active Weather Warnings Evaluation
        active_warnings = weather_data.get("active_warnings", [])
        if active_warnings:
            for w in active_warnings:
                recommendations.append(f"Advisory alert: {w}")
            factors.append(RiskFactor(
                parameter="Severe Weather Warnings",
                value="Active Warnings Present",
                threshold="None",
                status="UNSAFE"
            ))
            risk_score += 40
        else:
            factors.append(RiskFactor(
                parameter="Severe Weather Warnings",
                value="None Active",
                threshold="Green (Nil Warning)",
                status="SAFE"
            ))

        # 4. Geospatial Restriction Evaluation
        is_restricted = geospatial_data.get("is_inside_restricted_zone", False)
        if is_restricted:
            viol = geospatial_data.get("active_violation", {})
            risk_score = 95
            recommendations.append(f"STRICT PROHIBITION: Location is inside {viol.get('name')}. Fishing here is illegal under marine sanctuary conservation laws.")
            factors.append(RiskFactor(
                parameter="Marine Sanctuary Boundary",
                value=f"Inside {viol.get('name')}",
                threshold="Outside boundary",
                status="UNSAFE"
            ))
        else:
            closest = geospatial_data.get("nearest_restricted_zone")
            if closest:
                factors.append(RiskFactor(
                    parameter="Marine Sanctuary Boundary",
                    value=f"{closest.get('distance_km')} km from {closest.get('name')}",
                    threshold="Clear (> 0 km)",
                    status="CLEAR"
                ))

        # Determine Overall Risk Level (LOW, MODERATE, HIGH, UNKNOWN)
        risk_score = min(100, risk_score)
        if is_restricted or any(f.status == "UNSAFE" for f in factors) or risk_score >= 60:
            overall_level = RiskLevelEnum.HIGH
            status_color = "red"
            headline = "High Risk — Unsafe for Normal Fishing Operations"
        elif any(f.status == "CAUTION" for f in factors) or risk_score >= 35:
            overall_level = RiskLevelEnum.MODERATE
            status_color = "yellow"
            headline = "Moderate Risk — Proceed with Caution & Radios Active"
        else:
            overall_level = RiskLevelEnum.LOW
            status_color = "green"
            headline = "Low Risk — Conditions Favourable for Maritime Activities"

        return RiskAssessment(
            risk_level=overall_level,
            risk_score=risk_score,
            status_color=status_color,
            headline=headline,
            factors=factors,
            recommendations=recommendations,
            evidence_ids=evidence_ids
        )

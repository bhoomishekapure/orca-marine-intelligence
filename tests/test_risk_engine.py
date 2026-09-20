import pytest
from reasoning.risk_engine import DeterministicRiskEngine
from backend.models.schemas import RiskLevelEnum

def test_risk_engine_safe():
    weather = {"wind_speed_kmh": 20.0, "active_warnings": []}
    ocean = {"significant_wave_height_m": 1.2}
    geo = {"is_inside_restricted_zone": False, "nearest_restricted_zone": {"name": "Malvan", "distance_km": 60.0}}
    
    assessment = DeterministicRiskEngine.evaluate(weather, ocean, geo, ["EVID-001"])
    assert assessment.risk_level in [RiskLevelEnum.LOW, RiskLevelEnum.SAFE]
    assert assessment.status_color == "green"
    assert assessment.risk_score < 35

def test_risk_engine_high_waves_caution():
    weather = {"wind_speed_kmh": 22.0, "active_warnings": []}
    ocean = {"significant_wave_height_m": 2.1}  # > 1.8m -> MODERATE
    geo = {"is_inside_restricted_zone": False}
    
    assessment = DeterministicRiskEngine.evaluate(weather, ocean, geo, ["EVID-001"])
    assert assessment.risk_level in [RiskLevelEnum.MODERATE, RiskLevelEnum.CAUTION]
    assert assessment.status_color == "yellow"

def test_risk_engine_high_wind_unsafe():
    weather = {"wind_speed_kmh": 48.0, "active_warnings": []}  # > 45 km/h -> HIGH
    ocean = {"significant_wave_height_m": 1.4}
    geo = {"is_inside_restricted_zone": False}
    
    assessment = DeterministicRiskEngine.evaluate(weather, ocean, geo, ["EVID-001"])
    assert assessment.risk_level in [RiskLevelEnum.HIGH, RiskLevelEnum.UNSAFE]
    assert assessment.status_color == "red"

def test_risk_engine_restricted_zone_unsafe():
    weather = {"wind_speed_kmh": 15.0, "active_warnings": []}
    ocean = {"significant_wave_height_m": 1.0}
    geo = {
        "is_inside_restricted_zone": True,
        "active_violation": {"name": "Malvan Marine Sanctuary"}
    }
    
    assessment = DeterministicRiskEngine.evaluate(weather, ocean, geo, ["EVID-001"])
    assert assessment.risk_level in [RiskLevelEnum.HIGH, RiskLevelEnum.UNSAFE]
    assert any("illegal" in r.lower() or "prohibition" in r.lower() for r in assessment.recommendations)

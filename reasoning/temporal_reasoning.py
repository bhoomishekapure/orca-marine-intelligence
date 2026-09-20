from datetime import datetime, timedelta, timezone
from typing import Tuple

class TemporalReasoningEngine:
    @staticmethod
    def resolve_target_datetime(date_expr: str, time_expr: str) -> datetime:
        """Resolve expressions like 'tomorrow', '06:00' into a concrete datetime."""
        now = datetime.now(timezone.utc)
        
        # 1. Resolve date
        target_date = now.date()
        date_lower = (date_expr or "today").lower().strip()
        
        if "tomorrow" in date_lower or "उद्या" in date_lower or "कल" in date_lower:
            target_date = target_date + timedelta(days=1)
        elif "today" in date_lower or "आज" in date_lower:
            pass
        elif date_lower.startswith("202"):
            try:
                target_date = datetime.strptime(date_lower[:10], "%Y-%m-%d").date()
            except ValueError:
                pass
                
        # 2. Resolve time
        hour = 6
        minute = 0
        time_lower = (time_expr or "06:00").lower().strip()
        
        if "9" in time_lower:
            hour = 9
        elif "6" in time_lower:
            hour = 6
        elif "morning" in time_lower or "सकाळी" in time_lower or "सुबह" in time_lower:
            hour = 6
        elif "afternoon" in time_lower or "दुपारी" in time_lower or "दोपहर" in time_lower:
            hour = 14
        elif ":" in time_lower:
            try:
                parts = time_lower.split(":")
                hour = int(parts[0])
                minute = int(parts[1][:2])
            except (ValueError, IndexError):
                hour = 6

        return datetime(target_date.year, target_date.month, target_date.day, hour, minute, 0, tzinfo=timezone.utc)

    @staticmethod
    def compare_time_windows(earlier_time: datetime, later_time: datetime, condition_diff: dict) -> str:
        """Explain the change in conditions when a user changes target time."""
        h1 = earlier_time.strftime("%I %p")
        h2 = later_time.strftime("%I %p")
        
        wave_diff = condition_diff.get("wave_height_diff_m", 0.0)
        wind_diff = condition_diff.get("wind_speed_diff_kmh", 0.0)
        
        explanation = f"Comparing {h1} and {h2}: "
        if abs(wave_diff) < 0.2 and abs(wind_diff) < 5.0:
            explanation += f"Conditions remain very similar. Wave height changes by {wave_diff:+.1f} m and wind speed by {wind_diff:+.1f} km/h."
        else:
            explanation += f"Wave height changes by {wave_diff:+.1f} m and wind speed changes by {wind_diff:+.1f} km/h as diurnal sea breezes evolve."
            
        return explanation

from typing import Dict, Any


class FeatureFlags:
    """Runtime toggles for engine experimental features."""

    def __init__(self):
        self._flags: Dict[str, bool] = {
            "enable_caching": True,
            "enable_spell_suggestions": True,
            "enable_chaos_injection": False,
            "enable_exact_phrase_matching": True,
            "enable_rate_limiting": False,
        }

    def is_enabled(self, flag_name: str) -> bool:
        return self._flags.get(flag_name, False)

    def set_flag(self, flag_name: str, enabled: bool):
        self._flags[flag_name] = enabled

    def get_all(self) -> Dict[str, bool]:
        return dict(self._flags)


feature_flags = FeatureFlags()

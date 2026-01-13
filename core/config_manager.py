"""
Config Manager - Handle app configuration and gamepad profiles
"""

import os
import json
from typing import Optional, Dict, Any, List


class ConfigManager:
    """Manages application configuration and gamepad profiles."""

    DEFAULT_CONFIG = {
        'server_url': 'http://localhost:8082',
        'auto_connect': True,
        'fullscreen': False,
        'active_profile': 'default',
    }

    def __init__(self):
        self.config_dir = os.path.expanduser('~/.config/dmx-visualizer-control')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.profiles_dir = os.path.join(self.config_dir, 'profiles')

        self._ensure_dirs()
        self._config = self._load_config()
        self._create_default_profiles()

    def _ensure_dirs(self):
        """Ensure config directories exist."""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.profiles_dir, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    return {**self.DEFAULT_CONFIG, **config}
            except (json.JSONDecodeError, IOError):
                pass
        return dict(self.DEFAULT_CONFIG)

    def _save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set a config value."""
        self._config[key] = value
        self._save_config()

    def get_all(self) -> Dict[str, Any]:
        """Get all config values."""
        return dict(self._config)

    # Gamepad Profiles

    def _create_default_profiles(self):
        """Create default gamepad profiles if they don't exist."""
        defaults = {
            'default': {
                'name': 'Default (Steam Deck)',
                'buttons': {
                    '0': 'select',
                    '1': 'back',
                    '2': 'refresh',
                    '3': 'context',
                    '4': 'prev_tab',
                    '5': 'next_tab',
                    '6': 'modifier',
                    '7': 'none',
                    '8': 'reset',
                    '9': 'save',
                    '12': 'nav_up',
                    '13': 'nav_down',
                    '14': 'nav_left',
                    '15': 'nav_right',
                },
                'analog': {
                    'deadzone': 0.2,
                    'sensitivity': 1.0,
                    'invert_y': False,
                },
            },
            'xbox': {
                'name': 'Xbox Controller',
                'buttons': {
                    '0': 'select',
                    '1': 'back',
                    '2': 'refresh',
                    '3': 'context',
                    '4': 'prev_tab',
                    '5': 'next_tab',
                    '6': 'modifier',
                    '7': 'none',
                    '8': 'reset',
                    '9': 'save',
                    '12': 'nav_up',
                    '13': 'nav_down',
                    '14': 'nav_left',
                    '15': 'nav_right',
                },
                'analog': {
                    'deadzone': 0.15,
                    'sensitivity': 1.0,
                    'invert_y': False,
                },
            },
            'playstation': {
                'name': 'PlayStation Controller',
                'buttons': {
                    '0': 'select',      # Cross
                    '1': 'back',        # Circle
                    '2': 'refresh',     # Square
                    '3': 'context',     # Triangle
                    '4': 'prev_tab',    # L1
                    '5': 'next_tab',    # R1
                    '6': 'modifier',    # L2
                    '7': 'none',        # R2
                    '8': 'reset',       # Share
                    '9': 'save',        # Options
                    '12': 'nav_up',
                    '13': 'nav_down',
                    '14': 'nav_left',
                    '15': 'nav_right',
                },
                'analog': {
                    'deadzone': 0.2,
                    'sensitivity': 1.0,
                    'invert_y': False,
                },
            },
        }

        for name, profile in defaults.items():
            profile_path = os.path.join(self.profiles_dir, f'{name}.json')
            if not os.path.exists(profile_path):
                with open(profile_path, 'w') as f:
                    json.dump(profile, f, indent=2)

    def get_profile_list(self) -> List[str]:
        """Get list of available profile names."""
        profiles = []
        for filename in os.listdir(self.profiles_dir):
            if filename.endswith('.json'):
                profiles.append(filename[:-5])
        return sorted(profiles)

    def get_gamepad_profile(self, name: str = None) -> Optional[Dict[str, Any]]:
        """Load a gamepad profile."""
        if name is None:
            name = self._config.get('active_profile', 'default')

        profile_path = os.path.join(self.profiles_dir, f'{name}.json')
        if os.path.exists(profile_path):
            try:
                with open(profile_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return None

    def save_gamepad_profile(self, name: str, profile: Dict[str, Any]):
        """Save a gamepad profile."""
        profile_path = os.path.join(self.profiles_dir, f'{name}.json')
        with open(profile_path, 'w') as f:
            json.dump(profile, f, indent=2)

    def delete_gamepad_profile(self, name: str) -> bool:
        """Delete a gamepad profile."""
        if name in ('default', 'xbox', 'playstation'):
            return False  # Don't delete built-in profiles

        profile_path = os.path.join(self.profiles_dir, f'{name}.json')
        if os.path.exists(profile_path):
            os.remove(profile_path)
            return True
        return False

    def set_active_profile(self, name: str):
        """Set the active gamepad profile."""
        self.set('active_profile', name)

    def get_active_profile(self) -> str:
        """Get the active profile name."""
        return self.get('active_profile', 'default')

    def export_profile(self, name: str, export_path: str) -> bool:
        """Export a profile to a file."""
        profile = self.get_gamepad_profile(name)
        if profile:
            with open(export_path, 'w') as f:
                json.dump(profile, f, indent=2)
            return True
        return False

    def import_profile(self, import_path: str, name: str) -> bool:
        """Import a profile from a file."""
        try:
            with open(import_path, 'r') as f:
                profile = json.load(f)
            profile['name'] = name
            self.save_gamepad_profile(name, profile)
            return True
        except (json.JSONDecodeError, IOError):
            return False

    # App Settings

    DEFAULT_APP_SETTINGS = {
        'server_url': 'http://localhost:8082',
        'auto_connect': True,
        'reconnect_interval': 10,
        'fullscreen': False,
        'always_on_top': False,
        'theme': 'retro',
        'scale_factor': 1.0,
        'gamepad_enabled': True,
        'vibration_enabled': True,
        'gamepad_poll_rate': 50,
        'debug_mode': False,
        'preview_quality': 'medium',
    }

    def get_app_settings(self) -> Dict[str, Any]:
        """Get all app settings."""
        settings = dict(self.DEFAULT_APP_SETTINGS)
        settings.update(self._config)
        return settings

    def save_app_settings(self, settings: Dict[str, Any]):
        """Save app settings."""
        self._config.update(settings)
        self._save_config()

    def reset_app_settings(self):
        """Reset app settings to defaults."""
        self._config = dict(self.DEFAULT_APP_SETTINGS)
        self._save_config()

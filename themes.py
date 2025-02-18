from typing import Dict
import random

class ThemeManager:
    # Base themes
    THEMES = {
        'default': {
            'S': 0xFF0000,  # Red
            'A': 0xFF6B00,  # Orange
            'B': 0x2ECC71,  # Green
            'C': 0x3498DB,  # Blue
            'D': 0x95A5A6   # Gray
        },
        'neon': {
            'S': 0xFF1493,  # Deep Pink
            'A': 0xFF69B4,  # Hot Pink
            'B': 0x00FF00,  # Lime
            'C': 0x00FFFF,  # Cyan
            'D': 0x9370DB   # Medium Purple
        },
        'pastel': {
            'S': 0xFFB6C1,  # Light Pink
            'A': 0xFFDAB9,  # Peach
            'B': 0x98FB98,  # Pale Green
            'C': 0x87CEEB,  # Sky Blue
            'D': 0xDDA0DD   # Plum
        }
    }
    
    # Dynamic type colors
    TYPE_COLORS = {
        'normal': 0xA8A878,
        'fire': 0xF08030,
        'water': 0x6890F0,
        'electric': 0xF8D030,
        'grass': 0x78C850,
        'ice': 0x98D8D8,
        'fighting': 0xC03028,
        'poison': 0xA040A0,
        'ground': 0xE0C068,
        'flying': 0xA890F0,
        'psychic': 0xF85888,
        'bug': 0xA8B820,
        'rock': 0xB8A038,
        'ghost': 0x705898,
        'dragon': 0x7038F8,
        'dark': 0x705848,
        'steel': 0xB8B8D0,
        'fairy': 0xEE99AC
    }

    @classmethod
    def get_theme_colors(cls, theme_name: str = 'default') -> Dict[str, int]:
        return cls.THEMES.get(theme_name, cls.THEMES['default'])

    @classmethod
    def get_type_color(cls, pokemon_type: str) -> int:
        return cls.TYPE_COLORS.get(pokemon_type.lower(), 0x000000)

    @classmethod
    def get_animated_transitions(cls) -> Dict[str, str]:
        return {
            'spawn': '⭐ → 💫 → ✨',
            'catch': '🎯 → 📦 → ✅',
            'shiny': '💫 → ✨ → 💫'
        }

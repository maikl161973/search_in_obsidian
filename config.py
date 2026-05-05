import json
import sys
from pathlib import Path
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """Загружает конфигурацию из файла"""

    config = {}

    config_file = Path('obsidian_search_config.json')
    if config_file.exists():
        try:
            # Предполагаем JSON файл конфигурации
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(
                f"Не удалось загрузить конфигурацию "
                f"из {config_file}: {e}", file=sys.stderr)
    
    return config

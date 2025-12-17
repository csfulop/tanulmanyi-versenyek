import yaml
import functools
import os

@functools.lru_cache(maxsize=1)
def get_config():
    """
    Loads and parses the config.yaml file.
    The configuration is cached to ensure it's loaded only once.
    """
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config.yaml')
    config_path = os.path.abspath(config_path)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"config.yaml not found at {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Basic validation
    required_top_level_keys = ['data_source', 'scraping', 'paths']
    for key in required_top_level_keys:
        if key not in config:
            raise ValueError(f"Missing required top-level key '{key}' in config.yaml")

    return config

if __name__ == "__main__":
    # Example usage and basic test
    try:
        cfg = get_config()
        print("Config loaded successfully:")
        print(yaml.dump(cfg, indent=2))
    except Exception as e:
        print(f"Error loading config: {e}")

from functools import cached_property
from pathlib import Path
import yaml

class Config:
    def __init__(self, config_dict):
        self.__dict__['_config_dict'] = config_dict

    def __getattr__(self, name):
        if name in self._config_dict:
            return self._config_dict[name]
        raise AttributeError(f"'Config' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in self._config_dict:
            self._config_dict[name] = value
        else:
            raise AttributeError(f"'Config' object has no attribute '{name}'")

    def __getitem__(self, key):
        return self._config_dict[key]

    def __setitem__(self, key, value):
        self._config_dict[key] = value

    def __repr__(self):
        return repr(self._config_dict)

class LittleConfig:
    def __init__(self, initial_path=None, config_path=None, config_name=None, overrides=None) -> None:
        self.initial_path = Path(initial_path) if initial_path else Path.cwd()
        self.config_path = Path(config_path) if config_path else Path.cwd()
        self.config_name = config_name
        self.overrides = overrides
        self._config = None

    def _load_yaml(self, yaml_path):
        with open(yaml_path, 'r') as file:
            return yaml.safe_load(file)

    def _load_defaults(self, config):
        if 'defaults' in config:
            for default in config['defaults']:
                for key, path in default.items():
                    full_path = Path(f'{self.config_path}/{key}/{path}.yaml')
                    config[key] = Config(self._load_yaml(full_path))
            del config['defaults']
        return config

    @cached_property
    def config(self):
        yaml_path = Path(f'{self.initial_path}/{self.config_name}.yaml')
        config_dict = self._load_yaml(yaml_path)
        config_dict = self._load_defaults(config_dict)
        if self.overrides:
            config_dict.update(self.overrides)
        self._config = Config(config_dict)
        return self._config
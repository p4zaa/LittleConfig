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
        self._config_dict[name] = value
        #if name in self._config_dict:
        #    self._config_dict[name] = value
        #else:
        #    raise AttributeError(f"'Config' object has no attribute '{name}'")

    def __getitem__(self, key):
        return self._config_dict.get(key, None)

    def __setitem__(self, key, value):
        self._config_dict[key] = value

    def __contains__(self, key):
        return key in self._config_dict

    def __delitem__(self, key):
        del self._config_dict[key]

    def __repr__(self):
        return repr(self._config_dict)

    def __iter__(self):
        return iter(self._config_dict.items())

    def items(self):
        return self._config_dict.items()

    def get(self, key, default=None):
        return self._config_dict.get(key, default)

    def update(self, other):
        if isinstance(other, dict):
            self._config_dict.update(other)
        elif isinstance(other, Config):
            self._config_dict.update(other._config_dict)
        else:
            raise ValueError("update() argument must be a dict or Config instance")

    def to_dict(self):
        pass

class LittleConfig:
    def __init__(self, initial_path=None, config_path=None, config_name=None, overrides=None) -> None:
        self.initial_path = Path(initial_path) if initial_path else Path.cwd()
        self.config_path = Path(config_path) if config_path else Path.cwd()
        self.config_name = config_name
        self.overrides = overrides
        self._config = None
        self._defaults_yaml = None
        self._original_defaults = None

    def _wrap_in_config(self, obj):
        if isinstance(obj, dict):
            return Config({k: self._wrap_in_config(v) for k, v in obj.items()})
        return obj

    def _load_yaml(self, yaml_path):
        with open(yaml_path, 'r') as file:
            return self._wrap_in_config(yaml.safe_load(file))

    def _load_defaults(self, config):
        if 'defaults' in config:
            self._original_defaults = config['defaults']
            for default in config['defaults']:
                for key, path in default.items():
                    if path:
                        full_path = Path(f'{self.config_path}/{key}/{path}.yaml')
                        loaded_yaml = self._load_yaml(full_path)
                        config[key] = Config(loaded_yaml) if isinstance(loaded_yaml, dict) else loaded_yaml
            #del config['defaults']
        return config

    def _apply_overrides(self, config, overrides):
        config.update(overrides)
        return config

    def _initialize_config(self, config):
        if self.overrides:
            config = self._apply_overrides(config, self.overrides)
        #if '_id_' not in config:
        #    config = self._apply_overrides(config, {'_id_': 'LITTLEBOBO'})
        return config

    @property
    def defaults_yaml(self):
        return self._original_defaults

    @defaults_yaml.setter
    def defaults_yaml(self, value):
        self._original_defaults = value

    @cached_property
    def config(self):
        yaml_path = Path(f'{self.initial_path}/{self.config_name}.yaml')
        config_dict = self._load_yaml(yaml_path)
        self.defaults_yaml = config_dict.get('defaults', None)
        config_dict = self._load_defaults(config_dict)
        config_dict = self._initialize_config(config_dict)
        self._config = Config(config_dict)
        return self._config

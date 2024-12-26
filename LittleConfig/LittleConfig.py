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
        return iter(self._config_dict)

    def items(self):
        return self._config_dict.items()

    def update(self, other):
        if isinstance(other, dict):
            self._config_dict.update(other)
        elif isinstance(other, Config):
            self._config_dict.update(other._config_dict)
        else:
            raise ValueError("update() argument must be a dict or Config instance")
        
    def recursive_update(self, other):
        """
        Recursively updates a dictionary with values from another dictionary.
        Nested dictionaries are updated rather than replaced.
        
        :param other: The dictionary with updates.
        :return: The updated dictionary.
        """
        for key, value in other.items():
            if isinstance(value, dict) and key in self._config_dict and isinstance(self._config_dict[key], dict):
                self.partial_update(self._config_dict[key], value)
            else:
                self._config_dict[key] = value
        return self._config_dict

    def to_dict(self):
        def unwrap(obj):
            if isinstance(obj, Config):
                return {k: unwrap(v) for k, v in obj.items()}
            return obj
        return unwrap(self._config_dict)

    def get(self, key, default=None):
        return self._config_dict.get(key, default)

class LittleConfig:
    def __init__(self, _dict: dict=None, initial_path=None, config_path=None, config_name=None, overrides=None, partial_overrides=None) -> None:
        self.initial_path = Path(initial_path) if initial_path else Path.cwd()
        self.config_path = Path(config_path) if config_path else Path.cwd()
        self.config_name = config_name
        self.overrides = overrides
        self.partial_overrides = partial_overrides
        self._config = _dict

        if self._config:
            self._config = self._wrap_in_config(self._config)

    def _wrap_in_config(self, obj):
        if isinstance(obj, dict):
            return Config({k: self._wrap_in_config(v) for k, v in obj.items()})
        return obj

    def _load_yaml(self, yaml_path):
        with open(yaml_path, 'r') as file:
            return self._wrap_in_config(yaml.safe_load(file))

    def _load_defaults(self, config):
        if 'defaults' in config:
            for default in config['defaults']:
                for key, path in default.items():
                    if path:
                        full_path = Path(f'{self.config_path}/{key}/{path}.yaml')
                        loaded_yaml = self._load_yaml(full_path)
                        config[key] = Config(loaded_yaml) if isinstance(loaded_yaml, dict) else loaded_yaml
            del config['defaults']
        return config

    def _apply_overrides(self, config, overrides):
        config.update(self._wrap_in_config(overrides))
        return config
    
    def _apply_partial_overrides(self, config, partial_overrides):
        for key, value in partial_overrides.items():
            if key in config:
                if isinstance(value, dict) and isinstance(config[key], Config):
                    self._apply_partial_overrides(config[key], value)
                else:
                    config[key] = self._wrap_in_config(value)
            else:
                config[key] = self._wrap_in_config(value)
        return config

    def _initialize_config(self, config):
        if self.overrides:
            config = self._apply_overrides(config, self.overrides)
        if self.partial_overrides:
            config = self._apply_partial_overrides(config, self.partial_overrides)
        return config

    @cached_property
    def config(self):
        if self._config is None:
            yaml_path = Path(f'{self.initial_path}/{self.config_name}.yaml')
            config_dict = self._load_yaml(yaml_path)
            config_dict = self._load_defaults(config_dict)
            config_dict = self._initialize_config(config_dict)
            self._config = Config(config_dict)
        return self._config
    
    def to_dict(self):
        return self.config.to_dict()
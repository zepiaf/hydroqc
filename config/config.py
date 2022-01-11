"""Config helper

This part of the code can probably be rewritten :)
"""

import yaml

class Element:
    """Used to create nested objects"""
    def __init__(self):
        pass

class Config:
    """returns a config object"""
    def __init__(self, config_file='config/config.yaml'):
        with open(config_file, 'r') as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
        for k, v in config.items():
            if isinstance(v,dict):
                setattr(self, k, Element())
                for sk, sv in v.items():
                    setattr(getattr(self,k), sk,sv)
            else:
                setattr(self, k, v)

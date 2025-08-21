# storage.py
import os
import configparser

def read_plugin_info(folder):
    path = os.path.join(folder, "plugin.info")
    if not os.path.exists(path):
        raise FileNotFoundError("plugin.info not found")
    cfg = configparser.ConfigParser()
    cfg.read(path)
    if "plugin" not in cfg:
        raise ValueError("Missing [plugin] section")
    return cfg, path

def write_plugin_info(cfg, path):
    with open(path, "w", encoding="utf-8") as f:
        cfg.write(f)

import os
import pkgutil
import importlib

from .base import BaseScraper

def load_scrapers():
    scrapers = []
    
    for loader, module_name, _ in pkgutil.iter_modules([os.path.dirname(__file__)]):
        if module_name not in ("__init__", "base", "loader"):
            module = importlib.import_module(f"{__package__}.{module_name}")
            
            for name, obj in vars(module).items():
                if isinstance(obj, type) and issubclass(obj, BaseScraper) and obj is not BaseScraper:
                    scrapers.append(obj)
    
    return scrapers
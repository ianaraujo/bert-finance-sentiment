import os
import pkgutil
import importlib

from scraper.base import BaseScraper

def load_scrapers():
    scrapers = []
    scraper_path = os.path.join(os.path.dirname(__file__), "..", "scraper", "src")
    
    for loader, module_name, _ in pkgutil.iter_modules([scraper_path]):
        if module_name not in ("__init__", "base", "loader"):
            module = importlib.import_module(f"scraper.src.{module_name}")
            
            for name, obj in vars(module).items():
                if isinstance(obj, type) and issubclass(obj, BaseScraper) and obj is not BaseScraper:
                    scrapers.append(obj)
    
    return scrapers
import pytest
import inspect
from datetime import datetime

from services.loader import load_scrapers
from main import DatabasePipeline

scrapers =  load_scrapers()

def is_valid_date_format(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    
class DummyPipeline(DatabasePipeline):
    def exists(self, gestora, title):
        # always pretend nothing exists in the DB yet
        return False

@pytest.fixture
def dummy_pipeline():
    return DummyPipeline()

@pytest.mark.parametrize("ScraperClass", scrapers)
def test_scraper_output_structure(ScraperClass, dummy_pipeline):
    """
    Test that each scraper's scrape() method returns a list of dicts with the correct structure.
    """
    scrape_signature = inspect.signature(ScraperClass.scrape)
    params = scrape_signature.parameters

    assert "limit" in params, (
        f"{ScraperClass.__name__}.scrape() must accept a 'limit' parameter."
    )

    assert params["limit"].default is not inspect._empty, (
        f"{ScraperClass.__name__}.scrape() should have a default value for 'limit'."
    )

    scraper = ScraperClass(pipeline=dummy_pipeline)
    response = scraper.scrape(limit=5)

    assert isinstance(response, list), f"{ScraperClass.__name__}.scrape() must return a list"
    assert response and len(response) <= 5, f"{ScraperClass.__name__} did not properly limit the results to 5 items."
        
    # check each item in the list
    for letter in response:
        # basic dict type check
        assert isinstance(letter, dict), f"Items in {ScraperClass.__name__}.scrape() must be dicts"
        
        # check standard keys (example: 'title', 'price', 'url')
        expected_keys = {"gestora", "title", "date", "url", "content"}
        
        for key in expected_keys:
            assert key in letter, f"Missing '{key}' key in {ScraperClass.__name__}.scrape() result"
        
        # optionally check value types
        assert isinstance(letter["gestora"], str), "gestora must be a string"
        assert isinstance(letter["title"], str), "title must be a string"
        assert isinstance(letter["url"], str), "url must be a string"
        assert isinstance(letter["date"], str) and is_valid_date_format(letter["date"]), "date must be a valid YYYY-MM-DD string"
        assert isinstance(letter["content"], str), "content must be a string"

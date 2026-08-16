"""Pytest configuration and fixtures for Flask Sudoku app."""
import pytest
import app as app_module


@pytest.fixture
def app():
    """Create and configure a Flask app for testing.
    
    Sets testing mode to disable error catching during request handling,
    so you get better error reports when handling request errors.
    """
    flask_app = app_module.app
    flask_app.config['TESTING'] = True
    
    yield flask_app
    
    # Cleanup: reset CURRENT state after each test
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None


@pytest.fixture
def client(app):
    """Provide a Flask test client for making requests.
    
    The client is used to make requests to the app without running
    a live server. It returns response objects that can be inspected.
    """
    return app.test_client()


@pytest.fixture
def reset_game():
    """Reset game state before each test.
    
    Yields control to test, then cleans up CURRENT state.
    This is a cleanup fixture used in tests that need a fresh state.
    """
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None
    
    yield
    
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None

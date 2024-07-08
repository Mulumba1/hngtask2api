import sys
import os
import pytest
from pkg import create_app, db

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
         "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
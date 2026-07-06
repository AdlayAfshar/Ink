from backend.app.core.database import Base, SessionLocal, get_db


def test_database_module_loads():
    assert Base is not None
    assert SessionLocal is not None
    assert callable(get_db)
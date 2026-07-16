from backend.app.core.database import Base, SessionLocal, get_db
from backend.app.modules.auth.models import User

def test_database_module_loads():
    assert Base is not None
    assert SessionLocal is not None
    assert callable(get_db)


def test_user_table_name():
    assert User.__tablename__ == "users"


def test_user_table_has_expected_columns():
    columns = User.__table__.columns

    assert "id" in columns
    assert "email" in columns
    assert "hashed_password" in columns
    assert "created_at" in columns
    assert "updated_at" in columns
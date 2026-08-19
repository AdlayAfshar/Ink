from backend.app.modules.glossary.models import UserWord, UserWordNote


def test_user_word_table_name():
    assert UserWord.__tablename__ == "user_words"


def test_user_word_has_expected_columns():
    columns = UserWord.__table__.columns

    assert "id" in columns
    assert "user_id" in columns
    assert "word_id" in columns
    assert "learning_status" in columns
    assert "saved_at" in columns
    assert "last_reviewed_at" in columns
    assert "next_review_at" in columns


def test_user_word_note_table_name():
    assert UserWordNote.__tablename__ == "user_word_notes"


def test_user_word_note_has_expected_columns():
    columns = UserWordNote.__table__.columns

    assert "id" in columns
    assert "user_word_id" in columns
    assert "note" in columns
    assert "created_at" in columns


def test_user_word_has_unique_user_word_constraint():
    constraints = UserWord.__table__.constraints

    constraint_names = {constraint.name for constraint in constraints}

    assert "uq_user_words_user_id_word_id" in constraint_names


def test_user_word_note_references_user_words():
    foreign_keys = UserWordNote.__table__.c.user_word_id.foreign_keys

    targets = {foreign_key.target_fullname for foreign_key in foreign_keys}

    assert "user_words.id" in targets
from backend.app.modules.dictionary.models import (
    Word,
    WordDefinition,
    WordExample,
    WordSynonym,
)


def test_dictionary_table_names():
    assert Word.__tablename__ == "words"
    assert WordDefinition.__tablename__ == "word_definitions"
    assert WordExample.__tablename__ == "word_examples"
    assert WordSynonym.__tablename__ == "word_synonyms"


def test_word_has_expected_columns():
    columns = Word.__table__.columns

    assert "id" in columns
    assert "text" in columns
    assert "language" in columns
    assert "provider" in columns
    assert "provider_lookup_key" in columns


def test_dictionary_child_tables_have_word_id():
    assert "word_id" in WordDefinition.__table__.columns
    assert "word_id" in WordExample.__table__.columns
    assert "word_id" in WordSynonym.__table__.columns
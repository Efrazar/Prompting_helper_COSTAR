# tests/test_database.py
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.database import Database
from models.prompt import PromptTemplate


@pytest.fixture
def db(tmp_path):
    """Create a temporary database for each test — auto-cleaned by pytest."""
    db_file = tmp_path / "test.db"
    return Database(str(db_file))


@pytest.fixture
def sample_prompt():
    """Reusable sample prompt object."""
    return PromptTemplate(
        title="Test Prompt",
        role="Software Developer",
        context="Building a Python application",
        objective="Test database functionality",
        style="Technical",
        tone="Professional",
        audience="Developers",
        response_format="Code examples",
        start_analysis="Begin with setup instructions",
        tags="test,development"
    )


def test_save_and_retrieve_prompt(db, sample_prompt):
    prompt_id = db.save_prompt(sample_prompt)
    assert prompt_id is not None
    retrieved = db.get_prompt(prompt_id)
    assert retrieved.title == "Test Prompt"
    assert retrieved.role == "Software Developer"


def test_search_prompts(db, sample_prompt):
    db.save_prompt(sample_prompt)
    results = db.search_prompts("Python")
    assert len(results) >= 1


def test_update_prompt(db, sample_prompt):
    prompt_id = db.save_prompt(sample_prompt)
    db.update_prompt(prompt_id, title="Updated Title")
    updated = db.get_prompt(prompt_id)
    assert updated.title == "Updated Title"


def test_toggle_favorite(db, sample_prompt):
    prompt_id = db.save_prompt(sample_prompt)
    is_fav = db.toggle_favorite(prompt_id)
    assert is_fav is True
    is_fav_again = db.toggle_favorite(prompt_id)
    assert is_fav_again is False


def test_increment_usage(db, sample_prompt):
    prompt_id = db.save_prompt(sample_prompt)
    db.increment_usage(prompt_id)
    used = db.get_prompt(prompt_id)
    assert used.usage_count == 1


def test_delete_prompt(db, sample_prompt):
    prompt_id = db.save_prompt(sample_prompt)
    db.delete_prompt(prompt_id)
    deleted = db.get_prompt(prompt_id)
    assert deleted is None


def test_get_statistics(db, sample_prompt):
    db.save_prompt(sample_prompt)
    stats = db.get_statistics()
    assert "total_prompts" in stats
    assert stats["total_prompts"] >= 1


def test_export_import_json(db, sample_prompt, tmp_path):
    db.save_prompt(sample_prompt)
    export_file = str(tmp_path / "export.json")
    result = db.export_to_json(export_file)
    assert result is True
    assert os.path.exists(export_file)


def test_get_templates(db):
    """Sample templates are auto-created on first init."""
    templates = db.get_templates()
    assert len(templates) >= 1
    assert all(t.is_template for t in templates)

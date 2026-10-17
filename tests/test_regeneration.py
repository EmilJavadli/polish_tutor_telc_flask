"""Offline regression tests using synthetic lessons and a real SQLite database.

Only unavailable authentication/placement modules and paid API calls are stubbed.
The repository methods and Flask routes under test are executed, not mocked.
"""

import importlib
import sys
import types
import uuid
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from agent import lesson_generator as generator
from agent import llm
from agent.prompts import fill
from agent.schemas import Lesson, Practice
from database.models import (
    Base,
    LessonAttempt,
    LessonProgress,
    LessonRecord,
    User,
    UserProfile,
)
from flask import Blueprint
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
from repositories.lesson_repository import LessonRepository, RegenerationConflict
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import sessionmaker


def sample_lesson(day=29, title="Original", text="To jest lekcja."):
    return Lesson(
        day=day,
        title_pl=title,
        title_en=title,
        reading_pl=text,
        reading_en="This is a lesson.",
        new_vocabulary=[],
        grammar_rules=[],
        listening={
            "type": "dialogue",
            "situation_en": "Practice",
            "lines": [],
            "tasks": [],
        },
        exercises=[],
        writing_tasks=[],
        speaking={
            "part": 1,
            "title": "Practice",
            "instructions_pl": "Mow",
            "instructions_en": "Speak",
            "prompts": [],
        },
        quiz=[],
    )


@pytest.fixture
def repository(tmp_path):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    sf = sessionmaker(bind=engine, expire_on_commit=False)
    uid = uuid.uuid4()
    with sf.begin() as session:
        session.add(
            User(id=uid, provider="test", issuer="test", provider_subject=str(uid))
        )
        session.add(UserProfile(user_id=uid))
    repo = LessonRepository(sf, uid, tmp_path)
    repo.save_lesson(sample_lesson())
    with sf.begin() as session:
        record = session.scalar(select(LessonRecord))
        record.status = "completed"
        record.completed_at = datetime.now(timezone.utc)
        session.add(
            LessonAttempt(
                user_id=uid,
                lesson_id=record.id,
                attempt_type="quiz",
                attempt_number=1,
                payload={"kept": True},
            )
        )
        session.add(
            LessonProgress(user_id=uid, lesson_id=record.id, state={"kept": True})
        )
    return repo, sf, engine


def snapshot(sf):
    with sf() as session:
        record = session.scalar(select(LessonRecord))
        return (
            record.lesson_json,
            record.status,
            record.completed_at,
            session.scalar(select(func.count()).select_from(LessonAttempt)),
            session.scalar(select(func.count()).select_from(LessonProgress)),
        )


def test_success_resets_attempts_and_progress(repository):
    repo, sf, _ = repository
    old = repo.load_lesson(29).model_dump(mode="json")
    repo.replace_lesson(sample_lesson(title="Replacement"), expected=old)
    state = snapshot(sf)
    assert state[0]["title_pl"] == "Replacement"
    assert state[1:] == ("ready", None, 0, 0)


def test_database_failure_rolls_back_deletes_and_content(repository):
    repo, sf, engine = repository
    before = snapshot(sf)

    def fail_update(conn, cursor, statement, parameters, context, executemany):
        if statement.startswith("UPDATE lessons"):
            raise RuntimeError("Injected database failure")

    event.listen(engine, "before_cursor_execute", fail_update)
    try:
        with pytest.raises(RuntimeError):
            repo.replace_lesson(sample_lesson(title="Replacement"))
    finally:
        event.remove(engine, "before_cursor_execute", fail_update)
    assert snapshot(sf) == before


def test_conflicting_replacement_preserves_data(repository):
    repo, sf, _ = repository
    before = snapshot(sf)
    with pytest.raises(RegenerationConflict):
        repo.replace_lesson(sample_lesson(), expected={"stale": True})
    assert snapshot(sf) == before


def test_audio_cache_changes_with_content(repository):
    repo, _, _ = repository
    old = repo.audio_path(29, "reading_normal")
    repo.replace_lesson(sample_lesson(text="Nowa lekcja."))
    assert old != repo.audio_path(29, "reading_normal")


def test_legacy_audio_cleanup_failure_does_not_undo_save(repository, monkeypatch):
    repo, _, _ = repository
    monkeypatch.setattr(Path, "unlink", Mock(side_effect=PermissionError("denied")))
    assert repo.replace_lesson(sample_lesson(title="Saved"))
    assert repo.load_lesson(29).title_pl == "Saved"


@pytest.mark.parametrize("kind", ["../private", "unknown", "reading"])
def test_invalid_audio_kind_rejected(repository, kind):
    with pytest.raises(ValueError):
        repository[0].audio_path(29, kind)


@pytest.mark.parametrize("index", [-1, 2, 999])
def test_invalid_choice_index_is_reported_not_indexed(index):
    practice = Practice(
        exercises=[
            {
                "id": 1,
                "section": "grammar",
                "type": "choice",
                "prompt": "Test",
                "options": ["a", "b"],
                "correct_option": index,
                "explanation_en": "a",
            }
        ],
        writing_tasks=[],
        speaking={
            "part": 1,
            "title": "Test",
            "instructions_pl": "Test",
            "instructions_en": "Test",
            "prompts": [],
        },
        quiz=[],
    )
    problems = generator.validate_practice(practice, SimpleNamespace(speaking_part=1))
    assert any("invalid correct_option" in item for item in problems)


def test_repair_retries_do_not_mutate_callers_messages(monkeypatch):
    class Output(BaseModel):
        value: int

    messages = [{"role": "user", "content": "Return JSON"}]
    monkeypatch.setattr(
        generator, "chat_json", Mock(side_effect=[{"value": "bad"}, {"value": 1}])
    )
    assert generator._generate(messages, Output, lambda _: [], "test").value == 1
    assert len(messages) == 1


def test_incomplete_provider_response_can_be_repaired(monkeypatch):
    class Output(BaseModel):
        value: int

    monkeypatch.setattr(
        generator,
        "chat_json",
        Mock(side_effect=[llm.LLMResponseError("empty"), {"value": 1}]),
    )
    assert generator._generate([], Output, lambda _: [], "test").value == 1


def test_fill_supports_both_placeholder_formats():
    assert fill("<<day>> &lt;&lt;day&gt;&gt; {json}", day=29) == "29 29 {json}"


@pytest.fixture
def web(monkeypatch):
    # These project modules were not uploaded. Stubs are test-only.
    auth = types.ModuleType("auth.google_oidc")
    auth.bp = Blueprint("auth", __name__)
    auth.bp.add_url_rule("/login", "login", lambda: "login")
    auth.init_oauth = lambda app: None
    auth.identity_from_session = lambda: object()
    monkeypatch.setitem(sys.modules, "auth.google_oidc", auth)
    bank = types.ModuleType("placement.test_bank")
    for name in (
        "GRAMMAR_VOCAB",
        "READING",
        "LISTENING",
        "READING_TEXT",
        "LISTENING_TEXT",
    ):
        setattr(bank, name, [])
    monkeypatch.setitem(sys.modules, "placement.test_bank", bank)
    scoring = types.ModuleType("placement.scoring")
    scoring.objective_profile = scoring.classify = lambda *a: {}
    monkeypatch.setitem(sys.modules, "placement.scoring", scoring)
    grader = types.ModuleType("placement.grader")
    grader.grade_productive = lambda *a: {}
    monkeypatch.setitem(sys.modules, "placement.grader", grader)
    sys.modules.pop("app", None)
    module = importlib.import_module("app")
    module.app.config.update(TESTING=True, SECRET_KEY="test-only")
    yield module, module.app.test_client()
    sys.modules.pop("app", None)


def test_regeneration_route_success(web, repository, monkeypatch):
    module, client = web
    repo, sf, _ = repository
    monkeypatch.setattr(module, "repos", lambda: (None, None, repo, None))
    monkeypatch.setattr(
        module, "generate_lesson", lambda *a, **k: sample_lesson(title="New")
    )
    response = client.post("/api/lesson/29/regenerate")
    assert response.status_code == 200
    assert response.json["ok"] is True
    assert snapshot(sf)[3:] == (0, 0)


def test_generation_failure_preserves_existing_work(web, repository, monkeypatch):
    module, client = web
    repo, sf, _ = repository
    before = snapshot(sf)
    monkeypatch.setattr(module, "repos", lambda: (None, None, repo, None))
    monkeypatch.setattr(
        module, "generate_lesson", Mock(side_effect=RuntimeError("private details"))
    )
    response = client.post("/api/lesson/29/regenerate")
    assert response.status_code == 500 and response.is_json
    assert response.json["reference"]
    assert "private details" not in response.text
    assert snapshot(sf) == before


def test_repository_initialization_failure_returns_json(web, monkeypatch):
    module, client = web
    monkeypatch.setattr(
        module, "repos", Mock(side_effect=RuntimeError("connection failed"))
    )
    response = client.post("/api/lesson/29/regenerate")
    assert response.status_code == 500 and response.is_json


def test_expired_api_session_returns_401_json(web, monkeypatch):
    module, client = web
    monkeypatch.setattr(module, "identity_from_session", lambda: None)
    response = client.post("/api/lesson/29/regenerate")
    assert response.status_code == 401 and response.is_json


@pytest.mark.parametrize("day", [0, 274])
def test_invalid_day_returns_400(web, day):
    response = web[1].post(f"/api/lesson/{day}/regenerate")
    assert response.status_code == 400


def test_missing_lesson_returns_404(web, repository, monkeypatch):
    module, client = web
    monkeypatch.setattr(module, "repos", lambda: (None, None, repository[0], None))
    assert client.post("/api/lesson/30/regenerate").status_code == 404


def test_templates_parse_and_button_is_below_panel():
    root = Path(__file__).resolve().parents[1]
    env = Environment(loader=FileSystemLoader(root / "templates"))
    for path in (root / "templates").glob("*.html"):
        env.parse(path.read_text())
    html = (root / "templates/lesson.html").read_text()
    assert html.index('id="lessonPanel"') < html.index('id="lessonSettingsButton"')
    assert html.count('id="lessonSettingsButton"') == 1

"""User-scoped replacement for the old shared file repository."""

import datetime as dt
import hashlib
import json
import logging
import uuid
from pathlib import Path

from agent.schemas import (
    ExerciseAttempt,
    Lesson,
    ListeningAttempt,
    QuizAttempt,
    ReadingAttempt,
    SpeakingAttempt,
    WritingAttempt,
)
from database.models import LessonAttempt, LessonProgress, LessonRecord, UserProfile
from sqlalchemy import delete, func, select

KINDS = {
    "reading": ReadingAttempt,
    "quiz": QuizAttempt,
    "exercises": ExerciseAttempt,
    "listening": ListeningAttempt,
    "writing": WritingAttempt,
    "speaking": SpeakingAttempt,
}


class RegenerationConflict(RuntimeError):
    """The lesson changed while a replacement was being generated."""


class LessonRepository:
    def __init__(self, sf, user_id, audio_root=Path("data/audio")):
        self.sf = sf
        self.user_id = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        self.audio_dir = Path(audio_root) / str(self.user_id)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    @property
    def current_day(self):
        with self.sf() as s:
            return s.get(UserProfile, self.user_id).current_plan_position

    @current_day.setter
    def current_day(self, v):
        with self.sf() as s:
            p = s.get(UserProfile, self.user_id)
            p.current_plan_position = int(v)
            s.commit()

    def _record(self, s, day):
        return s.scalar(
            select(LessonRecord).where(
                LessonRecord.user_id == self.user_id, LessonRecord.curriculum_day == day
            )
        )

    def save_lesson(self, l):
        with self.sf() as s:
            x = self._record(s, l.day)
            if x:
                x.lesson_json = l.model_dump()
                x.status = "ready"
            else:
                s.add(
                    LessonRecord(
                        user_id=self.user_id,
                        curriculum_day=l.day,
                        lesson_json=l.model_dump(),
                    )
                )
            s.commit()

    def load_lesson(self, day):
        with self.sf() as s:
            x = self._record(s, day)
            return Lesson.model_validate(x.lesson_json) if x else None

    def lesson_days(self):
        with self.sf() as s:
            return list(
                s.scalars(
                    select(LessonRecord.curriculum_day)
                    .where(LessonRecord.user_id == self.user_id)
                    .order_by(LessonRecord.curriculum_day)
                )
            )

    def _lessons(self):
        return [x for d in self.lesson_days() if (x := self.load_lesson(d))]

    def taught_words(self, exclude_day=None):
        return [
            v.polish
            for l in self._lessons()
            if l.day != exclude_day and l.lesson_type == "lesson"
            for v in l.new_vocabulary
        ]

    def week_words(self, week, exclude_day=None):
        return [
            v.polish
            for l in self._lessons()
            if l.day != exclude_day and l.week == week and l.lesson_type == "lesson"
            for v in l.new_vocabulary
        ]

    def _lesson_id(self, s, day):
        x = self._record(s, day)
        return x.id if x else None

    def add_attempt(self, day, kind, attempt):
        with self.sf() as s:
            lid = self._lesson_id(s, day)
            assert lid
            n = (
                s.scalar(
                    select(func.count())
                    .select_from(LessonAttempt)
                    .where(
                        LessonAttempt.user_id == self.user_id,
                        LessonAttempt.lesson_id == lid,
                        LessonAttempt.attempt_type == kind,
                    )
                )
                + 1
            )
            s.add(
                LessonAttempt(
                    user_id=self.user_id,
                    lesson_id=lid,
                    attempt_type=kind,
                    attempt_number=n,
                    score=getattr(attempt, "score", None),
                    passed=getattr(attempt, "passed", None),
                    payload=attempt.model_dump(),
                )
            )
            s.commit()

    def attempts(self, day, kind):
        with self.sf() as s:
            lid = self._lesson_id(s, day)
            if not lid:
                return []
            rows = s.scalars(
                select(LessonAttempt)
                .where(
                    LessonAttempt.user_id == self.user_id,
                    LessonAttempt.lesson_id == lid,
                    LessonAttempt.attempt_type == kind,
                )
                .order_by(LessonAttempt.attempt_number)
            ).all()
            return [KINDS[kind].model_validate(x.payload) for x in rows]

    def checklist(self, day):
        return {
            **{
                k: bool(self.attempts(day, k))
                for k in ("exercises", "writing", "speaking")
            },
            "quiz": any(x.passed for x in self.attempts(day, "quiz")),
        }

    def summary(self, day):
        """Return lesson completion and latest scores for the Summary tab."""
        reading = self.attempts(day, "reading")
        listening = self.attempts(day, "listening")
        exercises = self.attempts(day, "exercises")
        writing = self.attempts(day, "writing")
        speaking = self.attempts(day, "speaking")
        quiz = self.attempts(day, "quiz")
        return {
            "completed": self.is_completed(day),
            "checklist": {
                "reading": bool(reading),
                "listening": bool(listening),
                "vocabulary": True,
                "grammar": True,
                "exercises": bool(exercises),
                "writing": bool(writing),
                "speaking": bool(speaking),
                "quiz": any(x.passed for x in quiz),
            },
            "scores": {
                "reading": round(reading[-1].score * 100) if reading else None,
                "listening": round(listening[-1].score * 100) if listening else None,
                "exercises": round(exercises[-1].score * 100) if exercises else None,
                "quiz": round(quiz[-1].score * 100) if quiz else None,
            },
        }

    def update_completion(self, day, today=None):
        if not all(self.checklist(day).values()):
            return False
        with self.sf() as s:
            x = self._record(s, day)
            x.status = "completed"
            x.completed_at = dt.datetime.now(dt.timezone.utc)
            s.commit()
            return True

    def is_completed(self, day):
        with self.sf() as s:
            x = self._record(s, day)
            return bool(x and x.status == "completed")

    def reset_day(self, day):
        with self.sf() as s:
            lid = self._lesson_id(s, day)
            if lid:
                s.query(LessonAttempt).filter(
                    LessonAttempt.user_id == self.user_id,
                    LessonAttempt.lesson_id == lid,
                ).delete()
                x = self._record(s, day)
                x.status = "ready"
                x.completed_at = None
                s.commit()

    def replace_lesson(self, lesson, *, expected=None):
        """Replace a lesson and reset its attempts in one database transaction.

        Generation happens before this method. Any database error rolls back
        content, attempts, progress, and completion together. Audio is keyed by
        content, so failed cleanup cannot serve the previous lesson's recording.
        """
        content = lesson.model_dump(mode="json")
        with self.sf() as session:
            with session.begin():
                record = session.scalar(
                    select(LessonRecord)
                    .where(
                        LessonRecord.user_id == self.user_id,
                        LessonRecord.curriculum_day == lesson.day,
                    )
                    .with_for_update()
                )
                if record is None:
                    raise ValueError("Lesson not found.")
                if expected is not None and record.lesson_json != expected:
                    raise RegenerationConflict("Lesson changed during generation.")
                for model in (LessonAttempt, LessonProgress):
                    session.execute(
                        delete(model).where(
                            model.user_id == self.user_id,
                            model.lesson_id == record.id,
                        )
                    )
                record.lesson_json = content
                record.status = "ready"
                record.completed_at = None
        # Do not delete newly generated content-keyed audio from concurrent reads.
        warnings = []
        for kind in ("reading_normal", "reading_slow", "listening"):
            path = self.audio_dir / f"day_{lesson.day:03d}_{kind}.mp3"
            try:
                path.unlink(missing_ok=True)
            except OSError:
                logging.getLogger(__name__).exception("Legacy audio cleanup failed")
                warnings.append("Some old audio files could not be removed.")
        return warnings

    def prepare_regeneration(self, day):
        """Deprecated: use replace_lesson to avoid destructive partial saves."""
        raise RuntimeError("Use replace_lesson(new_lesson) for atomic regeneration.")

    def audio_path(self, day, kind):
        if kind not in {"reading_normal", "reading_slow", "listening"}:
            raise ValueError("Unsupported audio kind.")
        lesson = self.load_lesson(day)
        if lesson is None:
            raise ValueError("Lesson not found.")
        content = (
            lesson.listening.model_dump(mode="json")
            if kind == "listening"
            else lesson.reading_pl
        )
        digest = hashlib.sha256(
            json.dumps(content, ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest()[:16]
        return self.audio_dir / f"day_{day:03d}_{kind}_{digest}.mp3"

    def delete_audio(self, day):
        for p in self.audio_dir.glob(f"day_{day:03d}_*.mp3"):
            p.unlink(missing_ok=True)

    def save_recording(self, day, audio, suffix="wav"):
        p = (
            self.audio_dir
            / f"day_{day:03d}_recording_{dt.datetime.now().timestamp()}.{suffix}"
        )
        p.write_bytes(audio)
        return p.name

    def recording_path(self, name):
        return self.audio_dir / name

    def get_progress(self, day):
        with self.sf() as s:
            lid = self._lesson_id(s, day)
            x = s.scalar(
                select(LessonProgress).where(
                    LessonProgress.user_id == self.user_id,
                    LessonProgress.lesson_id == lid,
                )
            )
            return dict(x.state) if x else {}

    def save_progress(self, day, state):
        with self.sf() as s:
            lid = self._lesson_id(s, day)
            x = s.scalar(
                select(LessonProgress).where(
                    LessonProgress.user_id == self.user_id,
                    LessonProgress.lesson_id == lid,
                )
            )
            if x:
                x.state = state
                x.updated_at = dt.datetime.now(dt.timezone.utc)
            else:
                s.add(LessonProgress(user_id=self.user_id, lesson_id=lid, state=state))
            s.commit()

    def stats(self, today):
        lessons = self._lessons()
        done = [l for l in lessons if self.is_completed(l.day)]
        return {
            "lessons": len(done),
            "words": sum(
                len(l.new_vocabulary) for l in done if l.lesson_type == "lesson"
            ),
            "grammar": len({g.id for l in done for g in l.grammar_rules}),
            "streak": 0,
        }

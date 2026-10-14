"""Deterministic graders for lesson activities."""

from __future__ import annotations

from datetime import datetime, timezone

from agent.schemas import (
    ExerciseAttempt,
    ListeningAttempt,
    QuizAttempt,
    ReadingAttempt,
)


def _timestamp() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def grade_reading(
    tasks: list,
    answers: dict[str, str | int],
) -> ReadingAttempt:
    """Grade reading questions and preserve evidence-based feedback."""
    results: dict[str, dict] = {}
    correct_count = 0

    for question in tasks:
        question_id = str(question.id)
        selected = answers.get(question_id)
        is_correct = str(selected) == str(question.correct_option)

        correct_count += int(is_correct)
        results[question_id] = {
            "correct": is_correct,
            "correct_option": question.correct_option,
            "evidence": question.evidence,
            "explanation": question.explanation,
        }

    score = correct_count / max(1, len(tasks))

    return ReadingAttempt(
        answers={str(key): str(value) for key, value in answers.items()},
        score=score,
        feedback=results,
        timestamp=_timestamp(),
    )


def grade_listening(
    tasks: list,
    answers: dict[str, str | int],
) -> ListeningAttempt:
    """Grade objective listening questions."""
    correct: dict[str, bool] = {}

    for question in tasks:
        question_id = str(question.id)
        correct[question_id] = (
            str(answers.get(question_id, ""))
            == str(question.correct_option)
        )

    score = sum(correct.values()) / max(1, len(tasks))

    return ListeningAttempt(
        answers={str(key): str(value) for key, value in answers.items()},
        score=score,
        correct=correct,
    )


def grade_exercises(
    items: list,
    answers: dict[str, str | int],
) -> ExerciseAttempt:
    """Grade vocabulary, grammar, and language-element exercises."""
    correct: dict[str, bool] = {}

    for exercise in items:
        exercise_id = str(exercise.id)
        answer = str(answers.get(exercise_id, "")).strip()

        if exercise.type == "choice":
            is_correct = answer == str(exercise.correct_option)
        else:
            accepted = {
                candidate.strip().casefold()
                for candidate in exercise.accepted_answers
            }
            is_correct = answer.casefold() in accepted

        correct[exercise_id] = is_correct

    score = sum(correct.values()) / max(1, len(items))

    return ExerciseAttempt(
        answers={str(key): str(value) for key, value in answers.items()},
        score=score,
        correct=correct,
    )


def grade_quiz(
    items: list,
    answers: dict[str, str | int],
    pass_score: float = 0.8,
) -> QuizAttempt:
    """Grade deterministic quiz questions.

    Open questions receive completion credit here. AI grading for open
    questions can be layered on separately without changing persistence.
    """
    results = []
    total_score = 0.0

    for question in items:
        question_id = str(question.id)
        answer = str(answers.get(question_id, "")).strip()

        if question.type == "multiple_choice":
            score = float(answer == str(question.correct_option))
        elif question.type == "fill_blank":
            accepted = {
                candidate.strip().casefold()
                for candidate in question.accepted_answers
            }
            score = float(answer.casefold() in accepted)
        else:
            score = float(bool(answer))

        total_score += score
        results.append(
            {
                "id": question.id,
                "score": score,
                "feedback": "",
            }
        )

    score = total_score / max(1, len(items))

    return QuizAttempt(
        attempt=1,
        score=score,
        passed=score >= pass_score,
        answers={str(key): str(value) for key, value in answers.items()},
        results=results,
    )

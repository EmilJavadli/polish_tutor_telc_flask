"""Graders for lesson activities.

Objective tasks are graded deterministically. Writing and speaking use the
existing OpenAI JSON client with level-aware production criteria.
"""

from __future__ import annotations

from datetime import datetime, timezone

from agent.llm import chat_json
from agent.prompts import (
    PRODUCTION_CRITERIA,
    PRODUCTION_GRADER_SYSTEM,
    SPEAKING_EXTRA,
    fill,
)
from agent.schemas import (
    Criterion,
    ExerciseAttempt,
    ListeningAttempt,
    Mistake,
    ProductionFeedback,
    QuestionResult,
    QuizAttempt,
    ReadingAttempt,
)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalized_answers(answers: dict) -> dict[str, str]:
    return {str(key): str(value) for key, value in answers.items()}


def grade_reading(tasks: list, answers: dict) -> ReadingAttempt:
    """Grade Reading questions and retain evidence-backed feedback."""
    feedback: dict[str, dict] = {}
    correct_count = 0

    for question in tasks:
        question_id = str(question.id)
        selected = answers.get(question_id)
        is_correct = str(selected) == str(question.correct_option)
        correct_count += int(is_correct)

        feedback[question_id] = {
            "correct": is_correct,
            "correct_option": question.correct_option,
            "evidence": question.evidence,
            "explanation": question.explanation,
        }

    return ReadingAttempt(
        answers=_normalized_answers(answers),
        score=correct_count / max(1, len(tasks)),
        feedback=feedback,
        timestamp=_timestamp(),
    )


def grade_listening(tasks: list, answers: dict) -> ListeningAttempt:
    """Grade objective Listening questions."""
    correct = {
        str(question.id): (
            str(answers.get(str(question.id), ""))
            == str(question.correct_option)
        )
        for question in tasks
    }

    return ListeningAttempt(
        answers=_normalized_answers(answers),
        score=sum(correct.values()) / max(1, len(tasks)),
        correct=correct,
    )


def grade_exercises(items: list, answers: dict) -> ExerciseAttempt:
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

    return ExerciseAttempt(
        answers=_normalized_answers(answers),
        score=sum(correct.values()) / max(1, len(items)),
        correct=correct,
    )


def grade_quiz(
    items: list,
    answers: dict,
    pass_score: float = 0.8,
) -> QuizAttempt:
    """Grade quiz items while preserving the original QuizAttempt schema."""
    results: list[QuestionResult] = []
    total_score = 0.0

    for question in items:
        question_id = str(question.id)
        answer = str(answers.get(question_id, "")).strip()

        if question.type == "multiple_choice":
            item_score = float(answer == str(question.correct_option))
        elif question.type == "fill_blank":
            accepted = {
                candidate.strip().casefold()
                for candidate in question.accepted_answers
            }
            item_score = float(answer.casefold() in accepted)
        else:
            # Open questions need separate semantic grading. Keep the existing
            # app behavior: a non-empty response receives completion credit.
            item_score = float(bool(answer))

        total_score += item_score
        results.append(
            QuestionResult(
                id=question.id,
                score=item_score,
                feedback="",
            )
        )

    score = total_score / max(1, len(items))

    return QuizAttempt(
        attempt=1,
        score=score,
        passed=score >= pass_score,
        answers=_normalized_answers(answers),
        results=results,
    )


def _grade_production(
    kind: str,
    text: str,
    level: str,
) -> ProductionFeedback:
    """Grade Writing or Speaking with the restored production prompt."""
    extra = SPEAKING_EXTRA if kind == "speaking" else ""
    criteria = PRODUCTION_CRITERIA[kind]

    system_prompt = fill(
        PRODUCTION_GRADER_SYSTEM,
        kind=kind,
        level=level,
        criteria=", ".join(criteria),
        extra=extra,
    )

    response = chat_json(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ]
    )

    returned_criteria = response.get("criteria", [])
    normalized_criteria = []

    for expected_name in criteria:
        matching = next(
            (
                item
                for item in returned_criteria
                if item.get("name") == expected_name
            ),
            None,
        )

        if matching is None:
            normalized_criteria.append(
                Criterion(
                    name=expected_name,
                    score=0,
                    comment="No assessment returned for this criterion.",
                )
            )
            continue

        normalized_criteria.append(
            Criterion(
                name=expected_name,
                score=int(max(0, min(5, matching.get("score", 0)))),
                comment=str(matching.get("comment", "")),
            )
        )

    mistakes = [
        Mistake.model_validate(item)
        for item in response.get("mistakes", [])
    ]

    return ProductionFeedback(
        criteria=normalized_criteria,
        corrected_text=str(response.get("corrected_text", "")),
        mistakes=mistakes,
        feedback=str(response.get("feedback", "")),
    )


def grade_writing(task, text: str, level: str) -> ProductionFeedback:
    """Grade a lesson Writing response at the learner's current level."""
    task_context = (
        f"Situation: {task.situation_pl}\n"
        f"Required points: {'; '.join(task.points_pl)}\n\n"
        f"Learner response:\n{text}"
    )
    return _grade_production("writing", task_context, level)


def grade_speaking(task, text: str, level: str) -> ProductionFeedback:
    """Grade a lesson Speaking transcript at the learner's current level."""
    task_context = (
        f"Task: {task.title}\n"
        f"Instructions: {task.instructions_pl}\n"
        f"Prompts: {'; '.join(task.prompts)}\n\n"
        f"Learner transcript:\n{text}"
    )
    return _grade_production("speaking", task_context, level)

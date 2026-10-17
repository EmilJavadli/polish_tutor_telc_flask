"""Curriculum day definitions and placement-based starting recommendations."""

from dataclasses import dataclass

TOTAL_DAYS = 273


@dataclass(frozen=True)
class PlanDay:
    day: int
    week: int
    month: int
    phase: str
    level: str
    theme_en: str
    theme_pl: str
    situation: str
    lesson_type: str
    grammar_ids: tuple[str, ...]
    grammar_titles: tuple[str, ...]
    listening_type: str
    speaking_part: int
    writing_focus: str
    reading_length: tuple[int, int]
    listening_length: tuple[int, int]
    writing_length: tuple[int, int]
    text_type: str


GRAMMAR = {
    "g1": ("Present tense", "czas teraźniejszy"),
    "g2": ("Accusative", "biernik"),
    "g3": ("Past tense", "czas przeszły"),
}
SPEAKING_PART_NAMES = {1: "Presentation", 2: "Experience", 3: "Discussion"}


def get_plan_day(day):
    week = (day - 1) // 7 + 1
    if week <= 8:
        level, phase = "A1", "Foundations (A1)"
    elif week <= 17:
        level, phase = "A2", "Elementary (A2)"
    else:
        level, phase = "B1", "Intermediate (B1)"
    return PlanDay(
        day,
        week,
        (week - 1) // 4 + 1,
        phase,
        level,
        "Everyday Polish",
        "Polski na co dzień",
        "daily life",
        "review" if day % 7 == 0 else "lesson",
        ("g1", "g2", "g3"),
        tuple(GRAMMAR[x][0] for x in ("g1", "g2", "g3")),
        "dialogue",
        1,
        "message",
        (80, 180),
        (60, 140),
        (40, 100),
        "message",
    )


def recommend_start_position(overall_level, skill_profiles, confidence=None):
    order = {"A0": 0, "A1": 1, "A2": 2, "B1": 3}
    levels = {
        k: (
            v.get("level", "A0")
            if isinstance(v, dict)
            else ("B1" if v >= 70 else "A2" if v >= 50 else "A1" if v >= 25 else "A0")
        )
        for k, v in (skill_profiles or {}).items()
    }
    vals = {k: order.get(v, 0) for k, v in levels.items()}
    count = lambda n: sum(v >= n for v in vals.values())
    confidence = 0.5 if confidence is None else confidence
    if overall_level == "A0":
        day = 1
    elif overall_level == "A1":
        day = (
            8
            if any(vals.get(k, 0) == 0 for k in ("listening", "writing", "speaking"))
            else 29 if count(2) >= 2 and confidence >= 0.65 else 22
        )
    elif overall_level == "A2":
        day = (
            50
            if any(vals.get(k, 0) <= 1 for k in ("listening", "writing", "speaking"))
            else 85 if count(2) >= 4 and count(3) >= 1 and confidence >= 0.7 else 57
        )
    else:
        day = (
            246
            if count(3) == 5 and confidence >= 0.8
            else 211 if count(3) >= 3 and min(vals.values(), default=0) >= 2 else 120
        )

    p = get_plan_day(day)
    return {
        "day": day,
        "week": p.week,
        "phase": p.phase,
        "curriculum_level": p.level,
        "skill_levels": levels,
        "priority_skills": [
            k for k, v in vals.items() if v == min(vals.values(), default=0)
        ],
        "reasons": [f"CEFR profile supports starting at day {day}."],
    }


def plan_markdown():
    return "# Polish Tutor plan\n\n273-day A1 to TELC B1 plan."

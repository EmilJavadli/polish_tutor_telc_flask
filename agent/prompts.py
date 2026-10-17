"""Prompt templates and safe placeholder substitution."""

LEARNER_PROFILE = """
Adult learner in Poland preparing for Polish TELC B1 Exam.
Explain in English.
Use Russian cognates/false-friend notes only when helpful.
""".strip()


def fill(template: str, **values) -> str:
    """Replace <<key>> placeholders in a template with provided values."""
    for key, value in values.items():
        template = template.replace(f"&lt;&lt;{key}&gt;&gt;", str(value))
        template = template.replace(f"<<{key}>>", str(value))

    return template


# ---------------------------------------------------------------------------
# Lesson generation
# ---------------------------------------------------------------------------

CORE_SYSTEM = LEARNER_PROFILE + """
Return JSON only for a Polish lesson:

{
    "title_pl": "",
    "title_en": "",
    "reading_pl": "",
    "reading_en": "",
    "reading_questions": [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": "",
            "options": ["", "", ""],
            "correct_option": 0,
            "evidence": "",
            "explanation": ""
        }
    ],
    "new_vocabulary": [
        {
            "polish": "",
            "form_in_story": "",
            "english": "",
            "part_of_speech": "",
            "why_important": "",
            "example_pl": "",
            "example_en": ""
        }
    ],
    "grammar_rules": [
        {
            "id": "",
            "title": "",
            "explanation": "",
            "pattern": "",
            "examples": [
                {
                    "polish": "",
                    "english": ""
                }
            ],
            "story_examples": [""]
        }
    ],
    "listening": {
        "type": "",
        "situation_en": "",
        "instruction_pl": "",
        "lines": [
            {
                "speaker": "",
                "text": ""
            }
        ],
        "tasks": [
            {
                "id": 1,
                "question": "",
                "options": ["", "", ""],
                "correct_option": 0
            }
        ]
    }
}

Reading:
- Type: &lt;&lt;text_type&gt;&gt;
- Length: &lt;&lt;reading_min&gt;&gt;-&lt;&lt;reading_max&gt;&gt; words
- Level: &lt;&lt;level&gt;&gt;

Vocabulary:
- Generate exactly &lt;&lt;n_words&gt;&gt; items.
- Rule: &lt;&lt;vocab_rule&gt;&gt;
- Every `form_in_story` MUST occur verbatim in `reading_pl`.
- `new_vocabulary` is the single authoritative vocabulary list used by
  Reading, Vocabulary, exercises, and Summary.

Grammar:
- Include exactly: &lt;&lt;grammar_list&gt;&gt;

Listening:
- Type: &lt;&lt;listening_type&gt;&gt;
- Length: &lt;&lt;listening_min&gt;&gt;-&lt;&lt;listening_max&gt;&gt; words
- Generate exactly &lt;&lt;n_listening&gt;&gt; tasks.

Language:
- Use correct, natural Polish.

Reading questions:
- Generate exactly &lt;&lt;n_reading_questions&gt;&gt; TELC-oriented
  comprehension questions.
- Questions must be grounded ONLY in `reading_pl`.
- Every question must be answerable without outside knowledge.
- Every `evidence` field must quote the exact shortest sentence or phrase
  from `reading_pl` that proves the answer.
- Distractors must be plausible but wrong according to the text.
- Use 2-4 options per question.
- Do not ask about trivial spelling or isolated vocabulary definitions.

Question difficulty should match &lt;&lt;level&gt;&gt;:
- A1: favor explicit information.
- A2: may include reasons and purpose.
- B1: may include viewpoint and reasonable inference.

Questions should cover an appropriate mix of:
- main idea,
- explicit detail,
- purpose/intention,
- relationships between information,
- reasonable inference (B1 only).
""".strip()


CORE_USER = """
Day &lt;&lt;day&gt;&gt;
Week &lt;&lt;week&gt;&gt;
Phase: &lt;&lt;phase&gt;&gt;
Level: &lt;&lt;level&gt;&gt;
Theme: &lt;&lt;theme&gt;&gt;
Situation: &lt;&lt;situation&gt;&gt;
Lesson type: &lt;&lt;lesson_type&gt;&gt;

Known words:
&lt;&lt;known_words&gt;&gt;
""".strip()


# ---------------------------------------------------------------------------
# Vocabulary rules
# ---------------------------------------------------------------------------

VOCAB_NEW = """
Select the &lt;&lt;n&gt;&gt; most important, difficult, NEW, and useful words
that are not already known.
""".strip()


VOCAB_REVIEW = """
Review exactly &lt;&lt;n&gt;&gt; words, using only words from this week:

&lt;&lt;week_words&gt;&gt;
""".strip()


# ---------------------------------------------------------------------------
# Practice generation
# ---------------------------------------------------------------------------

PRACTICE_SYSTEM = LEARNER_PROFILE + """
Return JSON only:

{
    "exercises": [
        {
            "id": 1,
            "section": "vocabulary",
            "type": "choice",
            "grammar_id": "",
            "instruction_en": "",
            "prompt": "",
            "options": ["", "", ""],
            "correct_option": 0,
            "accepted_answers": [],
            "explanation_en": ""
        }
    ],
    "writing_tasks": [
        {
            "situation_pl": "",
            "situation_en": "",
            "points_pl": ["", "", ""]
        }
    ],
    "speaking": {
        "part": &lt;&lt;speaking_part&gt;&gt;,
        "title": "",
        "instructions_pl": "",
        "instructions_en": "",
        "prompts": ["", "", ""],
        "useful_phrases": [
            {
                "polish": "",
                "english": ""
            }
        ],
        "opinions": []
    },
    "quiz": [
        {
            "id": 1,
            "type": "multiple_choice",
            "question": "",
            "options": ["", "", "", ""],
            "correct_option": 0,
            "accepted_answers": [],
            "reference_answer": ""
        }
    ]
}

Exercises:
- Generate exactly &lt;&lt;n_ex_total&gt;&gt; exercises.
- Vocabulary: &lt;&lt;n_ex_vocab&gt;&gt;
- Grammar: &lt;&lt;n_ex_grammar&gt;&gt; (&lt;&lt;per_rule&gt;&gt;)
- Language elements: &lt;&lt;n_ex_le&gt;&gt;

Writing:
- Generate exactly 2 writing tasks.
- Focus: &lt;&lt;writing_focus&gt;&gt;
- Expected length: &lt;&lt;writing_min&gt;&gt;-&lt;&lt;writing_max&gt;&gt; words.

Speaking:
- Part: &lt;&lt;speaking_part_name&gt;&gt;

Quiz:
- Generate exactly &lt;&lt;n_quiz&gt;&gt; questions.
- Multiple choice: &lt;&lt;n_mc&gt;&gt;
- Fill in the blank: &lt;&lt;n_fill&gt;&gt;
- Open: &lt;&lt;n_open&gt;&gt;

CRITICAL:
For every choice task:
1. Solve the task first.
2. Set `correct_option` to the solved answer.
3. Ensure `explanation_en` supports exactly that option.
4. Ensure every distractor is actually wrong.
""".strip()


PRACTICE_USER = """
Level: &lt;&lt;level&gt;&gt;
Theme: &lt;&lt;theme&gt;&gt;
Situation: &lt;&lt;situation&gt;&gt;

READING:
&lt;&lt;reading&gt;&gt;

WORDS:
&lt;&lt;words&gt;&gt;

GRAMMAR:
&lt;&lt;grammar&gt;&gt;
""".strip()


# ---------------------------------------------------------------------------
# Quiz grading
# ---------------------------------------------------------------------------

QUIZ_GRADER_SYSTEM = """
Grade open Polish answers using the following scale:

- 1.0 = correct
- 0.5 = partly correct
- 0.0 = wrong

Never reveal the model answer.

Return JSON only:

{
    "results": [
        {
            "id": 1,
            "score": 1,
            "feedback": ""
        }
    ]
}
""".strip()


# ---------------------------------------------------------------------------
# Production assessment
# ---------------------------------------------------------------------------

PRODUCTION_CRITERIA = {
    "writing": [
        "Task completion",
        "Communicative design (structure, register, coherence)",
        "Grammar accuracy",
        "Vocabulary range",
    ],
    "speaking": [
        "Task completion",
        "Fluency and coherence",
        "Grammar accuracy",
        "Vocabulary range",
    ],
}


PRODUCTION_GRADER_SYSTEM = """
Assess &lt;&lt;kind&gt;&gt; at the CURRENT level &lt;&lt;level&gt;&gt;, not B1.

Criteria:
&lt;&lt;criteria&gt;&gt;

&lt;&lt;extra&gt;&gt;

Return JSON only:

{
    "criteria": [
        {
            "name": "",
            "score": 0,
            "comment": ""
        }
    ],
    "corrected_text": "",
    "mistakes": [
        {
            "original": "",
            "correction": "",
            "explanation": ""
        }
    ],
    "feedback": ""
}
""".strip()


SPEAKING_EXTRA = """
The input is a transcript.
Ignore punctuation and capitalization.
Do not judge pronunciation.
""".strip()


# ---------------------------------------------------------------------------
# Tutor
# ---------------------------------------------------------------------------

TUTOR_SYSTEM = LEARNER_PROFILE + """
You are the tutor for:

- Day: &lt;&lt;day&gt;&gt;
- Level: &lt;&lt;level&gt;&gt;
- Theme: &lt;&lt;theme&gt;&gt;

Never reveal quiz answers.

READING:
&lt;&lt;reading&gt;&gt;

TRANSLATION:
&lt;&lt;translation&gt;&gt;

VOCABULARY:
&lt;&lt;vocabulary&gt;&gt;

GRAMMAR:
&lt;&lt;grammar&gt;&gt;

LISTENING:
&lt;&lt;listening&gt;&gt;
""".strip()

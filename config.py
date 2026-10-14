import os
from pathlib import Path


BASE_DIR=Path(__file__).resolve().parent
DATABASE_URL=os.getenv('DATABASE_URL',f"sqlite:///{BASE_DIR/'polish_tutor.db'}")
FLASK_SECRET_KEY=os.getenv('FLASK_SECRET_KEY','')
GOOGLE_CLIENT_ID=os.getenv('GOOGLE_CLIENT_ID','')
GOOGLE_CLIENT_SECRET=os.getenv('GOOGLE_CLIENT_SECRET','')
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY','')
ELEVENLABS_API_KEY=os.getenv('ELEVENLABS_API_KEY','')
ELEVENLABS_VOICE_ID=os.getenv('ELEVENLABS_VOICE_ID','')
LLM_MODEL = 'gpt-6-luna'
STT_MODEL = 'gpt-4o-mini-transcribe'
ELEVENLABS_MODEL='eleven_v4_turbo'
PLACEMENT_VERSION= 'cefr-v2'
DATA_DIR=Path(str(BASE_DIR/'data'))
QUIZ_PASS_SCORE=.8
DEV_LOGIN=os.getenv('DEV_LOGIN','1')=='1'

# Lesson generation configuration
# Restored for the original validated two-call OpenAI lesson generator.
NEW_WORDS_PER_LESSON = int(os.getenv('NEW_WORDS_PER_LESSON', '15'))
LISTENING_TASKS = int(os.getenv('LISTENING_TASKS', '5'))
MAX_GENERATION_ATTEMPTS = int(os.getenv('MAX_GENERATION_ATTEMPTS', '3'))
MAX_KNOWN_WORDS_IN_PROMPT = int(os.getenv('MAX_KNOWN_WORDS_IN_PROMPT', '250'))

EXERCISE_COMPOSITION = {
    'vocabulary': int(os.getenv('EXERCISES_VOCABULARY', '4')),
    'grammar': int(os.getenv('EXERCISES_GRAMMAR', '9')),
    'language_elements': int(os.getenv('EXERCISES_LANGUAGE_ELEMENTS', '3')),
}

QUIZ_COMPOSITION = {
    'multiple_choice': int(os.getenv('QUIZ_MULTIPLE_CHOICE', '4')),
    'fill_blank': int(os.getenv('QUIZ_FILL_BLANK', '3')),
    'open': int(os.getenv('QUIZ_OPEN', '1')),
}

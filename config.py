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

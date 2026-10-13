from datetime import datetime
from functools import wraps
from pathlib import Path
from flask import Flask,Blueprint,Response,jsonify,redirect,render_template,request,send_file,session,url_for
from dotenv import load_dotenv
load_dotenv()
from config import FLASK_SECRET_KEY,DATA_DIR,QUIZ_PASS_SCORE,DEV_LOGIN
from database.connection import get_session_factory
from auth.google_oidc import bp as auth_bp,init_oauth,identity_from_session
from repositories.user_repository import UserRepository
from repositories.lesson_repository import LessonRepository
from repositories.evaluation_repository import EvaluationRepository
from curriculum import get_plan_day,TOTAL_DAYS,recommend_start_position
from agent.lesson_generator import generate_lesson
from agent.graders import grade_exercises,grade_listening,grade_quiz,grade_writing,grade_speaking
from agent.llm import transcribe
from agent.schemas import WritingAttempt,SpeakingAttempt
from agent.tts import synthesize_speech,synthesize_dialogue
from placement.test_bank import GRAMMAR_VOCAB,READING,LISTENING,READING_TEXT,LISTENING_TEXT
from placement.scoring import objective_profile,classify
from placement.grader import grade_productive

app=Flask(__name__)
app.secret_key=FLASK_SECRET_KEY
app.config.update(SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax',MAX_CONTENT_LENGTH=20*1024*1024)

init_oauth(app)
app.register_blueprint(auth_bp)
main=Blueprint('main',__name__)


def current():
 ident=identity_from_session()
 if not ident:return None,None,None
 users=UserRepository(get_session_factory());user=users.resolve(ident);return user,users.profile(user.id),ident
def login_required(fn):
 @wraps(fn)
 def wrapped(*a,**kw):
  if not identity_from_session():return redirect(url_for('auth.login'))
  return fn(*a,**kw)
 return wrapped
def repos():
 user,profile,_=current();return user,profile,LessonRepository(get_session_factory(),user.id,DATA_DIR/'audio'),EvaluationRepository(get_session_factory(),user.id)
def payload(x):return x.model_dump(mode='json') if hasattr(x,'model_dump') else x

@main.get('/')
def index():
 if not identity_from_session():return render_template('login.html',dev_login=DEV_LOGIN)
 user,profile,_,eval_repo=repos()
 if not profile.evaluation_completed:return redirect(url_for('main.placement'))
 return redirect(url_for('main.dashboard'))

@main.get('/dashboard')
@login_required
def dashboard():
 user,profile,repo,_=repos();stats=repo.stats(datetime.now().date());skills=profile.skill_profile or {};return render_template('dashboard.html',user=user,profile=profile,stats=stats,skills=skills,current_day=repo.current_day,total_days=TOTAL_DAYS)

@main.get('/lesson')
@login_required
def lesson_page():
 user,profile,repo,_=repos();day=int(request.args.get('day',repo.current_day));lesson=repo.load_lesson(day);return render_template('lesson.html',user=user,profile=profile,lesson=payload(lesson) if lesson else None,day=day,plan=get_plan_day(day),progress=repo.get_progress(day) if lesson else {})

@main.post('/api/lesson/generate')
@login_required
def generate():
 _,_,repo,_=repos();day=int((request.get_json() or {}).get('day',repo.current_day));plan=get_plan_day(day);lesson=generate_lesson(plan,repo.taught_words(day),repo.week_words(plan.week,day));repo.save_lesson(lesson);return jsonify(payload(lesson))

@main.get('/api/lesson/<int:day>')
@login_required
def lesson_json(day):
 _,_,repo,_=repos();lesson=repo.load_lesson(day);return jsonify(payload(lesson)) if lesson else (jsonify({'error':'not found'}),404)

@main.post('/api/lesson/<int:day>/progress')
@login_required
def save_progress(day):
 _,_,repo,_=repos();state=repo.get_progress(day);state.update(request.get_json() or {});repo.save_progress(day,state);return jsonify({'saved':True})

@main.post('/api/lesson/<int:day>/listening')
@login_required
def listening(day):
 _,_,repo,_=repos();l=repo.load_lesson(day);a=grade_listening(l.listening.tasks,(request.get_json() or {}).get('answers',{}));repo.add_attempt(day,'listening',a);return jsonify(payload(a))
@main.post('/api/lesson/<int:day>/exercises')
@login_required
def exercises(day):
 _,_,repo,_=repos();l=repo.load_lesson(day);a=grade_exercises(l.exercises,(request.get_json() or {}).get('answers',{}));repo.add_attempt(day,'exercises',a);return jsonify(payload(a))
@main.post('/api/lesson/<int:day>/quiz')
@login_required
def quiz(day):
 _,_,repo,_=repos();l=repo.load_lesson(day);a=grade_quiz(l.quiz,(request.get_json() or {}).get('answers',{}),QUIZ_PASS_SCORE);repo.add_attempt(day,'quiz',a);repo.update_completion(day);return jsonify(payload(a))
@main.post('/api/lesson/<int:day>/writing')
@login_required
def writing(day):
 _,_,repo,_=repos();l=repo.load_lesson(day);body=request.get_json() or {};idx=int(body.get('task_index',0));text=body.get('text','');fb=grade_writing(l.writing_tasks[idx],text,l.level);a=WritingAttempt(task_index=idx,text=text,word_count=len(text.split()),result=fb,timestamp=datetime.now().isoformat());repo.add_attempt(day,'writing',a);repo.update_completion(day);return jsonify(payload(a))
@main.post('/api/lesson/<int:day>/speaking')
@login_required
def speaking(day):
 _,_,repo,_=repos();l=repo.load_lesson(day);f=request.files.get('audio');typed=request.form.get('text','')
 if f:audio=f.read();transcript=transcribe(audio,f.filename or 'answer.webm',context=l.speaking.title);name=repo.save_recording(day,audio,(f.filename.rsplit('.',1)[-1] if '.' in f.filename else 'webm'))
 else:transcript=typed;name=None
 fb=grade_speaking(l.speaking,transcript,l.level);a=SpeakingAttempt(transcript=transcript,audio_file=name,typed=not bool(f),result=fb,timestamp=datetime.now().isoformat());repo.add_attempt(day,'speaking',a);repo.update_completion(day);return jsonify(payload(a))

@main.post('/api/lesson/<int:day>/audio/<kind>')
@login_required
def audio(day,kind):
 _,_,repo,_=repos();l=repo.load_lesson(day);path=repo.audio_path(day,kind)
 if not path.exists():
  data=synthesize_dialogue(l.listening.lines) if kind=='listening' else synthesize_speech(l.reading_pl,'slow' if 'slow' in kind else 'normal');path.write_bytes(data)
 return send_file(path,mimetype='audio/mpeg')

@main.post('/api/chat/<int:day>')
@login_required
def chat(day):
 from agent.tutor_chat import stream_tutor_reply
 _,_,repo,_=repos();l=repo.load_lesson(day);body=request.get_json() or {};history=body.get('history',[]);message=body.get('message','');messages=history+[{'role':'user','content':message}]
 def stream():
  try:
   for chunk in stream_tutor_reply(l,messages):yield chunk
  except Exception as e:yield f'Tutor error: {e}'
 return Response(stream(),mimetype='text/plain')

@main.get('/placement')
@login_required
def placement():
 user,profile,_,ev=repos();evaluation=ev.get_or_create(mode='initial' if not profile.evaluation_completed else 'retake');return render_template('placement.html',user=user,profile=profile,evaluation=evaluation,grammar=GRAMMAR_VOCAB,reading=READING,reading_text=READING_TEXT,listening=LISTENING,listening_text=LISTENING_TEXT)

@main.post('/api/placement/complete')
@login_required
def placement_complete():
 user,profile,_,ev=repos();evaluation=ev.get_or_create(mode='initial' if not profile.evaluation_completed else 'retake');data=request.get_json() or {};responses=data.get('responses',{});writing_text=data.get('writing','');speaking_text=data.get('speaking','')
 profiles={'grammar_vocab':objective_profile(GRAMMAR_VOCAB,responses.get('grammar_vocab',{})),'reading':objective_profile(READING,responses.get('reading',{})),'listening':objective_profile(LISTENING,responses.get('listening',{})),'writing':grade_productive('writing',writing_text),'speaking':grade_productive('speaking',speaking_text)};result=classify(profiles);ev.save_result(evaluation.id,result,mode='initial' if not profile.evaluation_completed else 'retake')
 if not profile.evaluation_completed:ev.apply_result(evaluation.id,daily_minutes=int(data.get('daily_minutes',60)),target_level='B1')
 return jsonify(result)

@main.post('/api/placement/retake/<evaluation_id>/apply')
@login_required
def apply_retake(evaluation_id):
 _,profile,_,ev=repos();plan=ev.apply_result(evaluation_id,daily_minutes=profile.daily_study_minutes,target_level=profile.target_cefr_level);return jsonify({'applied':True,'start_day':plan.start_curriculum_day})

app.register_blueprint(main)
if __name__=='__main__':app.run(debug=True,port=5000)

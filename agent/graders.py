from datetime import datetime
from agent.schemas import ExerciseAttempt,ListeningAttempt,QuizAttempt,ProductionFeedback,Criterion
def grade_listening(tasks,answers):
 score=sum(str(answers.get(str(q.id),''))==str(q.correct_option) for q in tasks)/max(1,len(tasks));return ListeningAttempt(answers=answers,score=score,timestamp=datetime.now().isoformat())
def grade_exercises(items,answers):
 ok=0
 for q in items:
  a=answers.get(str(q.id),'');ok+= int(str(a)==str(q.correct_option) if q.type=='choice' else a.strip().lower() in [x.lower() for x in q.accepted_answers])
 return ExerciseAttempt(answers=answers,score=ok/max(1,len(items)),timestamp=datetime.now().isoformat())
def grade_quiz(items,answers,pass_score=.8):
 ok=0
 for q in items:ok+=int(str(answers.get(str(q.id),''))==str(q.correct_option) if q.type=='multiple_choice' else answers.get(str(q.id),'').strip().lower() in [x.lower() for x in q.accepted_answers] if q.type=='fill_blank' else bool(answers.get(str(q.id),'')))
 score=ok/max(1,len(items));return QuizAttempt(answers=answers,score=score,passed=score>=pass_score,timestamp=datetime.now().isoformat())
def _feedback(text):return ProductionFeedback(criteria=[Criterion(name='Task completion',score=4,comment='Demo assessment')],corrected_text=text,feedback='Good work. Production uses the AI grader.')
def grade_writing(task,text,level):return _feedback(text)
def grade_speaking(task,text,level):return _feedback(text)

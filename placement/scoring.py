from statistics import median
from curriculum import recommend_start_position
LEVELS=('A0','A1','A2','B1');VALUE={x:i for i,x in enumerate(LEVELS)}
def objective_profile(items,answers):
 bands={}
 for band in ('A1','A2','B1'):
  xs=[x for x in items if x['band']==band];correct=sum(str(answers.get(x['id'],''))==str(x['answer']) for x in xs);acc=correct/max(1,len(xs));bands[band]={'correct':correct,'total':len(xs),'accuracy':acc,'mastered':len(xs)>=3 and acc>=2/3}
 level='A1' if bands['A1']['mastered'] else 'A0'
 if level=='A1' and bands['A2']['mastered']:level='A2'
 if level=='A2' and bands['B1']['mastered']:level='B1'
 return {'level':level,'score':round(100*sum(x['correct'] for x in bands.values())/max(1,sum(x['total'] for x in bands.values())),1),'confidence':.85,'bands':bands}
def objective_score(items,answers):return objective_profile(items,answers)['score']
def classify(scores):
 norm={}
 for k,p in scores.items():
  if isinstance(p,(int,float)):
   level='B1' if p>=70 else 'A2' if p>=50 else 'A1' if p>=25 else 'A0';p={'level':level,'score':float(p),'confidence':.5}
  norm[k]=p
 vals={k:VALUE.get(p.get('level','A0'),0) for k,p in norm.items()};candidate=int(median(vals.values())) if vals else 0;productive=min(vals.get('writing',0),vals.get('speaking',0));receptive=min(vals.get('reading',0),vals.get('listening',0));grammar=vals.get('grammar_vocab',0)
 if candidate>=3 and min(productive,receptive,grammar)<2:candidate=2
 if candidate>=2 and min(productive,receptive,grammar)<1:candidate=1
 level=LEVELS[candidate];confidence=round(sum(float(p.get('confidence',.5)) for p in norm.values())/max(1,len(norm)),2);rec=recommend_start_position(level,norm,confidence);weak=min(vals.values(),default=0);strong=max(vals.values(),default=0)
 return {'level':level,'start_day':rec['day'],'start_recommendation':rec,'overall':round(sum(float(p.get('score',0)) for p in norm.values())/max(1,len(norm)),1),'scores':norm,'skill_levels':{k:p.get('level','A0') for k,p in norm.items()},'strengths':[k for k,v in vals.items() if v==strong and v>candidate],'weaknesses':[k for k,v in vals.items() if v==weak or v<candidate],'confidence':confidence}

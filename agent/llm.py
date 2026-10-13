import json
from functools import lru_cache
from config import OPENAI_API_KEY,LLM_MODEL,STT_MODEL
@lru_cache(maxsize=1)
def get_client():
 from openai import OpenAI
 if not OPENAI_API_KEY:raise RuntimeError('OPENAI_API_KEY is not configured')
 return OpenAI(api_key=OPENAI_API_KEY)
def chat_json(messages):
 r=get_client().chat.completions.create(model=LLM_MODEL,messages=messages,response_format={'type':'json_object'});return json.loads(r.choices[0].message.content or '{}')
def chat_stream(messages):
 for chunk in get_client().chat.completions.create(model=LLM_MODEL,messages=messages,stream=True):
  if chunk.choices and chunk.choices[0].delta.content:yield chunk.choices[0].delta.content
def transcribe(audio,filename='answer.webm',context=''):
 kw={'model':STT_MODEL,'file':(filename,audio)}
 if context:kw['prompt']=context
 return (get_client().audio.transcriptions.create(**kw).text or '').strip()

from config import ELEVENLABS_API_KEY,ELEVENLABS_VOICE_ID,ELEVENLABS_MODEL
def tts_available():return bool(ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID)
def synthesize_speech(text,pace='normal'):
 from elevenlabs.client import ElevenLabs
 if not tts_available():raise RuntimeError('ElevenLabs credentials are not configured')
 return b''.join(ElevenLabs(api_key=ELEVENLABS_API_KEY).text_to_speech.convert(voice_id=ELEVENLABS_VOICE_ID,model_id=ELEVENLABS_MODEL,text=text,output_format='mp3_44100_128'))
def synthesize_dialogue(lines):return synthesize_speech('\n'.join(f'{x.speaker}: {x.text}' for x in lines))

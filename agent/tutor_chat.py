from agent.llm import chat_stream

def stream_tutor_reply(lesson,history):
    system=f'You are a Polish tutor. Current lesson: {lesson.title_pl}. Reading: {lesson.reading_pl}. Never reveal quiz answers.'
    return chat_stream([{'role':'system',
                         'content':system}]+history)

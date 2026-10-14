from pydantic import BaseModel,Field
class Example(BaseModel):polish:str;english:str
class Vocabulary(BaseModel):polish:str;form_in_story:str='';english:str;part_of_speech:str='';why_important:str='';example_pl:str='';example_en:str=''
class GrammarRule(BaseModel):id:str;title:str;explanation:str='';pattern:str='';examples:list[Example]=Field(default_factory=list);story_examples:list[str]=Field(default_factory=list)
class DialogueLine(BaseModel):speaker:str;text:str
class ChoiceTask(BaseModel):id:int;question:str;options:list[str];correct_option:int
class ReadingQuestion(BaseModel):
    id:int
    type:str='multiple_choice'
    question:str
    options:list[str]
    correct_option:int
    explanation:str=''
    evidence:str=''
class Listening(BaseModel):type:str='dialogue';situation_en:str='';instruction_pl:str='';lines:list[DialogueLine]=Field(default_factory=list);tasks:list[ChoiceTask]=Field(default_factory=list)
class Exercise(BaseModel):id:int;section:str;type:str;grammar_id:str='';instruction_en:str='';prompt:str;options:list[str]=Field(default_factory=list);correct_option:int|None=None;accepted_answers:list[str]=Field(default_factory=list);explanation_en:str=''
class WritingTask(BaseModel):situation_pl:str;situation_en:str;points_pl:list[str]
class SpeakingTask(BaseModel):part:int=1;title:str;instructions_pl:str;instructions_en:str;prompts:list[str];useful_phrases:list[Example]=Field(default_factory=list);opinions:list[str]=Field(default_factory=list)
class QuizQuestion(BaseModel):id:int;type:str;question:str;options:list[str]=Field(default_factory=list);correct_option:int|None=None;accepted_answers:list[str]=Field(default_factory=list);reference_answer:str=''
class CoreLesson(BaseModel):title_pl:str;title_en:str;reading_pl:str;reading_en:str;reading_questions:list[ReadingQuestion]=Field(default_factory=list);new_vocabulary:list[Vocabulary];grammar_rules:list[GrammarRule];listening:Listening
class Practice(BaseModel):exercises:list[Exercise];writing_tasks:list[WritingTask];speaking:SpeakingTask;quiz:list[QuizQuestion]
class Lesson(CoreLesson,Practice):day:int;week:int;level:str;lesson_type:str='lesson';theme_en:str;situation:str;text_type:str='text';created:str=''
class ReadingAttempt(BaseModel):answers:dict={};score:float=0;feedback:dict=Field(default_factory=dict);timestamp:str=''
class ListeningAttempt(BaseModel):answers:dict={};score:float=0;timestamp:str=''
class ExerciseAttempt(BaseModel):answers:dict={};score:float=0;feedback:dict={};timestamp:str=''
class QuizAttempt(BaseModel):answers:dict={};score:float=0;passed:bool=False;feedback:dict={};timestamp:str=''
class Criterion(BaseModel):name:str;score:float;comment:str=''
class Mistake(BaseModel):original:str;correction:str;explanation:str=''
class ProductionFeedback(BaseModel):criteria:list[Criterion]=Field(default_factory=list);corrected_text:str='';mistakes:list[Mistake]=Field(default_factory=list);feedback:str=''
class WritingAttempt(BaseModel):task_index:int=0;text:str;word_count:int=0;result:ProductionFeedback;timestamp:str=''
class SpeakingAttempt(BaseModel):transcript:str;audio_file:str|None=None;typed:bool=False;result:ProductionFeedback;timestamp:str=''

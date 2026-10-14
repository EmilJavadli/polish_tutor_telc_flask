const lesson=JSON.parse(document.querySelector('#lessonData').textContent),day=window.LESSON_DAY;let panel=document.querySelector('#lessonPanel');let chatHistory=[];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const TELC_GUIDES = {
  Reading:{A1:'Read once for the main topic, then again for clear details such as names, places and times. Do not translate every word; answer only from information in the text.',A2:'Read first for the main message, then identify specific information, reasons and purpose. Use context to infer unfamiliar vocabulary.',B1:'Read for purpose, viewpoint, key details and connections between ideas. Notice contrast and cause connectors and base answers on evidence in the text.'},
  Listening:{A1:'Read the questions first. Listen once for the situation and main message, then again for who, where, when and what.',A2:'Read the questions before listening. First identify situation and intention; then listen for details, reasons, changes and required actions.',B1:'Use the first listening for the overall argument or conversation. Use the second to verify opinions, reasons, implied meaning and supporting details.'},
  Vocabulary:{A1:'Learn each word as part of a useful expression. Say the Polish form aloud and make one short sentence about your life.',A2:'Notice the form used in the text, common combinations and appropriate context. Reuse each key word in a complete sentence.',B1:'Learn meaning, register and common combinations rather than isolated translations. Practise paraphrasing and using expressions in connected explanations.'},
  Grammar:{A1:'Focus on the basic pattern and changing ending. Read examples aloud and create one similar sentence about yourself.',A2:'Study how the form communicates time, case, movement or intention. Compare examples and reuse the pattern in an everyday sentence.',B1:'Focus on accurate forms, word order and connectors that support explanation, comparison, narration and justification in connected language.'},
  Exercises:{A1:'Complete the tasks without checking the lesson first. Use sentence context, then review every mistake and repeat the correct form.',A2:'Work independently and read every instruction carefully. Use meaning and grammar together, then explain why the correct answer fits.',B1:'Treat this as TELC preparation: work without notes, manage your time and use the complete context. Review errors by category.'},
  Writing:{A1:'Read all task points before writing. Use short, clear sentences, cover every required point and check basic verb forms and spelling.',A2:'Plan before writing. Cover every task point, organize ideas logically, use simple connectors and match the register to the situation.',B1:'Apply TELC writing strategy: identify purpose, recipient and register; cover every task point; organize and connect ideas; then check grammar and spelling.'},
  Speaking:{A1:'Prepare keywords, not a script. Speak in short understandable sentences, answer every prompt and continue after mistakes.',A2:'Use brief notes only. Connect sentences, describe past or future events and give simple reasons. Reformulate if a word is missing.',B1:'Apply TELC speaking strategy: respond directly, speak in connected Polish, give reasons and examples, react naturally and do not read a prepared script.'},
  Quiz:{A1:'Complete this checkpoint without looking back at the lesson. The app requires 80% to pass; this is an internal learning threshold, not an official TELC score.',A2:'Work without notes and answer from active recall. The app requires 80% to pass; use mistakes to decide what to review.',B1:'Treat this as a TELC-preparation checkpoint and work without lesson materials. The app’s 80% pass mark is an internal mastery rule, not an official TELC requirement.'}
};
function telcGuide(section){
  const level=['A1','A2','B1'].includes(lesson.level)?lesson.level:'A1';
  const label=level==='B1'?'TELC exam strategy':'TELC preparation strategy';
  return `<div class="section-guide"><div class="section-guide-head"><strong>${label}</strong><span>${level}</span></div><p>${esc(TELC_GUIDES[section][level])}</p></div>`;
}
function choices(items,url,guide=""){let answers={};panel.innerHTML=guide+items.map(q=>`<div class="question"><b>${esc(q.prompt||q.question)}</b>${(q.options||[]).map((o,i)=>`<button data-id="${q.id}" data-a="${i}">${esc(o)}</button>`).join('')}${q.type&&q.type!=='choice'&&q.type!=='multiple_choice'?`<input data-text="${q.id}">`:''}</div>`).join('')+'<button class="primary" id="submitChoices">Submit</button><div id="answerResult"></div>';panel.querySelectorAll('[data-a]').forEach(b=>b.onclick=()=>{panel.querySelectorAll(`[data-id="${b.dataset.id}"]`).forEach(x=>x.classList.remove('selected'));b.classList.add('selected');answers[b.dataset.id]=Number(b.dataset.a)});$('#submitChoices').onclick=async()=>{panel.querySelectorAll('[data-text]').forEach(x=>answers[x.dataset.text]=x.value);let r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answers})}),j=await r.json();$('#answerResult').innerHTML=`<div class="result">Score: ${Math.round(j.score*100)}%</div>`}}
function telcSummaryTakeaway(){
 const level=['A1','A2','B1'].includes(lesson.level)?lesson.level:'A1';
 return {A1:'Today’s language builds the clear, simple communication needed before B1. Aim to describe familiar topics with short accurate sentences and understand the main information in everyday texts and recordings.',A2:'Today’s lesson builds toward TELC B1 through connected everyday communication. Reuse today’s vocabulary and grammar to describe experiences, plans and reasons in longer answers.',B1:'TELC takeaway: transfer today’s language into connected exam responses. Cover all task points, give reasons or examples, use suitable register and keep communicating even when language is not perfect.'}[level];
}
function summaryVocabulary(){return (lesson.new_vocabulary||[]).slice(0,8).map(w=>`<div><b>${esc(w.polish)}</b><span>${esc(w.english)}</span></div>`).join('');}
function summaryGrammar(){return (lesson.grammar_rules||[]).map(g=>`<div class="summary-grammar-item"><b>${esc(g.title)}</b><span>${esc(g.pattern||g.explanation||'Review today’s examples.')}</span></div>`).join('');}
function renderSummary(){
 panel.innerHTML=`<small class="eyebrow">SUMMARY</small><div class="summary-head"><div><h2>${esc(lesson.title_pl)}</h2><p>${esc(lesson.title_en)} · ${esc(lesson.level)}</p></div><span class="summary-level">${esc(lesson.level)}</span></div><div class="summary-grid"><section class="summary-card"><h3>Key vocabulary</h3><div class="summary-vocab">${summaryVocabulary()}</div></section><section class="summary-card"><h3>Grammar to remember</h3><div class="summary-grammar">${summaryGrammar()}</div></section></div><section class="summary-telc"><small>${lesson.level==='B1'?'TELC EXAM TAKEAWAY':'TELC PREPARATION TAKEAWAY'}</small><p>${esc(telcSummaryTakeaway())}</p></section><section class="summary-card"><div class="summary-card-title"><h3>Before you finish</h3><span id="summaryCompletionLabel">Loading progress…</span></div><div class="summary-checklist" id="summaryChecklist"></div></section><section class="summary-recall"><small>ONE-MINUTE RECALL</small><h3>Without looking back, recall:</h3><div class="recall-prompts"><span>3 words from today</span><span>1 grammar pattern</span><span>1 complete Polish sentence</span></div></section>`;
 loadSummaryProgress();
}
async function loadSummaryProgress(){
 const box=document.getElementById('summaryChecklist'),label=document.getElementById('summaryCompletionLabel');if(!box)return;
 const names={reading:'Reading',listening:'Listening',vocabulary:'Vocabulary',grammar:'Grammar',exercises:'Exercises',writing:'Writing',speaking:'Speaking',quiz:'Quiz'};
 try{const r=await fetch(`/api/lesson/${day}/summary`,{cache:'no-store'});if(!r.ok)throw new Error(`HTTP ${r.status}`);const data=await r.json();box.innerHTML=Object.entries(names).map(([key,name])=>{const done=Boolean(data.checklist?.[key]),score=data.scores?.[key];return `<div class="summary-check ${done?'done':''}"><span class="summary-check-icon">${done?'✓':'○'}</span><span>${name}</span>${score!==undefined&&score!==null?`<b>${score}%</b>`:''}</div>`}).join('');const completed=Object.values(data.checklist||{}).filter(Boolean).length;label.textContent=data.completed?'Lesson complete':`${completed}/8 activities complete`;}catch(error){console.error('Summary progress failed',error);label.textContent='Progress unavailable';box.innerHTML='<p class="muted">Progress could not be loaded.</p>';}
}
function render(name){if(name==='Reading')panel.innerHTML=`<small class="eyebrow">READING</small>${telcGuide('Reading')}<h2>${esc(lesson.title_pl)}</h2><p class="reading">${esc(lesson.reading_pl)}</p><details><summary>Show translation</summary><p>${esc(lesson.reading_en)}</p></details><div class="reading-audio-actions"><button type="button" class="secondary" id="readAudioSlow">Create slow audio</button><button type="button" class="secondary" id="readAudioNormal">Create normal audio</button></div><audio id="readingAudio" controls></audio><div id="readingAudioError"></div>`;
else if(name==='Listening'){window.renderTelcListening(lesson,day,panel,esc)}
else if(name==='Vocabulary')panel.innerHTML=`<small class="eyebrow">VOCABULARY</small>${telcGuide('Vocabulary')}<h2>Key words</h2><div class="vocab">${lesson.new_vocabulary.map(w=>`<div><b>${esc(w.polish)}</b><span>${esc(w.english)}</span></div>`).join('')}</div>`;
else if(name==='Grammar')panel.innerHTML=`<small class="eyebrow">GRAMMAR</small>${telcGuide('Grammar')}${lesson.grammar_rules.map(g=>`<div class="grammar-card"><h3>${esc(g.title)}</h3><p>${esc(g.explanation)}</p></div>`).join('')}`;
else if(name==='Exercises')choices(lesson.exercises,`/api/lesson/${day}/exercises`,telcGuide('Exercises'));
else if(name==='Quiz')choices(lesson.quiz,`/api/lesson/${day}/quiz`,telcGuide('Quiz'));
else if(name==='Writing')panel.innerHTML=`<small class="eyebrow">WRITING</small>${telcGuide('Writing')}<h2>${esc(lesson.writing_tasks[0].situation_en)}</h2><textarea id="writing"></textarea><button class="primary" id="submitWriting">Get feedback</button><div id="writingResult"></div>`;
else if(name==='Speaking')panel.innerHTML=`<small class="eyebrow">SPEAKING</small>${telcGuide('Speaking')}<h2>${esc(lesson.speaking.title)}</h2><p>${esc(lesson.speaking.instructions_en)}</p><button class="primary" id="record">Start recording</button><button class="secondary" id="stop" hidden>Stop</button><audio id="preview" controls hidden></audio><button class="primary" id="submitAudio" hidden>Submit recording</button><details><summary>Type instead</summary><textarea id="typedSpeaking"></textarea><button class="primary" id="submitTyped">Submit typed answer</button></details><div id="speakingResult"></div>`;
else if(name==='Summary')renderSummary();
wire(name)}
function choicesInto(root,items,url){let old=panel;panel=root;choices(items,url);panel=old}
async function createLessonAudio(kind, button, playerId, errorId) {
    const audioPlayer = document.getElementById(playerId);
    const errorBox = document.getElementById(errorId);
    if (!audioPlayer || !button) {
        console.error('Audio controls missing:', {kind, playerId});
        return;
    }

    const originalLabel = button.textContent;
    button.disabled = true;
    button.textContent = 'Creating audio...';
    if (errorBox) errorBox.innerHTML = '';

    try {
        const response = await fetch(`/api/lesson/${day}/audio/${kind}`, {
            method: 'POST',
            cache: 'no-store'
        });
        if (!response.ok) {
            const message = await response.text();
            throw new Error(message || `HTTP ${response.status}`);
        }
        const blob = await response.blob();
        if (!blob.size) throw new Error('Server returned empty audio.');

        if (audioPlayer.dataset.objectUrl) {
            URL.revokeObjectURL(audioPlayer.dataset.objectUrl);
        }
        const url = URL.createObjectURL(blob);
        audioPlayer.dataset.objectUrl = url;
        audioPlayer.src = url;
        audioPlayer.load();
        button.textContent = 'Audio ready';
    } catch (error) {
        console.error(`${kind} audio failed`, error);
        button.textContent = originalLabel;
        if (errorBox) {
            errorBox.innerHTML = `<div class="result audio-error">Audio creation failed: ${esc(error.message)}</div>`;
        }
    } finally {
        button.disabled = false;
    }
}
function wire(name) {
    const slow = document.getElementById('readAudioSlow');
    if (slow) {
        slow.addEventListener('click', () =>
            createLessonAudio('reading_slow', slow, 'readingAudio', 'readingAudioError')
        );
    }

    const normal = document.getElementById('readAudioNormal');
    if (normal) {
        normal.addEventListener('click', () =>
            createLessonAudio('reading_normal', normal, 'readingAudio', 'readingAudioError')
        );
    }


    const w = $('#submitWriting');
    if (w) {
        w.onclick = async () => {
            const r = await fetch(`/api/lesson/${day}/writing`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_index: 0, text: $('#writing').value})
            });
            const j = await r.json();
            $('#writingResult').innerHTML = `<div class="result">${esc(j.result.feedback)}</div>`;
        };
    }

    if (name === 'Speaking') wireRecorder();
}
async function submitSpeaking(form){let r=await fetch(`/api/lesson/${day}/speaking`,{method:'POST',body:form}),j=await r.json();$('#speakingResult').innerHTML=`<div class="result">Transcript: ${esc(j.transcript)}<br>${esc(j.result.feedback)}</div>`}
function wireRecorder(){let rec,chunks=[],blob;$('#record').onclick=async()=>{let stream=await navigator.mediaDevices.getUserMedia({audio:true});rec=new MediaRecorder(stream);rec.ondataavailable=e=>chunks.push(e.data);rec.onstop=()=>{blob=new Blob(chunks,{type:rec.mimeType});$('#preview').src=URL.createObjectURL(blob);$('#preview').hidden=false;$('#submitAudio').hidden=false;stream.getTracks().forEach(t=>t.stop())};rec.start();$('#record').hidden=true;$('#stop').hidden=false};$('#stop').onclick=()=>{rec.stop();$('#stop').hidden=true;$('#record').hidden=false};$('#submitAudio').onclick=()=>{let f=new FormData();f.append('audio',blob,'answer.webm');submitSpeaking(f)};$('#submitTyped').onclick=()=>{let f=new FormData();f.append('text',$('#typedSpeaking').value);submitSpeaking(f)}}
$$('.tab').forEach(b=>b.onclick=()=>{$$('.tab').forEach(x=>x.classList.remove('active'));b.classList.add('active');render(b.dataset.section)});render('Reading');
async function sendTutorMessage() {
    const input = document.querySelector('#chatInput');
    const sendButton = document.querySelector('#chatSend');
    const messages = document.querySelector('#messages');

    if (!input || !sendButton || !messages) {
        console.error('Tutor chat elements are missing.');
        return;
    }

    const msg = input.value.trim();
    if (!msg || sendButton.disabled) return;

    messages.insertAdjacentHTML(
        'beforeend',
        `<div class="message you"><small>You</small>${esc(msg)}</div>`
    );
    messages.scrollTop = messages.scrollHeight;

    input.value = '';
    input.disabled = true;
    sendButton.disabled = true;

    const pendingId = `tutor-pending-${Date.now()}`;
    messages.insertAdjacentHTML(
        'beforeend',
        `<div class="message tutorMsg" id="${pendingId}"><small>Tutor</small>Thinking…</div>`
    );
    messages.scrollTop = messages.scrollHeight;

    try {
        const response = await fetch(`/api/chat/${day}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg, history: chatHistory})
        });

        const text = await response.text();
        if (!response.ok) {
            throw new Error(text || `HTTP ${response.status}`);
        }

        chatHistory.push(
            {role: 'user', content: msg},
            {role: 'assistant', content: text}
        );

        const pending = document.getElementById(pendingId);
        if (pending) {
            pending.innerHTML = `<small>Tutor</small>${esc(text)}`;
        }
    } catch (error) {
        console.error('Tutor request failed:', error);
        input.value = msg;
        const pending = document.getElementById(pendingId);
        if (pending) {
            pending.innerHTML = `<small>Tutor</small>Could not send the message. ${esc(error.message)}`;
        }
    } finally {
        input.disabled = false;
        sendButton.disabled = false;
        input.focus();
        messages.scrollTop = messages.scrollHeight;
    }
}

const tutorInput = document.querySelector('#chatInput');
const tutorSendButton = document.querySelector('#chatSend');

if (tutorSendButton) {
    tutorSendButton.addEventListener('click', (event) => {
        event.preventDefault();
        sendTutorMessage();
    });
}

if (tutorInput) {
    tutorInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            event.stopPropagation();
            sendTutorMessage();
        }
    });
}

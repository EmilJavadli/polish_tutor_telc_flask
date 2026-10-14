const lesson=JSON.parse(document.querySelector('#lessonData').textContent),day=window.LESSON_DAY;let panel=document.querySelector('#lessonPanel');let chatHistory=[];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function choices(items,url){let answers={};panel.innerHTML=items.map(q=>`<div class="question"><b>${esc(q.prompt||q.question)}</b>${(q.options||[]).map((o,i)=>`<button data-id="${q.id}" data-a="${i}">${esc(o)}</button>`).join('')}${q.type&&q.type!=='choice'&&q.type!=='multiple_choice'?`<input data-text="${q.id}">`:''}</div>`).join('')+'<button class="primary" id="submitChoices">Submit</button><div id="answerResult"></div>';panel.querySelectorAll('[data-a]').forEach(b=>b.onclick=()=>{panel.querySelectorAll(`[data-id="${b.dataset.id}"]`).forEach(x=>x.classList.remove('selected'));b.classList.add('selected');answers[b.dataset.id]=Number(b.dataset.a)});$('#submitChoices').onclick=async()=>{panel.querySelectorAll('[data-text]').forEach(x=>answers[x.dataset.text]=x.value);let r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answers})}),j=await r.json();$('#answerResult').innerHTML=`<div class="result">Score: ${Math.round(j.score*100)}%</div>`}}
function render(name){if(name==='Reading')panel.innerHTML=`<small class="eyebrow">READING</small><h2>${esc(lesson.title_pl)}</h2><p class="reading">${esc(lesson.reading_pl)}</p><details><summary>Show translation</summary><p>${esc(lesson.reading_en)}</p></details><div class="reading-audio-actions"><button type="button" class="secondary" id="readAudioSlow">Create slow audio</button><button type="button" class="secondary" id="readAudioNormal">Create normal audio</button></div><audio id="readingAudio" controls></audio><div id="readingAudioError"></div>`;
else if(name==='Listening'){panel.innerHTML=`<small class="eyebrow">LISTENING</small><h2>${esc(lesson.listening.situation_en)}</h2><button class="secondary" id="listenAudio">Create listening audio</button><audio id="audio" controls></audio><div id="listenQuestions"></div>`;let root=panel;setTimeout(()=>choicesInto(root.querySelector('#listenQuestions'),lesson.listening.tasks,`/api/lesson/${day}/listening`),0)}
else if(name==='Words')panel.innerHTML=`<small class="eyebrow">VOCABULARY</small><h2>Key words</h2><div class="vocab">${lesson.new_vocabulary.map(w=>`<div><b>${esc(w.polish)}</b><span>${esc(w.english)}</span></div>`).join('')}</div>`;
else if(name==='Grammar')panel.innerHTML=`<small class="eyebrow">GRAMMAR</small>${lesson.grammar_rules.map(g=>`<div class="grammar-card"><h3>${esc(g.title)}</h3><p>${esc(g.explanation)}</p></div>`).join('')}`;
else if(name==='Exercises')choices(lesson.exercises,`/api/lesson/${day}/exercises`);
else if(name==='Quiz')choices(lesson.quiz,`/api/lesson/${day}/quiz`);
else if(name==='Writing')panel.innerHTML=`<small class="eyebrow">WRITING</small><h2>${esc(lesson.writing_tasks[0].situation_en)}</h2><textarea id="writing"></textarea><button class="primary" id="submitWriting">Get feedback</button><div id="writingResult"></div>`;
else if(name==='Speaking')panel.innerHTML=`<small class="eyebrow">SPEAKING</small><h2>${esc(lesson.speaking.title)}</h2><p>${esc(lesson.speaking.instructions_en)}</p><button class="primary" id="record">Start recording</button><button class="secondary" id="stop" hidden>Stop</button><audio id="preview" controls hidden></audio><button class="primary" id="submitAudio" hidden>Submit recording</button><details><summary>Type instead</summary><textarea id="typedSpeaking"></textarea><button class="primary" id="submitTyped">Submit typed answer</button></details><div id="speakingResult"></div>`;
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

    const listening = document.getElementById('listenAudio');
    if (listening) {
        listening.addEventListener('click', () =>
            createLessonAudio('listening', listening, 'audio', 'audioError')
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

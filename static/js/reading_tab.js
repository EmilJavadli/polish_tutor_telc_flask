/* TELC-style Reading tab adapted to real Polish Tutor lesson JSON. */
window.renderTelcReading = function renderTelcReading(lesson, day, panel, esc) {
  const level = ['A1','A2','B1'].includes(lesson.level) ? lesson.level : 'A1';
  const vocab = lesson.new_vocabulary || [];
  const questions = lesson.reading_questions || lesson.reading_tasks || [];
  const state = {step:0, answers:Array(questions.length).fill(null), checked:false, speed:'normal', audioUrl:null};
  const hints = {
    A1:[
      'Read the whole text quickly. What is the main topic? Do not translate every word.',
      'Read again and scan for clear details: names, places, days, times and numbers.',
      'Answer only from information in the text. After checking, return to the exact sentence that supports each answer.'
    ],
    A2:[
      'Skim for the main message, text type and purpose. Keep moving when one word is unfamiliar.',
      'Scan again for specific information, reasons, changes and practical details.',
      'Answer from textual evidence. Use the surrounding sentence to resolve unfamiliar vocabulary.'
    ],
    B1:[
      'Skim for purpose, viewpoint and overall structure before focusing on detail.',
      'Scan for arguments, contrast, reasons and links between ideas. Notice discourse markers.',
      'Answer from evidence in the text, not from general knowledge. Re-check the relevant passage before changing an answer.'
    ]
  }[level];

  function words(text) {
    let html = esc(text || '');
    const entries = vocab
      .map((v, i) => ({v, i, forms:[v.form_in_story, v.polish].filter(Boolean)}))
      .flatMap(x => x.forms.map(form => ({...x, form})))
      .sort((a, b) => b.form.length - a.form.length);

    const placeholders = [];
    for (const entry of entries) {
      const safe = esc(entry.form);
      if (!safe) continue;
      const escapedPattern = safe.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const pattern = new RegExp(`(^|[^A-Za-zÀ-žĄĆĘŁŃÓŚŹŻąćęłńóśźż])(${escapedPattern})(?=$|[^A-Za-zÀ-žĄĆĘŁŃÓŚŹŻąćęłńóśźż])`, 'giu');
      html = html.replace(pattern, (match, prefix, word) => {
        const token = `@@VOCAB_${placeholders.length}@@`;
        placeholders.push(`<span class="read-word new" data-vocab="${entry.i}">${word}</span>`);
        return `${prefix}${token}`;
      });
    }
    placeholders.forEach((markup, i) => { html = html.replace(`@@VOCAB_${i}@@`, markup); });
    return html;
  }

  panel.innerHTML = `
    <div class="read-wrap">
      <div class="read-head">
        <span class="read-eyebrow">📖 READING · DAY ${day}</span>
        <div class="read-chips"><span class="read-chip">⏱ ~10 min</span><span class="read-chip">${(lesson.reading_pl||'').trim().split(/\s+/).filter(Boolean).length} words</span><span class="read-chip read-level">${level}</span></div>
      </div>
      <h2 class="read-title">${esc(lesson.title_pl)}</h2>
      <div class="read-steps" id="readSteps">${['Skim: main topic','Scan: key details','Answer from the text'].map((x,i)=>`<button type="button" class="read-step ${i===0?'active':''}" data-step="${i}"><span>${i+1}</span>${x}</button>`).join('')}</div>
      <p class="read-step-hint" id="readHint"></p>
      <div class="read-split">
        <section class="read-card">
          <div class="read-toolbar">
            <button type="button" class="read-play" id="readPlay">▶</button>
            <div class="read-seg" id="readSpeed"><button type="button" data-speed="slow">🐢 Slow</button><button type="button" data-speed="normal" class="on">Normal</button></div>
            <div class="read-toolbar-right"><button type="button" class="read-icon" id="readNewWords">✨ New words</button><button type="button" class="read-icon" id="readTranslation">🇬🇧 Translation</button><div class="read-seg" id="readFont"><button data-font="16">A−</button><button data-font="18" class="on">A</button><button data-font="21">A+</button></div></div>
          </div>
          <article class="read-letter"><div class="read-text" id="readText"><p>${words(lesson.reading_pl)}</p><p class="read-translation" id="readTranslationText">${esc(lesson.reading_en)}</p></div></article>
          <div class="read-audio-error" id="readAudioError"></div>
          <audio id="readAudioElement" preload="metadata"></audio>
        </section>
        <aside class="read-card read-questions"><div class="read-q-head"><h3>Questions</h3><div class="read-dots" id="readDots"></div></div><div id="readQuestionWrap"></div><div class="read-score" id="readScore"></div></aside>
      </div>
      <div class="read-pop" id="readPop"></div>
      <div class="read-actions"><span id="readBarInfo">Step 1 of 3</span><button class="secondary" id="readReset">Reset</button><button class="primary" id="readNext">Next step →</button></div>
    </div>`;

  const $ = id => document.getElementById(id);
  let audio = $('readAudioElement');

  function setStep(n) {
    state.step = n;
    panel.querySelectorAll('.read-step').forEach((b,i)=>{b.classList.toggle('active',i===n);b.classList.toggle('done',i<n)});
    $('readHint').textContent = hints[n];
    renderQuestions();
  }
  panel.querySelectorAll('.read-step').forEach(b=>b.onclick=()=>setStep(Number(b.dataset.step)));

  function renderQuestions() {
    const answered = state.answers.filter(v=>v!==null).length;
    $('readDots').innerHTML = questions.map((q,i)=>`<span class="${state.checked?(state.answers[i]===q.correct_option||state.answers[i]===q.answer?'ok':'bad'):(state.answers[i]!==null?'done':'')}"></span>`).join('');
    if (state.step < 2) {
      $('readQuestionWrap').innerHTML = `<div class="read-locked">🔒 <b>${questions.length || 'Reading'} questions</b> ${questions.length?'unlock in step 3.':'are not included in this lesson yet.'}<br>First get the main idea, then scan for details.</div>`;
      $('readNext').textContent='Next step →'; $('readNext').disabled=false; $('readBarInfo').textContent=`Step ${state.step+1} of 3`; return;
    }
    if (!questions.length) {
      $('readQuestionWrap').innerHTML='<div class="read-locked"><b>No reading questions were generated for this lesson.</b><br>The redesigned reader is fully active; add <code>reading_questions</code> to the lesson generator to enable the TELC question pane.</div>';
      $('readNext').disabled=true; $('readBarInfo').textContent='Reading review'; return;
    }
    $('readQuestionWrap').innerHTML=`<div class="read-q-body">${questions.map((q,qi)=>`<div class="read-q ${state.checked?'locked':''}"><div class="read-q-text"><span>${qi+1}.</span>${esc(q.question||q.q)}</div>${(q.options||q.opts||[]).map((o,oi)=>{let cls='read-opt',mark='';const correct=q.correct_option??q.answer;if(state.checked){if(oi===correct){cls+=' correct';mark='✓'}else if(state.answers[qi]===oi){cls+=' wrong';mark='✕'}}else if(state.answers[qi]===oi)cls+=' selected';return `<button type="button" class="${cls}" data-q="${qi}" data-a="${oi}"><span class="read-key">${'ABC'[oi]||oi+1}</span>${esc(o)}<span class="read-mark">${mark}</span></button>`}).join('')}${state.checked?`<div class="read-evidence"><b>Evidence:</b> ${esc(q.evidence||'Review the reading text.')}<br><span>${esc(q.explanation||'')}</span></div>`:''}</div>`).join('')}</div>`;
    panel.querySelectorAll('.read-opt').forEach(b=>b.onclick=()=>{if(state.checked)return;state.answers[Number(b.dataset.q)]=Number(b.dataset.a);renderQuestions()});
    $('readNext').textContent='Check answers'; $('readNext').disabled=state.checked||answered<questions.length; $('readBarInfo').textContent=state.checked?'Review the evidence in the text.':`${answered} of ${questions.length} answered`;
  }

  async function ensureAudio() {
    if (state.audioUrl) return true;
    $('readPlay').disabled=true; $('readPlay').textContent='…';
    try {
      const kind = state.speed === 'slow' ? 'reading_slow' : 'reading_normal';
      const r=await fetch(`/api/lesson/${day}/audio/${kind}`,{method:'POST',cache:'no-store'});
      if(!r.ok)throw new Error((await r.text())||`HTTP ${r.status}`);
      const blob=await r.blob(); if(!blob.size)throw new Error('Empty audio returned by server.');
      state.audioUrl=URL.createObjectURL(blob);audio.src=state.audioUrl;$('readPlay').textContent='▶';return true;
    }catch(e){$('readAudioError').textContent=`Audio creation failed: ${e.message}`;$('readPlay').textContent='▶';return false}finally{$('readPlay').disabled=false}
  }
  $('readPlay').onclick=async()=>{if(!(await ensureAudio()))return;if(audio.paused){audio.playbackRate=state.speed==='slow'?.8:1;await audio.play()}else audio.pause()};
  audio.onplay=()=>$('readPlay').textContent='❚❚'; audio.onpause=()=>$('readPlay').textContent='▶';
  panel.querySelectorAll('#readSpeed button').forEach(b=>b.onclick=()=>{panel.querySelectorAll('#readSpeed button').forEach(x=>x.classList.remove('on'));b.classList.add('on');state.speed=b.dataset.speed;if(state.audioUrl){URL.revokeObjectURL(state.audioUrl);state.audioUrl=null;audio.removeAttribute('src')}});
  panel.querySelectorAll('#readFont button').forEach(b=>b.onclick=()=>{panel.querySelectorAll('#readFont button').forEach(x=>x.classList.remove('on'));b.classList.add('on');$('readText').style.fontSize=`${b.dataset.font}px`});
  $('readTranslation').onclick=()=>{$('readTranslation').classList.toggle('on');$('readTranslationText').classList.toggle('show')};
  $('readNewWords').onclick=()=>{$('readNewWords').classList.toggle('on');$('readText').classList.toggle('show-new')};
  panel.querySelectorAll('.read-word').forEach(w=>w.onclick=e=>{const v=vocab[Number(w.dataset.v)];const pop=$('readPop');pop.innerHTML=`<b>${esc(v.polish)}</b><small>${esc(v.part_of_speech||'')}</small><p>${esc(v.english)}</p>${v.why_important?`<em>${esc(v.why_important)}</em>`:''}`;pop.style.display='block';const r=e.target.getBoundingClientRect();pop.style.left=`${Math.min(r.left,innerWidth-260)}px`;pop.style.top=`${r.bottom+8}px`});
  document.addEventListener('click',e=>{if(!e.target.closest('.read-word')&&!e.target.closest('.read-pop'))$('readPop').style.display='none'});
  $('readNext').onclick=async()=>{
    if(state.step<2){setStep(state.step+1);return;}
    if(!questions.length)return;
    const answers=Object.fromEntries(questions.map((q,i)=>[String(q.id),state.answers[i]]));
    const response=await fetch(`/api/lesson/${day}/reading`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answers})});
    const result=await response.json();
    if(!response.ok){$('readScore').innerHTML=`<span>Could not check answers: ${esc(result.error||'Request failed')}</span>`;$('readScore').classList.add('show');return;}
    state.checked=true;renderQuestions();
    $('readScore').innerHTML=`<b>${Math.round(result.score*100)}%</b><span>Review the marked answers and return to the evidence in the text.</span>`;
    $('readScore').classList.add('show');
  };
  $('readReset').onclick=()=>{state.answers.fill(null);state.checked=false;$('readScore').classList.remove('show');setStep(0)};
  setStep(0);
};

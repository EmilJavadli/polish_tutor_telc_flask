/* TELC-style Listening tab. Loaded before lesson.js. */
window.renderTelcListening = function renderTelcListening(
  lesson,
  day,
  panel,
  esc,
) {
  const listening = lesson.listening || {};
  const tasks = listening.tasks || [];
  const lines = listening.lines || [];
  const level = ["A1", "A2", "B1"].includes(lesson.level) ? lesson.level : "A1";
  const answers = Array(tasks.length).fill(null);
  let checked = false;
  let audioUrl = null;
  let audio = null;
  let plays = 0;

  const strategy = {
    A1: "Read the questions first. On the first play, listen for the situation and main message. On the second play, check who, where, when and what.",
    A2: "Read the questions first. On the first play, identify the situation and intention. On the second play, confirm practical details, reasons, changes and required actions.",
    B1: "Read the questions before listening. Use the first play for the overall argument or situation. Use the second play to verify opinions, reasons, implied meaning and supporting details.",
  }[level];

  panel.innerHTML = `
    <div class="listen-wrap">
      <div class="listen-head">
        <span class="listen-eyebrow">🎧 LISTENING · TELC PREPARATION</span>
        <div class="listen-chips"><span class="listen-chip">⏱ ~6 min</span><span class="listen-chip listen-level">${level}</span></div>
      </div>
      <h2 class="listen-title">${esc(listening.instruction_pl || listening.situation_en || "Listen carefully and choose the correct answer.")}</h2>
      <details class="listen-tip"><summary>TELC strategy</summary><p>${esc(strategy)}</p></details>

      <div class="listen-player" id="listenPlayer">
        <div class="listen-player-row">
          <button type="button" class="listen-play" id="listenPlay" aria-label="Create and play audio">▶</button>
          <div class="listen-player-main">
            <div class="listen-player-top"><span id="listenNow"><b>Lesson recording</b> · ${esc(listening.situation_en || "Listening")}</span><span id="listenTime">Audio not created</span></div>
            <div class="listen-track" id="listenTrack"><div class="listen-fill" id="listenFill"></div></div>
            <div class="listen-segments" id="listenSegments"></div>
          </div>
          <div class="listen-player-side">
            <div class="listen-plays">Plays <i id="listenPlay1"></i><i id="listenPlay2"></i></div>
            <select class="listen-speed" id="listenSpeed"><option value="0.75">0.75×</option><option value="1" selected>1×</option></select>
          </div>
        </div>
        <audio id="listenAudioElement" preload="metadata"></audio>
        <div id="listenAudioError"></div>
      </div>

      <div class="listen-progress"><div class="listen-dots" id="listenDots"></div><span id="listenProgressText">0 of ${tasks.length} answered</span></div>
      <div id="listenQuestions"></div>
      <div class="listen-result" id="listenResult"></div>
      <div class="listen-actions"><button type="button" class="secondary" id="listenReset">Reset</button><button type="button" class="primary" id="listenCheck" disabled>Check answers</button></div>
    </div>`;

  const $ = (id) => document.getElementById(id);
  audio = $("listenAudioElement");

  function letters(i) {
    return ["A", "B", "C", "D"][i] || String(i + 1);
  }
  function fmt(seconds) {
    if (!Number.isFinite(seconds)) return "0:00";
    return `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, "0")}`;
  }
  function renderQuestions() {
    $("listenQuestions").innerHTML = tasks
      .map(
        (q, qi) => `
      <section class="listen-q ${checked ? "locked" : ""}">
        <div class="listen-q-head"><span>QUESTION ${qi + 1}</span><span class="listen-q-msg">🎙 Recording</span></div>
        <div class="listen-q-text">${esc(q.question)}</div>
        ${(q.options || [])
          .map((option, oi) => {
            let cls = "listen-opt",
              mark = "";
            if (checked) {
              if (oi === q.correct_option) {
                cls += " correct";
                mark = "✓";
              } else if (answers[qi] === oi) {
                cls += " wrong";
                mark = "✕";
              }
            } else if (answers[qi] === oi) cls += " selected";
            return `<button type="button" class="${cls}" data-question="${qi}" data-option="${oi}"><span class="listen-key">${letters(oi)}</span><span>${esc(option)}</span><span class="listen-mark">${mark}</span></button>`;
          })
          .join("")}
        ${checked ? `<div class="listen-explain">💬 Listen again and locate the exact words that support the correct answer.</div>` : ""}
      </section>`,
      )
      .join("");

    panel.querySelectorAll(".listen-opt").forEach((button) =>
      button.addEventListener("click", () => {
        if (checked) return;
        answers[Number(button.dataset.question)] = Number(
          button.dataset.option,
        );
        renderQuestions();
        updateProgress();
      }),
    );
  }
  function updateProgress() {
    const count = answers.filter((x) => x !== null).length;
    $("listenDots").innerHTML = tasks
      .map((q, i) => {
        let cls = answers[i] === null ? "" : "done";
        if (checked) cls = answers[i] === q.correct_option ? "ok" : "bad";
        return `<span class="${cls}"></span>`;
      })
      .join("");
    $("listenProgressText").textContent =
      `${count} of ${tasks.length} answered`;
    $("listenCheck").disabled = checked || count < tasks.length;
  }
  async function ensureAudio() {
    if (audioUrl) return true;
    const play = $("listenPlay");
    const previous = play.textContent;
    play.disabled = true;
    play.textContent = "…";
    $("listenTime").textContent = "Creating audio…";
    try {
      const response = await fetch(`/api/lesson/${day}/audio/listening`, {
        method: "POST",
        cache: "no-store",
      });
      if (!response.ok)
        throw new Error((await response.text()) || `HTTP ${response.status}`);
      const blob = await response.blob();
      if (!blob.size) throw new Error("Empty audio returned by server.");
      audioUrl = URL.createObjectURL(blob);
      audio.src = audioUrl;
      await new Promise((resolve) =>
        audio.addEventListener("loadedmetadata", resolve, { once: true }),
      );
      $("listenTime").textContent = `0:00 / ${fmt(audio.duration)}`;
      play.textContent = "▶";
      renderSegments();
      return true;
    } catch (error) {
      play.textContent = previous;
      $("listenTime").textContent = "Audio unavailable";
      $("listenAudioError").innerHTML =
        `<div class="listen-error">Audio creation failed: ${esc(error.message)}</div>`;
      return false;
    } finally {
      play.disabled = false;
    }
  }
  function renderSegments() {
    if (!lines.length) return;
    $("listenSegments").innerHTML = lines
      .map(
        (line, i) =>
          `<button type="button" class="listen-seg" data-line="${i}">${i + 1}. ${esc(line.speaker || "Speaker")}</button>`,
      )
      .join("");
    panel.querySelectorAll(".listen-seg").forEach((button) =>
      button.addEventListener("click", () => {
        if (!audio.duration) return;
        audio.currentTime =
          (audio.duration * Number(button.dataset.line)) / lines.length;
      }),
    );
  }
  $("listenPlay").addEventListener("click", async () => {
    if (!(await ensureAudio())) return;
    if (audio.paused) {
      if (audio.currentTime === 0 || audio.ended) {
        plays += 1;
        if (plays >= 1) $("listenPlay1").classList.add("used");
        if (plays >= 2) $("listenPlay2").classList.add("used");
      }
      audio.playbackRate = Number($("listenSpeed").value);
      await audio.play();
    } else audio.pause();
  });
  $("listenSpeed").addEventListener(
    "change",
    (e) => (audio.playbackRate = Number(e.target.value)),
  );
  audio.addEventListener("play", () => ($("listenPlay").textContent = "❚❚"));
  audio.addEventListener("pause", () => ($("listenPlay").textContent = "▶"));
  audio.addEventListener("timeupdate", () => {
    const pct = audio.duration ? (audio.currentTime / audio.duration) * 100 : 0;
    $("listenFill").style.width = `${pct}%`;
    $("listenTime").textContent =
      `${fmt(audio.currentTime)} / ${fmt(audio.duration)}`;
  });
  $("listenTrack").addEventListener("click", (e) => {
    if (!audio.duration) return;
    const rect = e.currentTarget.getBoundingClientRect();
    audio.currentTime = ((e.clientX - rect.left) / rect.width) * audio.duration;
  });
  $("listenReset").addEventListener("click", () => {
    answers.fill(null);
    checked = false;
    $("listenResult").innerHTML = "";
    renderQuestions();
    updateProgress();
  });
  $("listenCheck").addEventListener("click", async () => {
    const response = await fetch(`/api/lesson/${day}/listening`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        answers: Object.fromEntries(
          answers.map((a, i) => [String(tasks[i].id), a]),
        ),
      }),
    });
    const result = await response.json();
    checked = true;
    renderQuestions();
    updateProgress();
    $("listenResult").innerHTML =
      `<div class="listen-score">${Math.round((result.score || 0) * 100)}%</div><p>${result.score === 1 ? "Świetnie! Perfect score." : "Review the marked questions, then listen again for the supporting detail."}</p>${lines.length ? `<div class="listen-transcript"><b>📝 Transcript</b>${lines.map((line, i) => `<div><b>${esc(line.speaker || `Speaker ${i + 1}`)}:</b> ${esc(line.text)}</div>`).join("")}</div>` : ""}`;
    $("listenResult").classList.add("show");
  });

  renderQuestions();
  updateProgress();
};

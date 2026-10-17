/** Vocabulary component adapted from the user-supplied vocabulary_lesson.html.
 * Shadow DOM preserves the supplied design without leaking styles into other tabs.
 * Uses actual lesson vocabulary; progress stays local to this browser/account/lesson.
 */
window.renderLessonVocabulary = function renderLessonVocabulary(
  lesson,
  day,
  panel,
) {
  const host = document.createElement("div");
  host.className = "lesson-vocabulary-host";
  panel.replaceChildren(host);
  const shadow = host.attachShadow({ mode: "open" });
  shadow.innerHTML = `<style>
:host {
  color-scheme: dark;
  --bg: #0e1015;
  --panel: #161920;
  --line: #2a303d;
  --muted: #a4aec1;
  --pink: #ff5277;
  --green: #51d6a0;
}
* {
  box-sizing: border-box;
}
:host {
  margin: 0;
  background: var(--bg);
  color: #eef1f7;
  font:
    15px "Segoe UI",
    sans-serif;
}
button,
input,
select {
  font: inherit;
}
button,
select {
  cursor: pointer;
}
button {
  color: inherit;
  background: #1c222e;
  border: 1px solid var(--line);
  border-radius: 9px;
  padding: 10px 15px;
}
button:hover {
  border-color: var(--pink);
}
button:focus-visible,
input:focus-visible,
select:focus-visible {
  outline: 2px solid #8baaff;
  outline-offset: 3px;
}
.primary {
  background: var(--pink);
  color: #170a10;
  border-color: var(--pink);
  font-weight: 700;
}
nav {
  padding: 18px 4%;
  border-bottom: 1px solid var(--line);
  color: var(--muted);
}
nav strong {
  color: var(--pink);
  margin: 0 25px;
}
main {
  max-width: 1440px;
  margin: auto;
  padding: 32px 4%;
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}
h1 {
  font-size: 32px;
  margin: 5px 0 8px;
}
p {
  line-height: 1.65;
}
.muted,
small {
  color: var(--muted);
}
.eyebrow {
  color: var(--pink);
  font-size: 12px;
  letter-spacing: 2px;
  font-weight: 700;
}
.stats {
  display: flex;
  gap: 12px;
  margin: 25px 0;
}
.stat {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px 24px;
  flex: 1;
}
.stat b {
  font-size: 24px;
  display: block;
  margin-bottom: 4px;
}
.tools {
  display: flex;
  gap: 10px;
  margin: 22px 0;
  flex-wrap: wrap;
}
input,
select {
  background: var(--panel);
  border: 1px solid var(--line);
  color: inherit;
  padding: 12px;
  border-radius: 9px;
}
input[type="search"] {
  flex: 1;
  min-width: 180px;
}
.layout {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
}
.panel {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 16px;
  overflow: hidden;
}
.list {
  max-height: 570px;
  overflow: auto;
}
.row {
  width: 100%;
  border: 0;
  border-bottom: 1px solid var(--line);
  border-radius: 0;
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  text-align: left;
  gap: 12px;
  padding: 18px 20px;
  background: transparent;
  align-items: center;
}
.row.active {
  background: #30202c;
  box-shadow: inset 3px 0 var(--pink);
}
.row small {
  display: block;
  margin-top: 5px;
}
.badge {
  font-size: 11px;
  padding: 5px 8px;
  border-radius: 20px;
  background: #263143;
  color: #c2d4ff;
}
.detail {
  padding: 28px;
}
.detail h2 {
  font-size: 34px;
  margin: 10px 0;
}
.tag {
  font-size: 12px;
  color: #b9b2ff;
  background: #292541;
  border-radius: 6px;
  padding: 5px 9px;
}
.block {
  border-top: 1px solid var(--line);
  padding-top: 18px;
  margin-top: 22px;
}
.example {
  font-size: 20px;
}
.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 24px;
}
.tip {
  border-left: 3px solid var(--pink);
  padding: 12px 18px;
  background: #1c202a;
  border-radius: 8px;
  margin-top: 24px;
}
.footer {
  font-size: 12px;
  color: var(--muted);
  margin-top: 20px;
}
dialog {
  background: var(--panel);
  color: inherit;
  border: 1px solid var(--line);
  border-radius: 20px;
  padding: 28px;
  width: min(560px, 92vw);
}
dialog::backdrop {
  background: #000b;
  backdrop-filter: blur(5px);
}
.flash {
  text-align: center;
  padding: 30px 5px;
}
.flash h2 {
  font-size: 36px;
}
.flash button {
  margin: 5px;
}
.close {
  float: right;
}
#notice {
  min-height: 24px;
  color: var(--green);
  margin-top: 12px;
}
progress {
  width: 100%;
  accent-color: var(--pink);
}
@media (max-width: 800px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .list {
    max-height: 320px;
  }
  header {
    align-items: flex-start;
    flex-direction: column;
  }
  .stats {
    gap: 6px;
  }
  .stat {
    padding: 12px;
  }
  .stat b {
    font-size: 20px;
  }
  nav {
    font-size: 12px;
  }
  .row {
    grid-template-columns: 1fr 1fr auto;
  }
  .detail {
    padding: 20px;
  }
}

:host {
  display: block;
  min-width: 0;
}
main {
  padding: 0;
  max-width: none;
}
header h1 {
  letter-spacing: normal;
}
button {
  min-height: 40px;
}
input {
  min-width: 0;
}
.layout > * {
  min-width: 0;
}
.row > * {
  overflow-wrap: anywhere;
}
dialog {
  max-height: 85vh;
  overflow: auto;
}
.empty {
  padding: 24px;
}
.sentence-input {
  width: 100%;
}
.save-button {
  margin-top: 10px;
}
.footer {
  line-height: 1.6;
}
</style><main><header><div><div class="eyebrow">YOUR DAILY POLISH · <span id="vocabLevel"></span></div><h1>Words for real life.</h1><div class="muted">Learn the expression. Remember the meaning. Make it yours.</div></div><button class="primary" id="start">Start flashcards →</button></header><div class="stats"><div class="stat"><b id="total"></b><small>Lesson words</small></div><div class="stat"><b id="learning"></b><small>Learning</small></div><div class="stat"><b id="known"></b><small>Marked known</small></div></div><div class="tools"><input aria-label="Search vocabulary" id="search" placeholder="Search in Polish or English..." type="search"/><select aria-label="Filter by status" id="filter"><option value="all">All words</option><option>New</option><option>Learning</option><option>Known</option></select><button id="hide">Hide meanings</button></div><div class="layout"><section aria-label="Vocabulary words" class="panel list" id="list"></section><section aria-label="Selected word details" class="panel detail" id="detail"></section></div><div class="tip"><b>A little practice, not just a word list.</b><br/><span class="muted">Read the phrase aloud, hide its meaning, then write one sentence about your day.</span></div><div class="footer">Progress and personal sentences are saved in this browser when storage is available, separately for your account and lesson. Pronunciation uses the device voice, if supported.</div></main><dialog id="review" aria-label="Vocabulary flashcards"><button aria-label="Close flashcards" class="close" id="close">✕</button><small id="counter"></small><progress id="progress"></progress><div class="flash" id="flash"></div></dialog>`;
  shadow.getElementById("vocabLevel").textContent = lesson.level || "A1";
  const vocabulary = Array.isArray(lesson.new_vocabulary)
    ? lesson.new_vocabulary
    : [];
  const words = vocabulary.map((item) =>
    [
      item.polish || "",
      item.english || "",
      item.part_of_speech || "",
      item.useful_expression || item.form_in_story || item.polish || "",
      item.example_pl || "",
      item.example_en || "",
    ].map(String),
  );
  const userScope = panel.dataset.vocabularyUser;
  // Never share browser progress between accounts or regenerated lesson contents.
  const storageKey = userScope
    ? "polski-vocab-v2:" +
      JSON.stringify([userScope, day, lesson.created || "", words])
    : "polski-vocab-ephemeral:" + String(Math.random());
  let saved = {};
  try {
    saved = JSON.parse(localStorage.getItem(storageKey) || "{}");
  } catch {}
  if (!saved || typeof saved !== "object" || Array.isArray(saved)) saved = {};
  let selected = 0,
    hidden = false,
    queue = [],
    position = 0,
    revealed = false;
  const $ = (id) => shadow.getElementById(id);
  const esc = (s) =>
    String(s).replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  function state(i) {
    const status = saved[i]?.status;
    return ["New", "Learning", "Known"].includes(status) ? status : "New";
  }
  function store() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(saved));
      return true;
    } catch {
      return false;
    }
  }
  function mark(i, status) {
    saved[i] = { ...saved[i], status };
    store();
    render();
  }
  function render() {
    const q = $("search").value.toLocaleLowerCase("pl"),
      f = $("filter").value;
    const ids = words
      .map((_, i) => i)
      .filter(
        (i) =>
          (f === "all" || state(i) === f) &&
          words[i].join(" ").toLocaleLowerCase("pl").includes(q),
      );
    $("list").innerHTML = ids.length
      ? ids
          .map(
            (i) =>
              `<button class="row ${i === selected ? "active" : ""}" data-id="${i}" aria-pressed="${i === selected}"><span><b lang="pl">${esc(words[i][0])}</b><small>${esc(words[i][2])}</small></span><span class="muted">${hidden ? "••••••" : esc(words[i][1])}</span><span class="badge">${state(i)}</span></button>`,
          )
          .join("")
      : '<p style="padding:20px">No matching words. Try another search or filter.</p>';
    $("total").textContent = words.length;
    $("learning").textContent = words.filter(
      (_, i) => state(i) === "Learning",
    ).length;
    $("known").textContent = words.filter(
      (_, i) => state(i) === "Known",
    ).length;
    detail();
  }
  function detail() {
    const w = words[selected];
    if (!w) {
      $("detail").innerHTML =
        '<p class="muted">No vocabulary was included in this lesson.</p>';
      return;
    }
    $("detail").innerHTML =
      `<div class="eyebrow">WORD IN FOCUS <span class="badge">${state(selected)}</span></div><h2 lang="pl">${esc(w[0])}</h2><span class="tag">${esc(w[2])}</span><p class="muted">${hidden ? "Meaning hidden. Reveal it when you are ready." : esc(w[1])}</p><button id="speak">▶ Listen</button> <button id="slow">▶ Slow</button><div class="block"><small>USEFUL EXPRESSION</small><p class="example" lang="pl">${esc(w[3])}</p><small>IN A SENTENCE</small><p lang="pl">${esc(w[4])}</p><p class="muted">${hidden ? "Translation hidden" : esc(w[5])}</p></div><div class="block"><label for="sentence">Make it yours</label><p class="muted">Write one Polish sentence using this word.</p><input style="width:100%" id="sentence" placeholder="Moje zdanie..." value="${esc(saved[selected]?.sentence || "")}"><button style="margin-top:10px" id="save">Save sentence</button><div id="notice" role="status"></div></div><div class="actions"><button data-status="New">New</button><button data-status="Learning">Still learning</button><button data-status="Known">✓ I know this</button></div>`;
    $("sentence").oninput = () => {
      saved[selected] = { ...saved[selected], sentence: $("sentence").value };
      store();
    };
    $("speak").onclick = () => speak(w[0], 1);
    $("slow").onclick = () => speak(w[0], 0.7);
    $("save").onclick = () => {
      saved[selected] = { ...saved[selected], sentence: $("sentence").value };
      store();
      $("notice").textContent = "Sentence saved for this browser session.";
    };
    shadow
      .querySelectorAll("[data-status]")
      .forEach((b) => (b.onclick = () => mark(selected, b.dataset.status)));
  }
  function speak(text, rate) {
    if (
      !("speechSynthesis" in window) ||
      !("SpeechSynthesisUtterance" in window)
    ) {
      $("notice").textContent = "Speech is unavailable in this browser.";
      return;
    }
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "pl-PL";
    u.rate = rate;
    const voice = speechSynthesis
      .getVoices()
      .find((v) => v.lang.toLowerCase().startsWith("pl"));
    if (voice) u.voice = voice;
    u.onerror = () => {
      if ($("notice"))
        $("notice").textContent =
          "Pronunciation could not play. Check device voices and audio settings.";
    };
    speechSynthesis.speak(u);
  }
  $("list").onclick = (e) => {
    const b = e.target.closest("[data-id]");
    if (b) {
      selected = +b.dataset.id;
      render();
    }
  };
  $("search").oninput = render;
  $("filter").onchange = render;
  $("hide").onclick = () => {
    hidden = !hidden;
    $("hide").textContent = hidden ? "Show meanings" : "Hide meanings";
    render();
  };
  $("start").disabled = !words.length;
  $("start").onclick = () => {
    queue = words.map((_, i) => i).filter((i) => state(i) !== "Known");
    if (!queue.length) queue = words.map((_, i) => i);
    position = 0;
    revealed = false;
    flash();
    $("review").showModal();
  };
  $("close").onclick = () => $("review").close();
  $("review").addEventListener("close", () => {
    if ("speechSynthesis" in window) speechSynthesis.cancel();
  });
  function flash() {
    if (position >= queue.length) {
      $("counter").textContent = "Session complete";
      $("progress").value = 1;
      $("progress").max = 1;
      $("flash").innerHTML =
        '<h2>Nice work.</h2><p>You have reviewed every card in this session.</p><button id="done" class="primary">Back to vocabulary</button>';
      $("done").onclick = () => $("review").close();
      return;
    }
    const w = words[queue[position]];
    $("counter").textContent = `CARD ${position + 1} OF ${queue.length}`;
    $("progress").max = queue.length;
    $("progress").value = position;
    $("flash").innerHTML =
      `<p class="muted">Recall the English meaning</p><h2 lang="pl">${esc(w[0])}</h2><p lang="pl">${esc(w[3])}</p>${revealed ? `<p class="example">${esc(w[1])}</p><p>${esc(w[4])}</p><p class="muted">${esc(w[5])}</p><button id="again">Still learning</button><button id="know" class="primary">I remembered</button>` : '<button id="reveal" class="primary">Reveal meaning</button>'}`;
    if (revealed) {
      $("again").onclick = () => advance("Learning");
      $("know").onclick = () => advance("Known");
    } else
      $("reveal").onclick = () => {
        revealed = true;
        flash();
      };
  }
  function advance(status) {
    mark(queue[position], status);
    position++;
    revealed = false;
    flash();
  }
  render();
};

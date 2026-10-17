/* Shared DOM helpers. Loaded before lesson-specific scripts. */
const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const generateButton = $("#generateLesson");
if (generateButton) {
  generateButton.addEventListener("click", async () => {
    const status = $("#generateStatus");
    generateButton.disabled = true;
    status.textContent = "Generating and validating your lesson...";
    try {
      const response = await fetch("/api/lesson/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({ day: Number(generateButton.dataset.day) }),
      });
      const text = await response.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch {
        throw new Error(
          `Server returned HTTP ${response.status}. Check the server logs.`,
        );
      }
      if (!response.ok)
        throw new Error(
          [data.error, data.reference].filter(Boolean).join(" ") ||
            "Generation failed.",
        );
      window.location.reload();
    } catch (error) {
      status.textContent = error.message;
      generateButton.disabled = false;
    }
  });
}

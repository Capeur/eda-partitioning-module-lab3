// Renders quiz.json (embedded as #quiz-data) as a self-check form.
(function () {
  const dataEl = document.getElementById("quiz-data");
  const root = document.getElementById("quiz-root");
  if (!dataEl || !root) return;
  const quiz = JSON.parse(dataEl.textContent);
  const t = root.dataset; // labels in the page language

  const ol = document.createElement("ol");

  quiz.items.forEach((item, i) => {
    const li = document.createElement("li");
    const q = document.createElement("div");
    q.className = "q";
    q.textContent = item.prompt;
    li.append(q);
    const choices = item.type === "true_false" ? [t.true || "True", t.false || "False"] : item.choices;
    choices.forEach((text, c) => {
      const label = document.createElement("label");
      const input = document.createElement("input");
      input.type = "radio";
      input.name = `q${i}`;
      input.value = String(c);
      label.append(input, document.createTextNode(text));
      li.append(label);
    });
    const why = document.createElement("p");
    why.className = "why";
    why.hidden = true;
    why.textContent = item.explain || "";
    li.append(why);
    ol.append(li);
  });

  const check = document.createElement("button");
  check.className = "btn primary";
  check.type = "button";
  check.textContent = t.check || "Check my answers";
  const reset = document.createElement("button");
  reset.className = "btn";
  reset.type = "button";
  reset.textContent = t.reset || "Reset";
  const score = document.createElement("span");
  score.className = "score";
  const bar = document.createElement("div");
  bar.className = "btns";
  bar.append(check, reset, score);
  root.append(ol, bar);

  const correctIndex = (item) =>
    item.type === "true_false" ? (item.answer ? 0 : 1) : item.answer;

  check.addEventListener("click", () => {
    let right = 0;
    quiz.items.forEach((item, i) => {
      const li = ol.children[i];
      const labels = li.querySelectorAll("label");
      const picked = li.querySelector("input:checked");
      labels.forEach((l) => l.classList.remove("good", "bad"));
      labels[correctIndex(item)].classList.add("good");
      if (picked && Number(picked.value) === correctIndex(item)) right += 1;
      else if (picked) picked.parentElement.classList.add("bad");
      li.querySelector(".why").hidden = false;
    });
    const pass = right / quiz.items.length >= (quiz.passing_score ?? 0.67);
    score.textContent = `${right} / ${quiz.items.length} — ${pass ? t.pass || "passed" : t.fail || "try again"}`;
  });

  reset.addEventListener("click", () => {
    ol.querySelectorAll("input").forEach((x) => (x.checked = false));
    ol.querySelectorAll("label").forEach((l) => l.classList.remove("good", "bad"));
    ol.querySelectorAll(".why").forEach((w) => (w.hidden = true));
    score.textContent = "";
  });
})();

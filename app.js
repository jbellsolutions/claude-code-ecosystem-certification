const dataUrl = "site/data/course-data.json";

async function fetchText(path) {
  const response = await fetch(path);
  if (!response.ok) {
    return "";
  }
  return response.text();
}

function makeChip(text) {
  const chip = document.createElement("span");
  chip.className = "stat-chip";
  chip.textContent = text;
  return chip;
}

function makePill(text) {
  const pill = document.createElement("span");
  pill.className = "pill";
  pill.textContent = text;
  return pill;
}

function makeCheck(text) {
  const row = document.createElement("div");
  row.className = "check-item";
  const label = document.createElement("div");
  label.textContent = text;
  row.append(label);
  return row;
}

function transcriptSnippet(text) {
  const clean = text.replace(/\s+/g, " ").trim();
  return clean.length > 360 ? `${clean.slice(0, 360).trim()}...` : clean;
}

async function buildModuleCard(module) {
  const article = document.createElement("article");
  article.className = "module-card reveal";

  const poster = document.createElement("img");
  poster.className = "module-poster";
  poster.src = module.poster;
  poster.alt = `${module.title} poster frame`;
  article.append(poster);

  const copy = document.createElement("div");
  copy.className = "module-copy";

  const meta = document.createElement("div");
  meta.className = "module-meta";
  meta.innerHTML = `
    <span class="module-order">${module.orderLabel}</span>
    <span class="module-duration">${module.duration}</span>
  `;
  copy.append(meta);

  const title = document.createElement("h3");
  title.className = "module-title";
  title.textContent = module.title;
  copy.append(title);

  const headline = document.createElement("p");
  headline.className = "module-headline";
  headline.textContent = module.headline;
  copy.append(headline);

  const subheadline = document.createElement("p");
  subheadline.className = "module-subheadline";
  subheadline.textContent = module.subheadline;
  copy.append(subheadline);

  const focusList = document.createElement("div");
  focusList.className = "focus-list";
  module.focus.forEach((item) => {
    const pill = document.createElement("span");
    pill.className = "focus-pill";
    pill.textContent = item;
    focusList.append(pill);
  });
  copy.append(focusList);

  const details = document.createElement("details");
  details.className = "transcript-toggle";
  const summary = document.createElement("summary");
  summary.textContent = "Transcript Excerpt";
  details.append(summary);
  const snippet = document.createElement("p");
  snippet.className = "transcript-snippet";
  snippet.textContent = "Loading excerpt...";
  details.append(snippet);
  copy.append(details);

  article.append(copy);

  fetchText(module.transcript)
    .then((text) => {
      snippet.textContent = transcriptSnippet(text);
    })
    .catch(() => {
      snippet.textContent = "Transcript excerpt unavailable in this preview.";
    });

  return article;
}

function setupReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  document.querySelectorAll(".reveal").forEach((node) => observer.observe(node));
}

async function init() {
  const response = await fetch(dataUrl);
  const data = await response.json();

  document.getElementById("hero-kicker").textContent = data.kicker;
  document.getElementById("hero-title").textContent = data.title;
  document.getElementById("hero-headline").textContent = data.headline;
  document.getElementById("hero-subheadline").textContent = data.subheadline;

  const statRibbon = document.getElementById("stat-ribbon");
  statRibbon.append(
    makeChip(`${data.stats.lessonCount} source-order modules`),
    makeChip(`${data.stats.runtime} total runtime`),
    makeChip(data.stats.format)
  );

  const audienceList = document.getElementById("audience-list");
  data.audience.forEach((item) => audienceList.append(makePill(item)));

  const outcomeList = document.getElementById("outcome-list");
  data.outcomes.forEach((item) => outcomeList.append(makeCheck(item)));

  const noteList = document.getElementById("note-list");
  data.notes.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    noteList.append(li);
  });

  const moduleGrid = document.getElementById("module-grid");
  for (const module of data.modules) {
    const card = await buildModuleCard(module);
    moduleGrid.append(card);
  }

  setupReveal();
}

init().catch((error) => {
  console.error(error);
});

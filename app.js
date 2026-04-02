const dataUrl = "site/data/course-data.json";
const sessionKey = "plotCodeCertificationUser";

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

function createModuleCard(module) {
  const article = document.createElement("article");
  article.className = "module-card reveal";

  const video = document.createElement("video");
  video.controls = true;
  video.preload = "none";
  video.poster = module.poster;
  video.src = module.video;
  article.append(video);

  const body = document.createElement("div");
  body.className = "module-body";

  const meta = document.createElement("div");
  meta.className = "module-meta";
  meta.innerHTML = `
    <span class="module-order">${module.orderLabel}</span>
    <span class="module-duration">${module.duration}</span>
  `;
  body.append(meta);

  const title = document.createElement("h3");
  title.className = "module-title";
  title.textContent = module.title;
  body.append(title);

  const headline = document.createElement("p");
  headline.className = "module-headline";
  headline.textContent = module.headline;
  body.append(headline);

  const subheadline = document.createElement("p");
  subheadline.className = "module-subheadline";
  subheadline.textContent = module.subheadline;
  body.append(subheadline);

  const tags = document.createElement("div");
  tags.className = "module-tags";
  ["Video lesson", "Checklist exercise", "Level one curriculum"].forEach((text) => {
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = text;
    tags.append(tag);
  });
  body.append(tags);

  const lessonBlock = document.createElement("div");
  lessonBlock.className = "lesson-block";

  const heading = document.createElement("h4");
  heading.textContent = "Checklist Of What They Learned";
  lessonBlock.append(heading);

  const checklist = document.createElement("div");
  checklist.className = "module-checklist";
  module.focus.forEach((item, index) => {
    const row = document.createElement("label");
    const input = document.createElement("input");
    input.type = "checkbox";
    input.name = `${module.id}-${index}`;
    const text = document.createElement("span");
    text.textContent = item;
    row.append(input, text);
    checklist.append(row);
  });
  lessonBlock.append(checklist);
  body.append(lessonBlock);

  article.append(body);
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

function setRevealState(rootSelector, isVisible) {
  document.querySelectorAll(`${rootSelector} .reveal`).forEach((node) => {
    node.classList.toggle("is-visible", isVisible);
  });
}

function updateAuthView() {
  const user = localStorage.getItem(sessionKey);
  const authView = document.getElementById("auth-view");
  const portalView = document.getElementById("portal-view");
  const logoutButton = document.getElementById("logout-button");
  const portalTitle = document.getElementById("portal-title");

  if (user) {
    authView.classList.add("hidden");
    portalView.classList.remove("hidden");
    logoutButton.classList.remove("hidden");
    portalTitle.textContent = `Welcome, ${user}`;
    setRevealState("#portal-view", true);
  } else {
    authView.classList.remove("hidden");
    portalView.classList.add("hidden");
    logoutButton.classList.add("hidden");
    setRevealState("#auth-view", true);
  }

  setupReveal();
}

async function init() {
  const response = await fetch(dataUrl);
  const data = await response.json();

  document.title = data.title;
  document.getElementById("hero-kicker").textContent = data.kicker;
  document.getElementById("hero-title").textContent = data.title;
  document.getElementById("hero-headline").textContent = data.headline;
  document.getElementById("hero-subheadline").textContent = data.subheadline;
  document.getElementById("login-title").textContent = data.login.title;
  document.getElementById("login-subheadline").textContent = data.login.subheadline;

  const statRibbon = document.getElementById("stat-ribbon");
  statRibbon.append(
    makeChip(`${data.stats.lessonCount} video modules`),
    makeChip(`${data.stats.runtime} total runtime`),
    makeChip(data.stats.format)
  );

  const audienceList = document.getElementById("audience-list");
  data.audience.forEach((item) => audienceList.append(makePill(item)));

  const outcomeList = document.getElementById("outcome-list");
  data.outcomes.forEach((item) => outcomeList.append(makeCheck(item)));

  const moduleGrid = document.getElementById("module-grid");
  data.modules.forEach((module) => moduleGrid.append(createModuleCard(module)));

  const loginForm = document.getElementById("login-form");
  const feedback = document.getElementById("login-feedback");
  loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!email || !password) {
      feedback.textContent = "Enter both an email and password to continue.";
      return;
    }

    const firstName = email.split("@")[0].replace(/[._-]/g, " ");
    const normalized = firstName.replace(/\b\w/g, (char) => char.toUpperCase());
    localStorage.setItem(sessionKey, normalized || "Member");
    feedback.textContent = "Login successful. Opening the certification portal.";
    updateAuthView();
    document.getElementById("portal-view").scrollIntoView({ behavior: "smooth", block: "start" });
  });

  document.getElementById("logout-button").addEventListener("click", () => {
    localStorage.removeItem(sessionKey);
    updateAuthView();
    window.location.hash = "";
  });

  updateAuthView();
}

init().catch((error) => {
  console.error(error);
});

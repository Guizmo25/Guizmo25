const articlesList = document.querySelector("#articlesList");
const newsForm = document.querySelector("#newsForm");
const refreshBtn = document.querySelector("#refreshBtn");
const seedBtn = document.querySelector("#seedBtn");
const publishedCount = document.querySelector("#publishedCount");
const draftCount = document.querySelector("#draftCount");

const STORAGE_KEY = "habbo_cms_articles";

const demoArticles = [
  {
    id: crypto.randomUUID(),
    title: "Soirée DJ Pixel Night",
    category: "Event",
    status: "Publié",
    summary:
      "Retrouvez l'équipe de modération pour un set live et des lots surprises.",
    date: new Date().toLocaleDateString("fr-FR"),
  },
  {
    id: crypto.randomUUID(),
    title: "Nouveau concours pixel-art",
    category: "Communauté",
    status: "Brouillon",
    summary:
      "Un concours créatif avec des badges exclusifs pour les meilleurs artistes.",
    date: new Date().toLocaleDateString("fr-FR"),
  },
  {
    id: crypto.randomUUID(),
    title: "Boutique : packs hiver",
    category: "Shop",
    status: "Publié",
    summary:
      "Des bundles givrés disponibles toute la semaine dans l'hôtel.",
    date: new Date().toLocaleDateString("fr-FR"),
  },
];

const loadArticles = () => {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(demoArticles));
    return demoArticles;
  }
  return JSON.parse(stored);
};

const saveArticles = (articles) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(articles));
};

const updateCounts = (articles) => {
  const published = articles.filter((article) => article.status === "Publié");
  const drafts = articles.filter((article) => article.status === "Brouillon");
  publishedCount.textContent = published.length;
  draftCount.textContent = drafts.length;
};

const buildArticleCard = (article) => {
  const wrapper = document.createElement("article");
  wrapper.className = "article";

  const meta = document.createElement("div");
  meta.className = "article__meta";

  const title = document.createElement("h4");
  title.textContent = article.title;

  const info = document.createElement("span");
  info.textContent = `${article.category} • ${article.date}`;

  const summary = document.createElement("small");
  summary.textContent = article.summary;

  const badge = document.createElement("span");
  badge.className = `badge ${
    article.status === "Brouillon" ? "badge--draft" : ""
  }`;
  badge.textContent = article.status;

  meta.append(title, info, summary, badge);

  const actions = document.createElement("div");
  actions.className = "article__actions";

  const toggleBtn = document.createElement("button");
  toggleBtn.className = "secondary";
  toggleBtn.textContent =
    article.status === "Publié" ? "Mettre en brouillon" : "Publier";
  toggleBtn.addEventListener("click", () => toggleStatus(article.id));

  const deleteBtn = document.createElement("button");
  deleteBtn.className = "ghost";
  deleteBtn.textContent = "Supprimer";
  deleteBtn.addEventListener("click", () => removeArticle(article.id));

  actions.append(toggleBtn, deleteBtn);

  wrapper.append(meta, actions);
  return wrapper;
};

const renderArticles = () => {
  const articles = loadArticles();
  articlesList.innerHTML = "";

  articles
    .sort((a, b) => b.id.localeCompare(a.id))
    .forEach((article) => articlesList.append(buildArticleCard(article)));

  updateCounts(articles);
};

const addArticle = (data) => {
  const articles = loadArticles();
  articles.unshift({
    id: crypto.randomUUID(),
    title: data.title,
    category: data.category,
    status: data.status,
    summary: data.summary,
    date: new Date().toLocaleDateString("fr-FR"),
  });
  saveArticles(articles);
  renderArticles();
};

const toggleStatus = (id) => {
  const articles = loadArticles();
  const updated = articles.map((article) => {
    if (article.id !== id) return article;
    return {
      ...article,
      status: article.status === "Publié" ? "Brouillon" : "Publié",
    };
  });
  saveArticles(updated);
  renderArticles();
};

const removeArticle = (id) => {
  const articles = loadArticles().filter((article) => article.id !== id);
  saveArticles(articles);
  renderArticles();
};

newsForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const formData = new FormData(newsForm);
  addArticle({
    title: formData.get("title").trim(),
    category: formData.get("category"),
    status: formData.get("status"),
    summary: formData.get("summary").trim(),
  });
  newsForm.reset();
});

refreshBtn.addEventListener("click", () => renderArticles());
seedBtn.addEventListener("click", () => {
  saveArticles(demoArticles);
  renderArticles();
});

renderArticles();

(async function () {
  'use strict';

  const BRANCH_NAME = 'main';

  const DELAY_MIN_MS = 3000;
  const DELAY_MAX_MS = 6000;
  const LOAD_TIMEOUT_MS = 12000;
  const MAX_PAGES = 300;
  const SAFE = BRANCH_NAME.replace(/\//g, '_');
  const STORAGE_KEY = `gl_commit_scrape_${SAFE}`;

  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const jitter = (min, max) => min + Math.random() * (max - min);

  const m = location.pathname.match(/^(.*?)\/-\/commits(?:\/(.*))?$/);
  if (!m) return console.warn('⚠️ Open your repo commits page first, then re-run the script.');
  if ((m[2] && decodeURIComponent(m[2])) !== BRANCH_NAME) {
    console.log(`🔀 Navigating to "${BRANCH_NAME}"... re-run the script once loaded.`);
    location.href = `${location.origin}${m[1]}/-/commits/${encodeURIComponent(BRANCH_NAME)}`;
    return;
  }

  const store = new Map();
  try {
    JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]').forEach(c => store.set(c.sha, c));
  } catch (_) {}

  const persist = () => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify([...store.values()])); } catch (_) {}
  };

  function extractCurrentPage() {
    const rows = document.querySelectorAll('li.commit-list-item[id^="commit-"]');
    let added = 0;
    rows.forEach(row => {
      const link = row.querySelector('a[data-testid="commit-title-link"]');
      if (!link) return;
      const href = link.getAttribute('href') || '';
      const sha = (href.match(/\/-\/commit\/([0-9a-f]{7,40})$/i) || [])[1] || href;
      if (store.has(sha)) return;

      const author = (
        row.querySelector('a[data-testid="commit-author-link"]') ||
        row.querySelector('.gl-text-wrap span')
      )?.textContent.trim() || '';

      store.set(sha, {
        sha,
        title: (link.getAttribute('title') || link.textContent || '').trim(),
        iso: row.querySelector('time[data-testid="commit-authored-date"]')?.getAttribute('datetime') || null,
        author,
      });
      added++;
    });
    return { added, firstRow: rows[0] || null };
  }

  async function waitForReload(prevFirstRow) {
    const start = Date.now();
    while (document.contains(prevFirstRow) && Date.now() - start < LOAD_TIMEOUT_MS) {
      await sleep(250);
    }
  }

  function toMarkdown() {
    const commits = [...store.values()].sort((a, b) => (b.iso || '').localeCompare(a.iso || ''));
    const byDay = new Map();
    commits.forEach(c => {
      const day = c.iso ? c.iso.slice(0, 10) : 'unknown-date';
      if (!byDay.has(day)) byDay.set(day, []);
      byDay.get(day).push(c);
    });

    let md = `# Commit history - ${BRANCH_NAME} Branch\n\nGenerated on ${new Date().toISOString()} - ${commits.length} commits\n\n`;
    for (const [day, list] of byDay) {
      md += `## ${day}\n\n`;
      list.forEach(c => {
        const title = c.title.replace(/\s+/g, ' ').trim();
        md += `- **${c.iso || 'unknown'}** - ${title} _(by ${c.author || 'Unknown author'}, \`${c.sha.slice(0, 8)}\`)_\n`;
      });
      md += '\n';
    }
    return md;
  }

  function download() {
    const url = URL.createObjectURL(new Blob([toMarkdown()], { type: 'text/markdown;charset=utf-8' }));
    const a = Object.assign(document.createElement('a'), { href: url, download: `COMMIT_HISTORY_${SAFE}.md` });
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  // Manual export at any time: window.__commitScrape.download()
  window.__commitScrape = { store, download };

  console.log(`⏳ Scraping "${BRANCH_NAME}"...`);

  let noNewStreak = 0;
  for (let page = 1; page <= MAX_PAGES; page++) {
    const { added, firstRow } = extractCurrentPage();
    persist();
    console.log(`Page ${page}: +${added}, total = ${store.size}`);

    noNewStreak = added ? 0 : noNewStreak + 1;
    if (noNewStreak >= 2) { console.log('⚠️ Nothing new, stopping.'); break; }

    const nextBtn = document.querySelector('button[data-testid="nextButton"]');
    if (!nextBtn || nextBtn.disabled || nextBtn.getAttribute('aria-disabled') === 'true') {
      console.log('✅ Last page reached.');
      break;
    }

    await sleep(jitter(DELAY_MIN_MS, DELAY_MAX_MS));
    nextBtn.click();
    await waitForReload(firstRow);
    await sleep(jitter(500, 1200));
  }

  download();
  console.log(`🎉 Done: ${store.size} commits → COMMIT_HISTORY_${SAFE}.md`);
})();
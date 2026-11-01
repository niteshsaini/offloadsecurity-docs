/**
 * Long tables (12+ body rows) get a filter box: type to show only the rows
 * that contain the text. Applies to every docs table automatically, so pages
 * stay plain Markdown. Runs after each route change.
 */
import type {ClientModule} from '@docusaurus/types';

const MIN_ROWS = 12;

function enhance(): void {
  document.querySelectorAll<HTMLDivElement>('.markdown .table-wrap').forEach((wrap) => {
    if (wrap.dataset.filterable) return;
    const tbody = wrap.querySelector('tbody');
    const rows = tbody ? Array.from(tbody.rows) : [];
    if (rows.length < MIN_ROWS) return;
    wrap.dataset.filterable = 'true';

    const bar = document.createElement('div');
    bar.className = 'table-filter';
    const input = document.createElement('input');
    input.type = 'search';
    input.placeholder = `Filter ${rows.length} rows…`;
    input.setAttribute('aria-label', 'Filter table rows');
    const count = document.createElement('span');
    count.className = 'table-filter__count';
    count.setAttribute('aria-live', 'polite');
    bar.append(input, count);
    wrap.parentElement?.insertBefore(bar, wrap);

    const text = rows.map((r) => r.textContent?.toLowerCase() ?? '');
    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      let shown = 0;
      rows.forEach((r, i) => {
        const hit = !q || text[i].includes(q);
        r.hidden = !hit;
        if (hit) shown += 1;
      });
      count.textContent = q ? `${shown} of ${rows.length}` : '';
    });
  });
}

const module: ClientModule = {
  onRouteDidUpdate() {
    // Let the new page render first.
    window.requestAnimationFrame(() => enhance());
  },
};

export default module;

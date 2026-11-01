/**
 * Reports searches that return nothing ("Docs Search No Results", with the
 * query) to the analytics provider, so missing topics and synonyms show up.
 * No-op without analytics (see src/lib/track.ts).
 */
import type {ClientModule} from '@docusaurus/types';
import {track} from '@site/src/lib/track';

let timer: number | undefined;
let lastReported = '';

function check(input: HTMLInputElement): void {
  const q = input.value.trim();
  if (q.length < 3 || q === lastReported) return;
  // docusaurus-search-local renders its empty state with a `noResults_*` class.
  if (document.querySelector('.navbar [class*="noResults"]')) {
    lastReported = q;
    track('Docs Search No Results', {query: q.toLowerCase().slice(0, 100)});
  }
}

const module: ClientModule = {
  onRouteDidUpdate() {
    const input = document.querySelector<HTMLInputElement>('.navbar__search-input');
    if (!input || input.dataset.tracked) return;
    input.dataset.tracked = 'true';
    input.addEventListener('input', () => {
      window.clearTimeout(timer);
      // Wait until the reader pauses typing.
      timer = window.setTimeout(() => check(input), 1500);
    });
  },
};

export default module;

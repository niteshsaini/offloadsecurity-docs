import React from 'react';
import styles from './SearchPrompt.module.css';

/**
 * A large "Search the docs" box for the home page. It does not run its own
 * search: it opens the navbar search (docusaurus-search-local) by sending the
 * same Ctrl/⌘ K shortcut the search bar listens for, so there is one index and
 * one results UI.
 */
export default function SearchPrompt(): JSX.Element {
  const isMac = typeof navigator !== 'undefined' && /Mac|iPhone|iPad/.test(navigator.platform);
  const open = () => {
    document.dispatchEvent(
      new KeyboardEvent('keydown', {key: 'k', code: 'KeyK', metaKey: isMac, ctrlKey: !isMac, bubbles: true}),
    );
    // Fallback (e.g. a mobile navbar where the input is collapsed).
    const input = document.querySelector<HTMLInputElement>('.navbar__search-input');
    if (input && document.activeElement !== input) input.focus();
  };
  return (
    <button type="button" className={styles.prompt} onClick={open}>
      <span aria-hidden="true" className={styles.icon}>⌕</span>
      <span className={styles.text}>Search the documentation</span>
      <kbd className={styles.kbd}>{isMac ? '⌘' : 'Ctrl'} K</kbd>
    </button>
  );
}

/**
 * Privacy-friendly analytics events. Works with either Plausible or Umami
 * (both cookieless) when the site was built with one enabled — see
 * DOCS_ANALYTICS_* in docusaurus.config.ts. Without analytics it does nothing.
 */
type Props = Record<string, string | number | boolean>;

declare global {
  interface Window {
    plausible?: (event: string, options?: {props?: Props}) => void;
    umami?: {track: (event: string, data?: Props) => void};
  }
}

export function track(event: string, props: Props = {}): void {
  if (typeof window === 'undefined') return;
  try {
    if (window.plausible) window.plausible(event, {props});
    else if (window.umami) window.umami.track(event, props);
  } catch {
    // Analytics must never break the page.
  }
}

import React from 'react';
import Head from '@docusaurus/Head';

export interface QA {
  q: string;
  a: string;
}

/**
 * Renders a visible FAQ section AND injects FAQPage JSON-LD into <head>.
 *
 * AI SEO: FAQPage structured data is favoured by AI answer engines
 * (ChatGPT, Google AI Overviews, Perplexity, Copilot) and is eligible for
 * rich results. The visible copy and the schema stay identical — Google
 * requires the structured data to match on-page content.
 *
 * The JSON-LD goes through @docusaurus/Head (react-helmet-async), which is
 * how Docusaurus itself emits BreadcrumbList JSON-LD into the static HTML.
 * An inline body <script> gets stripped by the static renderer, so Head is
 * the reliable path.
 *
 * Usage (page must be .mdx):
 *   import DocFaq from '@site/src/components/DocFaq';
 *   <DocFaq items={[{q: '...', a: '...'}]} />
 */
export default function DocFaq({items}: {items: QA[]}): JSX.Element {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map((it) => ({
      '@type': 'Question',
      name: it.q,
      acceptedAnswer: {'@type': 'Answer', text: it.a},
    })),
  };
  return (
    <>
      <Head>
        <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
      </Head>
      <section className="doc-faq">
        <h2>Frequently asked questions</h2>
        {items.map((it, i) => (
          <details key={i} className="doc-faq__item">
            <summary className="doc-faq__q">{it.q}</summary>
            <div className="doc-faq__a">
              <p>{it.a}</p>
            </div>
          </details>
        ))}
      </section>
    </>
  );
}

import React, {useState} from 'react';
import Footer from '@theme-original/DocItem/Footer';
import type FooterType from '@theme/DocItem/Footer';
import type {WrapperProps} from '@docusaurus/types';
import {useDoc} from '@docusaurus/plugin-content-docs/client';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {track} from '@site/src/lib/track';

type Props = WrapperProps<typeof FooterType>;

/**
 * "Was this page helpful?" — one click, no account. Votes go to the
 * analytics provider when one is configured (event "Docs Feedback" with the
 * page path and vote). A "No" also offers a way to say what was missing:
 * a prefilled GitHub issue or an email.
 */
function PageFeedback(): JSX.Element {
  const {metadata} = useDoc();
  const {siteConfig} = useDocusaurusContext();
  const [vote, setVote] = useState<'yes' | 'no' | null>(null);

  const page = metadata.permalink;
  const url = `${siteConfig.url}${page}`;
  const issue = `https://github.com/${siteConfig.organizationName}/${siteConfig.projectName}/issues/new?${new URLSearchParams({
    title: `Docs feedback: ${metadata.title}`,
    body: `Page: ${url}\n\nWhat was missing or wrong?\n`,
  })}`;
  const mail = `mailto:contact@offloadsecurity.com?${new URLSearchParams({
    subject: `Docs feedback: ${metadata.title}`,
    body: `Page: ${url}\n\nWhat was missing or wrong?\n`,
  }).toString().replace(/\+/g, '%20')}`;

  const send = (v: 'yes' | 'no') => {
    setVote(v);
    track('Docs Feedback', {page, vote: v});
  };

  return (
    <div className="doc-feedback" role="group" aria-label="Page feedback">
      {vote === null && (
        <>
          <span className="doc-feedback__q">Was this page helpful?</span>
          <button type="button" className="doc-feedback__btn" onClick={() => send('yes')}>
            <span aria-hidden="true">👍</span> Yes
          </button>
          <button type="button" className="doc-feedback__btn" onClick={() => send('no')}>
            <span aria-hidden="true">👎</span> No
          </button>
        </>
      )}
      {vote === 'yes' && <span className="doc-feedback__q">Thanks for letting us know.</span>}
      {vote === 'no' && (
        <span className="doc-feedback__q">
          Thanks. Tell us what was missing: <a href={issue} target="_blank" rel="noopener noreferrer">open an issue</a> or{' '}
          <a href={mail}>email us</a>.
        </span>
      )}
    </div>
  );
}

export default function FooterWrapper(props: Props): JSX.Element {
  return (
    <>
      <PageFeedback />
      <Footer {...props} />
    </>
  );
}

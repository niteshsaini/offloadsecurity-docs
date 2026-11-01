import React from 'react';
import Content from '@theme-original/DocItem/Content';
import type ContentType from '@theme/DocItem/Content';
import type {WrapperProps} from '@docusaurus/types';
import DocCardList from '@theme/DocCardList';
import Heading from '@theme/Heading';
import {useDoc} from '@docusaurus/plugin-content-docs/client';
import {useCurrentSidebarSiblings} from '@docusaurus/plugin-content-docs/client';

type Props = WrapperProps<typeof ContentType>;

/**
 * Section landing pages (`<section>/index`) end with a card grid of every
 * other page in their sidebar category, so each section has the same "where
 * next" navigation without maintaining link lists by hand.
 * Opt out per page with `hide_section_cards: true` in front matter.
 */
function SectionCards(): JSX.Element | null {
  const {metadata, frontMatter} = useDoc();
  const siblings = useCurrentSidebarSiblings();
  const isSectionIndex = metadata.id.endsWith('/index');
  if (!isSectionIndex || (frontMatter as {hide_section_cards?: boolean}).hide_section_cards) return null;
  const items = siblings.filter((item) => !(item.type === 'link' && item.docId === metadata.id));
  if (items.length === 0) return null;
  return (
    <section className="section-cards">
      <Heading as="h2" id="pages-in-this-section">
        Pages in this section
      </Heading>
      <DocCardList items={items} />
    </section>
  );
}

export default function ContentWrapper(props: Props): JSX.Element {
  return (
    <>
      <Content {...props} />
      <SectionCards />
    </>
  );
}

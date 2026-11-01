import React, {type ReactNode} from 'react';
import Link from '@docusaurus/Link';
import styles from './CardGrid.module.css';

export interface CardProps {
  title: string;
  to: string;
  children?: ReactNode;
}

/** A linked card: title + one-line description. Used on the home page. */
export function Card({title, to, children}: CardProps): JSX.Element {
  return (
    <Link to={to} className={styles.card}>
      <span className={styles.title}>
        {title} <span aria-hidden="true" className={styles.arrow}>→</span>
      </span>
      {children && <span className={styles.body}>{children}</span>}
    </Link>
  );
}

/** Responsive grid of <Card>s: 3 columns on desktop, 1–2 on smaller screens. */
export default function CardGrid({children, columns = 3}: {children: ReactNode; columns?: 2 | 3}): JSX.Element {
  return <div className={columns === 2 ? `${styles.grid} ${styles.two}` : styles.grid}>{children}</div>;
}

export interface PathProps {
  title: string;
  audience: string;
  steps: {label: string; to: string}[];
}

/** A reading path for one audience: numbered links in the order to read them. */
export function Path({title, audience, steps}: PathProps): JSX.Element {
  return (
    <div className={styles.path}>
      <span className={styles.title}>{title}</span>
      <span className={styles.body}>{audience}</span>
      <ol className={styles.steps}>
        {steps.map((s) => (
          <li key={s.to}>
            <Link to={s.to}>{s.label}</Link>
          </li>
        ))}
      </ol>
    </div>
  );
}

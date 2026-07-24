import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Offload Security Docs',
  // Canonical entity positioning — kept consistent with the marketing site's
  // single source of truth (offloadsecurity-website/src/data/company.js).
  // Docusaurus uses `tagline` as the default site meta description, so this
  // must describe the whole platform, not CSPM alone.
  tagline: 'Unified CNAPP, vulnerability management and compliance — one governed risk view',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  markdown: {
    format: 'md',
    mermaid: true,
  },

  url: 'https://docs.offloadsecurity.com',
  baseUrl: '/',

  organizationName: 'niteshsaini',
  projectName: 'offloadsecurity-docs',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
          editUrl: 'https://github.com/niteshsaini/offload-cspm/tree/main/docs-site/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themes: ['@docusaurus/theme-mermaid'],

  themeConfig: {
    image: 'img/offload-social-card.png',
    // Explicit entity description for search + AI answer engines. Matches the
    // canonical short description used across the marketing site and profiles.
    metadata: [
      {
        name: 'description',
        content:
          'Offload Security is a unified CNAPP, vulnerability management and compliance platform that consolidates findings across cloud, code, containers, Kubernetes, applications, on-premises infrastructure and existing security tools into one governed risk view.',
      },
    ],
    mermaid: {
      theme: { light: 'neutral', dark: 'dark' },
    },
    colorMode: {
      defaultMode: 'dark',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Offload Security',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Documentation',
        },
        {
          href: 'https://offloadsecurity.com',
          label: 'Platform',
          position: 'left',
        },
        {
          href: 'https://github.com/niteshsaini/offload-cspm',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {
              label: 'Introduction',
              to: '/introduction',
            },
            {
              label: 'Getting Started',
              to: '/getting-started',
            },
            {
              label: 'On-Premises',
              to: '/on-premises',
            },
          ],
        },
        {
          title: 'Platform',
          items: [
            {
              label: 'Cloud Security',
              to: '/cloud-security',
            },
            {
              label: 'Compliance',
              to: '/compliance',
            },
            {
              label: 'AI & Threat Intelligence',
              to: '/ai-threat-intelligence',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Offload Security',
              href: 'https://offloadsecurity.com',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/niteshsaini/offload-cspm',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Offload Security. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'json', 'yaml', 'docker'],
    },
    tableOfContents: {
      minHeadingLevel: 2,
      maxHeadingLevel: 4,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;

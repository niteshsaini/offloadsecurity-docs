import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// The platform release these docs describe. The working copy in `docs/` is
// always the CURRENT release and is served at the site root, so existing
// URLs never move. When the next release is cut, snapshot this one first
// (`npm run docusaurus docs:version <this value>` — it then lives under
// /<version>/) and bump this constant. See VERSIONING.md.
const CURRENT_RELEASE = '1.4.0';

const config: Config = {
  title: 'Offload Security Docs',
  // Canonical entity positioning — kept consistent with the marketing site's
  // single source of truth (offloadsecurity-website/src/data/company.js).
  // Docusaurus uses `tagline` as the default site meta description, so this
  // must describe the whole platform, not CSPM alone.
  tagline: 'Unified CNAPP, vulnerability management and compliance — one governed risk view',
  favicon: 'img/favicon.png',

  future: {
    v4: true,
  },

  markdown: {
    // 'detect' = CommonMark for .md, MDX for .mdx. (A fixed 'md' would force
    // CommonMark on .mdx too, rendering JSX components as literal text.)
    format: 'detect',
    mermaid: true,
  },

  url: 'https://docs.offloadsecurity.com',
  customFields: {
    currentRelease: CURRENT_RELEASE,
  },
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
          // Surface a "Last updated" date on every page (derived from git
          // history at build time). Helps API users and self-hosters judge
          // freshness. Author is omitted — the date is the useful signal.
          showLastUpdateTime: true,
          // Wide tables scroll inside their own box (see custom.css).
          rehypePlugins: [require('./src/plugins/rehype-table-wrap')],
          // Versioned docs, Wazuh-style: a version selector in the navbar,
          // the current release at the root, older releases under /<version>/
          // with an "unmaintained version" banner.
          lastVersion: 'current',
          versions: {
            current: {
              label: `${CURRENT_RELEASE} (current)`,
              path: '',
              badge: true,
              banner: 'none',
            },
          },
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  // Self-hosted Inter (no Google Fonts request).
  clientModules: [require.resolve('@fontsource-variable/inter')],

  plugins: [
    // Click a screenshot to view it full size.
    'docusaurus-plugin-image-zoom',
    // Writes /llms.txt — a page index for AI assistants and answer engines.
    './src/plugins/llms-txt.js',
  ],

  themes: [
    '@docusaurus/theme-mermaid',
    // Offline, self-hosted full-text search — no external service or API key.
    // Indexes the docs at build time and renders a search bar in the navbar.
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true,
        indexBlog: false,
        docsRouteBasePath: '/',
        highlightSearchTermsOnTargetPage: true,
        searchResultLimits: 8,
      },
    ],
  ],

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
    zoom: {
      selector: '.markdown img:not(a img)',
      background: {
        light: 'rgba(255, 255, 255, 0.95)',
        dark: 'rgba(15, 23, 42, 0.95)',
      },
    },
    mermaid: {
      theme: { light: 'neutral', dark: 'dark' },
    },
    colorMode: {
      defaultMode: 'dark',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Offload Security',
      // Kept short: Docs · API · Release notes on the left; version,
      // platform and contact on the right. Glossary, FAQ, CLI and
      // troubleshooting live in the sidebar (Resources) and the footer.
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/api-reference',
          label: 'API',
          position: 'left',
          activeBaseRegex: '^/api-(reference|automation)',
        },
        {
          to: '/release-notes',
          label: 'Release notes',
          position: 'left',
        },
        {
          type: 'docsVersionDropdown',
          position: 'right',
          dropdownActiveClassDisabled: true,
        },
        {
          href: 'https://offloadsecurity.com/platform',
          label: 'Platform',
          position: 'right',
        },
        {
          href: 'mailto:contact@offloadsecurity.com',
          label: 'Contact Us',
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
              label: 'Quickstart',
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
          title: 'Reference',
          items: [
            {
              label: 'API Reference',
              to: '/api-reference',
            },
            {
              label: 'CLI & CI/CD',
              to: '/cli-and-cicd',
            },
            {
              label: 'Release Notes',
              to: '/release-notes',
            },
            {
              label: 'Glossary',
              to: '/glossary',
            },
          ],
        },
        {
          title: 'Help & support',
          items: [
            {
              label: 'FAQ',
              to: '/faq',
            },
            {
              label: 'Troubleshooting',
              to: '/troubleshooting',
            },
            {
              label: 'Trust & Security',
              to: '/trust-and-security',
            },
            {
              label: 'Contact support',
              href: 'mailto:contact@offloadsecurity.com',
            },
            {
              label: 'Offload Security',
              href: 'https://offloadsecurity.com',
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

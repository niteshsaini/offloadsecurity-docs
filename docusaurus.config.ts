import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Offload Security Docs',
  tagline: 'AI-Powered Cloud Security Posture Management',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  markdown: {
    format: 'md',
  },

  url: 'https://docs.offloadsecurity.com',
  baseUrl: '/',

  organizationName: 'niteshsaini',
  projectName: 'offload-cspm',

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

  themeConfig: {
    image: 'img/offload-social-card.png',
    colorMode: {
      defaultMode: 'dark',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Offload Security',
      logo: {
        alt: 'Offload Security Logo',
        src: 'img/logo.svg',
      },
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
              label: 'Getting Started',
              to: '/platform-overview/getting-started',
            },
            {
              label: 'Architecture',
              to: '/platform-overview/architecture',
            },
            {
              label: 'Deployment',
              to: '/infrastructure/deployment',
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

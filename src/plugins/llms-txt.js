// Generates /llms.txt (https://llmstxt.org) after the build: one line per
// current-version docs page — title, URL and the page's meta description —
// grouped by top-level section. Read from the built HTML so the URLs, titles
// and descriptions are exactly what the site serves.
const fs = require('fs');
const path = require('path');

const decode = (s) =>
  s
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#x27;|&#39;/g, "'");

module.exports = function llmsTxtPlugin(context) {
  return {
    name: 'llms-txt',
    async postBuild({outDir, routesPaths}) {
      const {siteConfig} = context;
      const site = siteConfig.url.replace(/\/$/, '');
      const release = siteConfig.customFields?.currentRelease;
      const pages = [];
      for (const route of routesPaths) {
        // Skip non-doc routes and snapshotted older versions (/1.4.0/...).
        if (route === '/404.html' || route.startsWith('/search') || /^\/\d+\.\d+\.\d+(\/|$)/.test(route)) continue;
        const file = path.join(outDir, route, 'index.html');
        if (!fs.existsSync(file)) continue;
        const html = fs.readFileSync(file, 'utf8');
        const title = (html.match(/<title[^>]*>([^<]*)<\/title>/) || [])[1];
        // The build minifies HTML, so attribute quotes are optional.
        const m = html.match(/<meta[^>]*\sname="?description"?\s[^>]*content=(?:"([^"]*)"|([^\s>]+))/);
        const desc = m ? m[1] ?? m[2] : '';
        if (!title) continue;
        pages.push({
          route,
          title: decode(title.replace(/ \| .*$/, '')),
          desc: desc ? decode(desc) : '',
        });
      }
      const groups = new Map();
      for (const p of pages.sort((a, b) => a.route.localeCompare(b.route))) {
        const top = p.route.split('/').filter(Boolean)[0] || 'overview';
        if (!groups.has(top)) groups.set(top, []);
        groups.get(top).push(p);
      }
      // Section names as the sidebar shows them; single-page sections are
      // folded into "Resources".
      const SECTIONS = {
        overview: 'Overview',
        'getting-started': 'Getting Started',
        introduction: 'Introduction',
        adoption: 'Adoption Guides',
        'cloud-security': 'Cloud Security',
        'security-scanning': 'App & Infrastructure Scanning',
        'vulnerability-risk': 'Vulnerabilities & Risk',
        'reports-and-ai': 'Reports & AI',
        compliance: 'Compliance & GRC',
        'ai-threat-intelligence': 'AI & Threat Intelligence',
        integrations: 'Integrations',
        'api-automation': 'API & Automation',
        'api-reference': 'API Reference',
        authentication: 'Platform Security',
        'on-premises': 'On-Premises',
        industries: 'Industries',
        'release-notes': 'Release Notes',
      };
      const merged = new Map();
      for (const [top, items] of groups) {
        const key = SECTIONS[top] && (items.length > 1 || top === 'overview' || top === 'getting-started') ? SECTIONS[top] : 'Resources';
        merged.set(key, [...(merged.get(key) || []), ...items]);
      }
      const order = [...Object.values(SECTIONS), 'Resources'];
      const sorted = [...merged].sort((x, y) => order.indexOf(x[0]) - order.indexOf(y[0]));
      let out = `# ${siteConfig.title}\n\n> ${siteConfig.tagline}\n\n`;
      out += `These docs describe Offload Security${release ? ` ${release} (the current release)` : ''}. `;
      out += 'Older releases, when available, are under /<version>/ — prefer the current docs unless a specific version is needed.\n';
      for (const [name, items] of sorted) {
        out += `\n## ${name}\n\n`;
        for (const p of items) {
          out += `- [${p.title}](${site}${p.route})${p.desc ? `: ${p.desc}` : ''}\n`;
        }
      }
      fs.writeFileSync(path.join(outDir, 'llms.txt'), out);
    },
  };
};

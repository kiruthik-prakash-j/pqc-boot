// @ts-check

const [repoOwner, repoName] = (process.env.GITHUB_REPOSITORY || 'kiruthik/pqc-boot').split('/');
const ghPagesUrl = `https://${repoOwner}.github.io`;
const ghPagesBaseUrl = process.env.GITHUB_ACTIONS ? `/${repoName}/` : '/';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'PQC Secure Boot Documentation',
  tagline: 'Post-Quantum Cryptography Secure Bootloader Architecture & Implementation',
  url: ghPagesUrl,
  baseUrl: ghPagesBaseUrl,
  organizationName: repoOwner,
  projectName: repoName,
  deploymentBranch: 'gh-pages',
  trailingSlash: false,
  onBrokenLinks: 'warn',

  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          routeBasePath: 'docs',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'PQC Secure Boot',
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            to: '/docs/implementation/playground',
            label: 'PQC Playground',
            position: 'left',
          },
          {
            to: '/docs/thesis/introduction',
            label: 'Thesis',
            position: 'left',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Research',
                to: '/docs/research/quantum-threat-vectors',
              },
              {
                label: 'Learning',
                to: '/docs/learning/pqc-fundamentals',
              },
              {
                label: 'Implementation',
                to: '/docs/implementation/firmware-architecture',
              },
            ],
          },
          {
            title: 'Evaluation',
            items: [
              {
                label: 'Playground Simulation',
                to: '/docs/implementation/playground',
              },
              {
                label: 'Benchmarking Results',
                to: '/docs/logs/benchmarking-results',
              },
              {
                label: 'Development Logbook',
                to: '/docs/logs/development-logbook',
              },
            ],
          },
          {
            title: 'Academic',
            items: [
              {
                label: 'Thesis Chapter 1',
                to: '/docs/thesis/introduction',
              },
              {
                label: 'Thesis Chapter 2',
                to: '/docs/thesis/pqc-algorithms',
              },
              {
                label: 'Thesis Chapter 3',
                to: '/docs/thesis/architecture-design',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} PQC Secure Bootloader Project. Built with Docusaurus.`,
      },
    }),
};

module.exports = config;

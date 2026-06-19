// @ts-check

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Kalico Documentation',
  tagline: 'Community-maintained fork of Klipper 3D-Printer firmware',
  favicon: 'logo/kalico-32x32.png',

  url: 'https://docs.kalico.gg',
  baseUrl: '/',

  organizationName: 'KalicoCrew',
  projectName: 'kalico',

  onBrokenLinks: 'warn',

  markdown: {
    format: 'md',
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'zh-CN'],
    localeConfigs: {
      en: {
        htmlLang: 'en-US',
      },
      'zh-CN': {
        htmlLang: 'zh-Hans',
      },
    },
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/KalicoCrew/kalico/tree/main/docs-docusaurus/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'logo/kalico-big.png',
      navbar: {
        title: 'Kalico',
        logo: {
          alt: 'Kalico Logo',
          src: 'logo/kalico-96x96.png',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Docs',
          },
          {
            href: 'https://github.com/KalicoCrew/kalico/releases',
            label: 'Releases',
            position: 'left',
          },
          {
            href: 'https://kalico.gg/discord',
            label: 'Discord',
            position: 'right',
          },
          {
            href: 'https://github.com/KalicoCrew/kalico',
            label: 'GitHub',
            position: 'right',
          },
          {
            type: 'localeDropdown',
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
                to: '/docs/Installation',
              },
              {
                label: 'Configuration',
                to: '/docs/Config_Reference',
              },
              {
                label: 'G-Code Reference',
                to: '/docs/G-Codes',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'Discord',
                href: 'https://kalico.gg/discord',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/KalicoCrew/kalico',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Releases',
                href: 'https://github.com/KalicoCrew/kalico/releases',
              },
              {
                label: 'Klipper (Upstream)',
                href: 'https://www.klipper3d.org/',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Kalico Community. Built with Docusaurus.`,
      },
      prism: {
        theme: require('prism-react-renderer').themes.github,
        darkTheme: require('prism-react-renderer').themes.dracula,
        additionalLanguages: ['python', 'bash', 'ini'],
      },
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
    }),

  themes: [
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      /** @type {import('@easyops-cn/docusaurus-search-local').PluginOptions} */
      ({
        hashed: true,
        language: ['en', 'zh'],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      }),
    ],
  ],
};

module.exports = config;

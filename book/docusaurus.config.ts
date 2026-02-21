import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI: From Perception to Action',
  tagline: 'A comprehensive guide to the convergence of AI and physical systems',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://taha74824-cmd.github.io',
  baseUrl: '/physical-ai-book/',

  organizationName: 'taha74824-cmd',
  projectName: 'physical-ai-book',
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
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Physical AI Book',
      logo: {
        alt: 'Physical AI Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'bookSidebar',
          position: 'left',
          label: 'Read Book',
        },
        {
          href: 'https://github.com/taha74824-cmd/physical-ai-book',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Chapters',
          items: [
            {label: 'Introduction to Physical AI', to: '/chapter-01-introduction/overview'},
            {label: 'Foundations', to: '/chapter-02-foundations/overview'},
            {label: 'Machine Learning', to: '/chapter-03-machine-learning/overview'},
            {label: 'Computer Vision', to: '/chapter-04-computer-vision/overview'},
          ],
        },
        {
          title: 'More Chapters',
          items: [
            {label: 'NLP & Robotics', to: '/chapter-05-nlp-robotics/overview'},
            {label: 'Sim-to-Real', to: '/chapter-06-sim-to-real/overview'},
            {label: 'Embodied AI', to: '/chapter-07-embodied-ai/overview'},
            {label: 'Humanoid Robots', to: '/chapter-08-humanoid-robots/overview'},
          ],
        },
        {
          title: 'Resources',
          items: [
            {label: 'Safety & Ethics', to: '/chapter-09-safety-ethics/overview'},
            {label: 'Future of Physical AI', to: '/chapter-10-future/overview'},
            {label: 'GitHub', href: 'https://github.com/taha74824-cmd/physical-ai-book'},
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Book. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'json', 'yaml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;

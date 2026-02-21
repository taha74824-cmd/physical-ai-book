import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import FloatingChatBot from '@site/src/components/ChatBot/FloatingChatBot';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/chapter-01-introduction/overview">
            Start Reading 📖
          </Link>
          <Link
            className="button button--outline button--secondary button--lg"
            style={{marginLeft: '12px'}}
            to="/chapter-08-humanoid-robots/overview">
            Humanoid Robots 🤖
          </Link>
        </div>
        <div style={{marginTop: '32px', display: 'flex', gap: '16px', flexWrap: 'wrap', justifyContent: 'center'}}>
          {[
            {icon: '🤖', label: 'Robotics'},
            {icon: '🧠', label: 'Deep Learning'},
            {icon: '👁️', label: 'Computer Vision'},
            {icon: '🗣️', label: 'NLP'},
            {icon: '🌐', label: 'Sim-to-Real'},
            {icon: '🦾', label: 'Embodied AI'},
            {icon: '🚶', label: 'Humanoid Robots'},
            {icon: '🔒', label: 'Safety & Ethics'},
          ].map(({icon, label}) => (
            <div key={label} style={{
              background: 'rgba(255,255,255,0.15)',
              borderRadius: '20px',
              padding: '6px 14px',
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}>
              {icon} {label}
            </div>
          ))}
        </div>
      </div>
    </header>
  );
}

function BookFeatures() {
  const features = [
    {
      icon: '📚',
      title: '10 Comprehensive Chapters',
      desc: 'From foundations to the future — covering every aspect of Physical AI.',
    },
    {
      icon: '🤖',
      title: 'RAG-Powered AI Chatbot',
      desc: 'Ask questions about the book content using our AI assistant.',
    },
    {
      icon: '💡',
      title: 'Select Text to Ask',
      desc: 'Highlight any passage in the book and instantly ask the AI about it.',
    },
    {
      icon: '🔬',
      title: 'Code Examples',
      desc: 'Practical Python code examples for every major concept covered.',
    },
  ];

  return (
    <section style={{padding: '48px 0', background: 'var(--ifm-background-surface-color)'}}>
      <div className="container">
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: '24px',
        }}>
          {features.map((f) => (
            <div key={f.title} style={{
              padding: '24px',
              borderRadius: '12px',
              border: '1px solid var(--ifm-color-emphasis-200)',
              background: 'var(--ifm-background-color)',
            }}>
              <div style={{fontSize: '36px', marginBottom: '12px'}}>{f.icon}</div>
              <h3 style={{marginBottom: '8px'}}>{f.title}</h3>
              <p style={{color: 'var(--ifm-color-emphasis-600)', margin: 0}}>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="A comprehensive guide to Physical AI — the convergence of AI and physical systems">
      <HomepageHeader />
      <main>
        <BookFeatures />
      </main>
      <FloatingChatBot />
    </Layout>
  );
}

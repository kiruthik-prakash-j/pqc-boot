import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import PqcBootPlayground from '@site/src/components/PqcBootPlayground';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/research/quantum-threat-vectors">
            Explore Research & Architecture 🚀
          </Link>
          <Link
            className="button button--primary button--lg"
            style={{ marginLeft: '12px', backgroundColor: '#38bdf8', color: '#0f172a' }}
            to="/docs/implementation/playground">
            Try PQC Playground ⚡
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Post-Quantum Cryptography Secure Boot Architecture & Bare-Metal Implementation">
      <HomepageHeader />
      <main className="container margin-vert--lg">
        <section className="margin-bottom--xl">
          <h2>Interactive PQC Secure Bootloader Simulator</h2>
          <p>
            Simulate and analyze post-quantum cryptographic signature verification algorithms
            (ML-DSA-44/87, SLH-DSA, LMS) within an emulated bare-metal secure boot pipeline.
          </p>
          <PqcBootPlayground />
        </section>

        <section className="row margin-bottom--lg">
          <div className="col col--4">
            <div className="card padding--md">
              <h3>01. PQC Standards & Research</h3>
              <p>
                In-depth analysis of NIST FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA), RFC 8554 (LMS), and quantum threat vectors against RSA/ECC.
              </p>
              <Link to="/docs/research/quantum-threat-vectors">Read Research &rarr;</Link>
            </div>
          </div>
          <div className="col col--4">
            <div className="card padding--md">
              <h3>02. Bare-Metal Implementation</h3>
              <p>
                Zero-malloc execution pipeline, RISC-V and ARM QEMU bare-metal setup, CMake build scripts, and eFuse hardware RoT integration.
              </p>
              <Link to="/docs/implementation/firmware-architecture">Read Implementation &rarr;</Link>
            </div>
          </div>
          <div className="col col--4">
            <div className="card padding--md">
              <h3>03. Benchmarks & Academic Thesis</h3>
              <p>
                Hardware profiling logs, cycle counts, RAM footprints, and embedded academic thesis chapters.
              </p>
              <Link to="/docs/thesis/introduction">Read Thesis &rarr;</Link>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}

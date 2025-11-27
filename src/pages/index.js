import React from "react";
import Layout from "@theme/Layout";
import Link from "@docusaurus/Link";

export default function Home() {
  return (
    <Layout title="AI-Driven Spec-to-Book Generator">
      <header style={{ backgroundColor: "#000", color: "#fff", padding: "8rem 0", textAlign: "center" }}>
        <div className="container">
          <h1 style={{ fontSize: "4rem", margin: "0 0 1.5rem 0", fontWeight: "bold" }}>
            AI-Driven Spec-to-Book Generator
          </h1>
          <p style={{ fontSize: "2rem", margin: "0 0 3rem 0", opacity: 0.9 }}>
            Zero manual writing · Fully AI-generated book from a single spec
          </p>
          <Link
            className="button button--lg button--warning"
            to="/docs/intro"
            style={{ padding: "1.2rem 3rem", fontSize: "1.4rem", fontWeight: "bold" }}
          >
            Enter the Book
          </Link>
        </div>
      </header>

      <main style={{ textAlign: "center", padding: "5rem 0" }}>
        <p style={{ fontSize: "2rem", color: "#ff6bcb" }}>
          Made with love by Hira ♡
        </p>
      </main>
    </Layout>
  );
}
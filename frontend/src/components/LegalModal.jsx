import React, { useState } from "react";
import { CloseIcon, ShieldIcon, FileTextIcon } from "./Icons";
import "./LegalModal.css";

export default function LegalModal({ initialTab = "privacy", onClose }) {
  const [activeTab, setActiveTab] = useState(initialTab);

  return (
    <div className="legal-overlay" onClick={onClose}>
      <div className="legal-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="legal-header">
          <div className="legal-tabs">
            <button
              className={`legal-tab-btn ${activeTab === "privacy" ? "active" : ""}`}
              onClick={() => setActiveTab("privacy")}
            >
              <ShieldIcon size={15} />
              <span>Privacy Policy</span>
            </button>
            <button
              className={`legal-tab-btn ${activeTab === "terms" ? "active" : ""}`}
              onClick={() => setActiveTab("terms")}
            >
              <FileTextIcon size={15} />
              <span>Terms & Conditions</span>
            </button>
          </div>

          <button
            className="legal-close-btn"
            onClick={onClose}
            title="Close"
          >
            <CloseIcon size={16} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="legal-body">
          {activeTab === "privacy" ? (
            <div className="legal-content">
              <div className="legal-doc-header">
                <h2>Privacy Policy</h2>
                <div className="legal-doc-date">Effective Date: October 1, 2026</div>
              </div>

              <section className="legal-section">
                <h3>1. Overview and Scope</h3>
                <p>
                  This Privacy Policy describes how the Knowledge Graph RAG platform
                  collects, processes, stores, and protects data when you ingest enterprise documents
                  and execute hybrid graph/vector queries. We are committed to transparency, data
                  integrity, and user privacy in enterprise environments.
                </p>
              </section>

              <section className="legal-section">
                <h3>2. Information We Process</h3>
                <p>When using this platform, the following data may be processed:</p>
                <ul>
                  <li>
                    <strong>Document Contents:</strong> Files uploaded via the ingestion interface
                    (including PDF, DOCX, CSV, XLSX, PPTX, and TXT formats) for the sole purpose of
                    chunking, vectorization, and knowledge graph extraction.
                  </li>
                  <li>
                    <strong>User Queries:</strong> Search strings and questions submitted to the
                    hybrid query engine to evaluate semantic similarity and graph traversal paths.
                  </li>
                  <li>
                    <strong>Technical Metadata:</strong> File sizes, MIME types, document IDs, chunk
                    indices, and generated vector dimensions (384-dimensional embeddings).
                  </li>
                  <li>
                    <strong>Operational Logs:</strong> Request timestamps, processing durations, and
                    API error statuses necessary to ensure system uptime and debugging.
                  </li>
                </ul>
              </section>

              <section className="legal-section">
                <h3>3. Storage and Data Isolation</h3>
                <p>
                  All document text chunks, vector embeddings, and knowledge graph triples are stored in
                  isolated database instances configured by your deployment:
                </p>
                <ul>
                  <li>
                    <strong>Relational and Vector Data:</strong> Vector embeddings are stored in
                    PostgreSQL using the pgvector extension with Hierarchical Navigable Small World (HNSW)
                    indexing.
                  </li>
                  <li>
                    <strong>Knowledge Graph Data:</strong> Extracted entities and relationships are
                    persisted in Neo4j as labeled property graphs.
                  </li>
                  <li>
                    <strong>Local Isolation:</strong> By default, data remains strictly within the
                    configured database containers and local filesystem storage.
                  </li>
                </ul>
              </section>

              <section className="legal-section">
                <h3>4. External LLM and API Processing</h3>
                <p>
                  Entity extraction and query synthesis rely on configured model providers (such as
                  Google Gemini or Groq APIs). Only the textual content of relevant chunks and user questions
                  are transmitted over encrypted TLS connections to these providers for synthesis. No
                  proprietary documents are used to train foundational public models under standard enterprise
                  API agreements.
                </p>
              </section>

              <section className="legal-section">
                <h3>5. Data Retention and Purging</h3>
                <p>
                  Users maintain full ownership and control over all uploaded assets. Documents and
                  associated graph nodes can be purged directly by resetting database tables or issuing
                  scoped deletion commands. We do not retain backup archives beyond designated operator
                  retention cycles.
                </p>
              </section>

              <section className="legal-section">
                <h3>6. Security Measures</h3>
                <p>
                  Standard administrative and technical protections are enforced, including containerized
                  network boundaries, parameterized SQL/Cypher queries to prevent injection vulnerabilities,
                  and environment-based credential management.
                </p>
              </section>

              <section className="legal-section">
                <h3>7. Updates to this Policy</h3>
                <p>
                  This policy may be amended to reflect architectural modifications, regulatory shifts, or
                  feature enhancements. Material updates will be documented directly in this repository.
                </p>
              </section>
            </div>
          ) : (
            <div className="legal-content">
              <div className="legal-doc-header">
                <h2>Terms & Conditions</h2>
                <div className="legal-doc-date">Effective Date: October 1, 2026</div>
              </div>

              <section className="legal-section">
                <h3>1. Acceptance of Terms</h3>
                <p>
                  By accessing or utilizing the Knowledge Graph RAG platform, you confirm your acceptance of
                  these Terms and Conditions. If you are accessing this platform on behalf of an enterprise or
                  organization, you represent that you possess the authority to bind that entity to these terms.
                </p>
              </section>

              <section className="legal-section">
                <h3>2. Permitted Use and Licensing</h3>
                <p>
                  Subject to compliance with repository licenses (MIT License), you are granted a non-exclusive,
                  revocable right to deploy, configure, and operate this software for enterprise retrieval,
                  internal knowledge management, and data evaluation.
                </p>
              </section>

              <section className="legal-section">
                <h3>3. Ingestion and Intellectual Property</h3>
                <p>
                  You retain all existing intellectual property rights and title to the documents, records, and
                  data files uploaded to the platform. You warrant that:
                </p>
                <ul>
                  <li>
                    You possess the lawful rights and licenses to ingest and parse all provided source files.
                  </li>
                  <li>
                    The uploaded materials do not violate applicable privacy regulations, copyright laws, or
                    contractual confidentiality agreements.
                  </li>
                  <li>
                    You will not ingest malicious binaries, scripts, or hostile payloads into the parser.
                  </li>
                </ul>
              </section>

              <section className="legal-section">
                <h3>4. Algorithmic and Output Disclaimer</h3>
                <p>
                  The platform utilizes neural embedding models, probabilistic query classification, and large
                  language models for answer generation. While the hybrid architecture employs multi-hop graph
                  validation and vector cosine scoring to ground outputs in factual evidence:
                </p>
                <ul>
                  <li>
                    Outputs are generated automatically and must be verified against source citations for critical
                    compliance or legal decisions.
                  </li>
                  <li>
                    The system does not guarantee that generated responses are universally error-free, exhaustive,
                    or infallible.
                  </li>
                  <li>
                    Performance and latency metrics vary according to system hardware, database indexing, and network
                    throughput.
                  </li>
                </ul>
              </section>

              <section className="legal-section">
                <h3>5. Limitation of Liability</h3>
                <p>
                  In no event shall the authors, maintainers, or contributors be held liable for any indirect,
                  consequential, incidental, or exemplary damages, including data loss, business interruption, or
                  computation downtime, arising from the deployment or misuse of this software.
                </p>
              </section>

              <section className="legal-section">
                <h3>6. Third-Party Integrations</h3>
                <p>
                  This system integrates with third-party software, including Docker, Neo4j, PostgreSQL, and
                  upstream LLM APIs. Use of third-party services is subject to their respective terms, service
                  level agreements, and API policies.
                </p>
              </section>

              <section className="legal-section">
                <h3>7. Termination</h3>
                <p>
                  Operators may terminate or restrict local service instances at any time. Provisions regarding
                  intellectual property ownership, warranty disclaimers, and limitation of liability shall survive
                  any termination.
                </p>
              </section>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="legal-footer">
          <div className="legal-footer-info">
            Knowledge Graph RAG Platform Governance
          </div>
          <button className="legal-dismiss-btn" onClick={onClose}>
            Acknowledge & Close
          </button>
        </div>
      </div>
    </div>
  );
}

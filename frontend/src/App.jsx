import { useState, useEffect, useRef } from "react";
import KnowledgeGraphVisualizer from "./components/KnowledgeGraphVisualizer";
import LegalModal from "./components/LegalModal";
import {
  NetworkIcon,
  DocumentIcon,
  UploadIcon,
  SearchIcon,
  CheckIcon,
  AlertIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  ArrowUpRightIcon,
  CloseIcon,
  ListIcon,
  ShieldIcon,
  FileTextIcon,
} from "./components/Icons";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

// Helper to convert linear graph evidence paths into nodes and links for 2D visualizer
function convertEvidenceToGraph(graphEvidence) {
  if (!graphEvidence || !Array.isArray(graphEvidence)) return { nodes: [], links: [] };
  const nodesMap = new Map();
  const links = [];

  graphEvidence.forEach((item) => {
    const nodes = item.nodes || [];
    nodes.forEach((n) => {
      if (n && n.name && !nodesMap.has(n.name)) {
        nodesMap.set(n.name, {
          id: n.name,
          name: n.name,
          entity_type: n.entity_type || "Entity",
        });
      }
    });

    for (let i = 0; i < nodes.length - 1; i++) {
      links.push({
        source: nodes[i].name,
        target: nodes[i + 1].name,
        relationship: item.relationship || "RELATED_TO",
        confidence: item.confidence || 1.0,
      });
    }
  });

  return {
    nodes: Array.from(nodesMap.values()),
    links,
  };
}

const SUPPORTED_FORMATS = [
  { label: "PDF", ext: ".pdf", color: "#3b82f6" },
  { label: "DOCX", ext: ".docx", color: "#60a5fa" },
  { label: "CSV", ext: ".csv", color: "#10b981" },
  { label: "XLSX", ext: ".xlsx", color: "#06b6d4" },
  { label: "PPTX", ext: ".pptx", color: "#f59e0b" },
  { label: "TXT", ext: ".txt", color: "#94a3b8" },
];

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Documents and active filter
  const [documents, setDocuments] = useState([]);
  const [selectedDocId, setSelectedDocId] = useState(null);

  // Graph explorer & visualizer states
  const [evidenceViewMode, setEvidenceViewMode] = useState("visual"); // 'visual' | 'raw'
  const [showGraphModal, setShowGraphModal] = useState(false);
  const [fullGraphData, setFullGraphData] = useState(null);
  const [loadingGraph, setLoadingGraph] = useState(false);
  const [graphFilterDocId, setGraphFilterDocId] = useState("");

  // Upload states
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStage, setUploadStage] = useState("idle"); // 'idle' | 'parsing' | 'graph' | 'vector' | 'done'
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState("");
  const fileInputRef = useRef(null);

  // Legal modal states ('privacy' | 'terms' | null)
  const [legalModalTab, setLegalModalTab] = useState(null);

  // Fetch available documents on mount
  const fetchDocuments = async () => {
    try {
      const response = await fetch(`${API_URL}/documents`);
      if (response.ok) {
        const data = await response.json();
        if (data.documents) {
          setDocuments(data.documents);
        }
      }
    } catch (err) {
      console.warn("Could not fetch documents:", err);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  // Fetch full knowledge graph data for modal visualizer
  const fetchFullGraph = async (docId = "") => {
    setLoadingGraph(true);
    try {
      const url = docId
        ? `${API_URL}/graph?document_id=${encodeURIComponent(docId)}&limit=250`
        : `${API_URL}/graph?limit=300`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setFullGraphData(data);
      }
    } catch (err) {
      console.error("Failed to load knowledge graph:", err);
    } finally {
      setLoadingGraph(false);
    }
  };

  const openGraphModal = (docId = "") => {
    const targetDoc = docId || selectedDocId || "";
    setGraphFilterDocId(targetDoc);
    setShowGraphModal(true);
    fetchFullGraph(targetDoc);
  };

  const handleGraphFilterChange = (newDocId) => {
    setGraphFilterDocId(newDocId);
    fetchFullGraph(newDocId);
  };

  // Handle document upload
  const handleFileUpload = async (file) => {
    if (!file) return;

    setUploading(true);
    setUploadError("");
    setUploadResult(null);
    setUploadStage("parsing");

    const formData = new FormData();
    formData.append("file", file);

    const timer1 = setTimeout(() => setUploadStage("graph"), 1200);
    const timer2 = setTimeout(() => setUploadStage("vector"), 3500);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      clearTimeout(timer1);
      clearTimeout(timer2);

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server returned status ${response.status}`);
      }

      const data = await response.json();
      setUploadStage("done");
      setUploadResult(data);
      setSelectedDocId(data.document_id);

      // Refresh document list
      await fetchDocuments();
    } catch (err) {
      console.error(err);
      setUploadError(err.message || "Failed to upload and ingest document.");
      setUploadStage("idle");
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const askQuestion = async () => {
    if (!question.trim() || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question.trim(),
          document_id: selectedDocId || null,
        }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `API returned ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(
        err.message || "Could not connect to the RAG API. Verify that the FastAPI backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      askQuestion();
    }
  };

  const defaultExamples = [
    "What database does the system depend on?",
    "Summarize the key architectural components and their roles.",
    "What technologies and versions are required?",
  ];

  return (
    <div className="app">
      {/* Subtle structural grid overlay */}
      <div className="grid-background"></div>

      {/* Navigation Bar */}
      <nav className="navbar">
        <div className="brand">
          <div className="brand-icon">
            <NetworkIcon size={18} />
          </div>
          <div>
            <div className="brand-name">Knowledge Graph RAG</div>
            <div className="brand-subtitle">
              Enterprise Hybrid Retrieval Engine
            </div>
          </div>
        </div>

        <div className="nav-controls">
          <button
            className="nav-explore-btn"
            onClick={() => openGraphModal(selectedDocId || "")}
            title="Open Interactive Knowledge Graph Visualizer"
          >
            <NetworkIcon size={15} />
            <span>Explore Graph</span>
          </button>

          <div className="doc-count-badge">
            <span className="count-number">{documents.length}</span>
            <span>Documents Loaded</span>
          </div>

          <div className="status">
            <span className="status-dot"></span>
            Hybrid Engine Active
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-container">
        {/* Hero Section */}
        <section className="hero">
          <div className="eyebrow">
            <span className="eyebrow-dot"></span>
            NEO4J × POSTGRESQL PGVECTOR × GEMINI
          </div>

          <h1>
            Enterprise Hybrid Knowledge Graph
            <br />
            <span>& Vector Retrieval Platform</span>
          </h1>

          <p className="hero-description">
            Unified multi-format document ingestion, canonical entity resolution, and
            relational graph traversal. Combines Neo4j topology with PostgreSQL pgvector
            cosine search to answer multi-hop questions with verifiable citations.
          </p>
        </section>

        {/* ============================================================ */}
        {/* DOCUMENT UPLOAD SECTION */}
        {/* ============================================================ */}
        <section className="upload-section">
          <div
            className={`dropzone ${dragOver ? "dragover" : ""} ${uploading ? "uploading-active" : ""}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => !uploading && fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: "none" }}
              accept=".pdf,.docx,.doc,.csv,.xlsx,.xls,.pptx,.ppt,.txt,.md"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />

            <div className="dropzone-icon">
              {uploading ? (
                <div className="upload-spinner"></div>
              ) : (
                <UploadIcon size={22} />
              )}
            </div>

            <div className="dropzone-content">
              <h3>
                {uploading
                  ? "Processing Document Pipeline..."
                  : "Drop file to ingest, or click to browse"}
              </h3>
              <p>
                Supported formats: <strong>PDF, DOCX, CSV, XLSX, PPTX, TXT</strong> (up to 50MB)
              </p>
            </div>

            {/* Supported format badges */}
            <div className="format-badges">
              {SUPPORTED_FORMATS.map((f, i) => (
                <span
                  key={i}
                  className="format-badge"
                  style={{ borderColor: `${f.color}40`, color: f.color }}
                >
                  {f.label}
                </span>
              ))}
            </div>

            {/* Upload Progress Stepper */}
            {uploading && (
              <div className="stepper-container" onClick={(e) => e.stopPropagation()}>
                <div className="stepper">
                  <div className={`step ${uploadStage !== "idle" ? "active" : ""}`}>
                    <span className="step-circle">1</span>
                    <span className="step-text">Parsing Text</span>
                  </div>
                  <div className="step-divider"></div>
                  <div
                    className={`step ${
                      uploadStage === "graph" || uploadStage === "vector" || uploadStage === "done"
                        ? "active"
                        : ""
                    }`}
                  >
                    <span className="step-circle">2</span>
                    <span className="step-text">Extracting Graph Triples</span>
                  </div>
                  <div className="step-divider"></div>
                  <div
                    className={`step ${
                      uploadStage === "vector" || uploadStage === "done" ? "active" : ""
                    }`}
                  >
                    <span className="step-circle">3</span>
                    <span className="step-text">Generating Embeddings</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Upload Error Banner */}
          {uploadError && (
            <div className="upload-error-banner">
              <AlertIcon size={16} />
              <span>{uploadError}</span>
            </div>
          )}

          {/* Upload Success Card */}
          {uploadResult && !uploading && (
            <div className="upload-success-card">
              <div className="success-header">
                <div className="success-badge">
                  <CheckIcon size={14} />
                  <span>INGESTION COMPLETE</span>
                </div>
                <div className="success-filename">{uploadResult.file_name}</div>
              </div>

              <div className="metrics-row">
                <div className="metric">
                  <div className="metric-val">{uploadResult.chunk_count}</div>
                  <div className="metric-lbl">Vector Chunks</div>
                </div>
                <div className="metric">
                  <div className="metric-val">{uploadResult.entity_count}</div>
                  <div className="metric-lbl">Graph Entities</div>
                </div>
                <div className="metric">
                  <div className="metric-val">{uploadResult.relationship_count}</div>
                  <div className="metric-lbl">Relationships</div>
                </div>
              </div>

              {uploadResult.sample_entities?.length > 0 && (
                <div className="sample-entities">
                  <div className="sample-label">Extracted Entities:</div>
                  <div className="tag-container">
                    {uploadResult.sample_entities.map((ent, idx) => (
                      <span key={idx} className="tag-badge">
                        {ent}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="upload-success-actions">
                <button
                  className="view-graph-btn"
                  onClick={() => openGraphModal(uploadResult.document_id)}
                >
                  <NetworkIcon size={15} />
                  <span>View Document in Knowledge Graph</span>
                </button>
              </div>
            </div>
          )}
        </section>

        {/* ============================================================ */}
        {/* DOCUMENT SELECTOR & SCOPE FILTER */}
        {/* ============================================================ */}
        {documents.length > 0 && (
          <section className="doc-filter-section">
            <div className="filter-header">
              <span className="filter-title">Active Query Scope:</span>
              <span className="filter-subtitle">
                Select a specific document or query globally across all files
              </span>
            </div>

            <div className="doc-selectors">
              <button
                className={`doc-btn ${selectedDocId === null ? "active" : ""}`}
                onClick={() => setSelectedDocId(null)}
              >
                <span className="btn-indicator-dot"></span>
                <span>All Documents</span>
                <span className="btn-count">
                  {documents.reduce((acc, d) => acc + (d.chunk_count || 0), 0)} chunks
                </span>
              </button>

              {documents.map((doc, idx) => (
                <button
                  key={idx}
                  className={`doc-btn ${selectedDocId === doc.document_id ? "active" : ""}`}
                  onClick={() => setSelectedDocId(doc.document_id)}
                >
                  <DocumentIcon size={14} />
                  <span>{doc.document_id}</span>
                  <span className="btn-count">{doc.chunk_count} chunks</span>
                </button>
              ))}
            </div>
          </section>
        )}

        {/* ============================================================ */}
        {/* QUESTION INPUT BOX */}
        {/* ============================================================ */}
        <section className="query-section">
          <div className="query-box">
            <div className="query-header">
              <div className="query-label">
                <SearchIcon size={15} />
                <span>Query Knowledge Base</span>
              </div>

              {selectedDocId && (
                <div className="active-scope-badge">
                  <span>Scoped to: <strong>{selectedDocId}</strong></span>
                  <button
                    className="clear-scope-btn"
                    onClick={() => setSelectedDocId(null)}
                    title="Query all documents"
                  >
                    <CloseIcon size={12} />
                  </button>
                </div>
              )}
            </div>

            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                selectedDocId
                  ? `Ask questions specific to ${selectedDocId}...`
                  : "Ask questions grounded in uploaded documents and entity relationships..."
              }
              rows={3}
            />

            <div className="query-bottom">
              <span className="hint">Press Enter to run query, Shift + Enter for new line</span>

              <button
                className="ask-button"
                onClick={askQuestion}
                disabled={loading || !question.trim()}
              >
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    <span>Synthesizing...</span>
                  </>
                ) : (
                  <>
                    <span>Execute Query</span>
                    <ArrowRightIcon size={14} />
                  </>
                )}
              </button>
            </div>
          </div>
        </section>

        {/* Example Questions */}
        {!result && !loading && (
          <section className="examples">
            <div className="section-label">SUGGESTED TECHNICAL QUERIES</div>

            <div className="example-grid">
              {defaultExamples.map((example, index) => (
                <button
                  key={index}
                  className="example-card"
                  onClick={() => setQuestion(example)}
                >
                  <span className="example-number">0{index + 1}</span>
                  <span className="example-text">{example}</span>
                  <ArrowUpRightIcon size={14} className="example-arrow" />
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Loading Indicator */}
        {loading && (
          <section className="loading-card">
            <div className="loading-spinner-box">
              <div className="loading-spinner"></div>
            </div>
            <div>
              <h3>Synthesizing Answer</h3>
              <p>Traversing Neo4j relational paths and ranking pgvector cosine similarities...</p>
            </div>
          </section>
        )}

        {/* Error Card */}
        {error && (
          <section className="error-card">
            <AlertIcon size={20} className="error-icon" />
            <div>
              <h3>Query Execution Error</h3>
              <p>{error}</p>
            </div>
          </section>
        )}

        {/* ============================================================ */}
        {/* QUERY RESULTS */}
        {/* ============================================================ */}
        {result && !loading && (
          <section className="results">
            {/* Generated Answer */}
            <div className="answer-card">
              <div className="card-header">
                <div>
                  <div className="card-label">
                    <span className="green-dot"></span>
                    SYNTHESIZED GROUNDED RESPONSE
                  </div>
                  <h2>Generated Answer</h2>
                </div>

                <div className="route-badge-container">
                  <span className="route-badge">{result.route.toUpperCase()}</span>
                  {result.document_id && (
                    <span className="scope-badge">DOC: {result.document_id}</span>
                  )}
                </div>
              </div>

              <div className="answer-text">{result.answer}</div>
            </div>

            {/* Retrieval Info Grid */}
            <div className="info-grid">
              <div className="info-card">
                <div className="info-label">RETRIEVAL ROUTE</div>
                <div className="info-value route-value">
                  <span className="route-indicator"></span>
                  {result.route}
                </div>
                <p>Retrieval strategy selected by the router.</p>
              </div>

              <div className="info-card">
                <div className="info-label">QUERY CLASSIFICATION</div>
                <div className="info-value">{result.query_type}</div>
                <p>Categorization determined by LLM query analysis.</p>
              </div>

              <div className="info-card">
                <div className="info-label">ROUTING CONFIDENCE</div>
                <div className="confidence-row">
                  <div className="confidence-value">
                    {Math.round(result.confidence * 100)}%
                  </div>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${Math.round(result.confidence * 100)}%`,
                      }}
                    ></div>
                  </div>
                </div>
                <p>Confidence score in the selected retrieval path.</p>
              </div>
            </div>

            {/* Entities Identified */}
            {result.entities?.length > 0 && (
              <div className="details-card">
                <div className="card-label">RECOGNIZED QUERY ENTITIES</div>
                <div className="tag-container">
                  {result.entities.map((entity, index) => (
                    <span className="tag-badge" key={index}>
                      {entity}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Graph Evidence */}
            {result.graph_evidence?.length > 0 && (
              <div className="details-card">
                <div className="details-heading">
                  <div>
                    <div className="card-label">KNOWLEDGE GRAPH EVIDENCE</div>
                    <h3>Relational Paths in Neo4j</h3>
                  </div>
                  <div className="graph-evidence-actions">
                    <div className="view-mode-toggle">
                      <button
                        className={`view-toggle-btn ${evidenceViewMode === "visual" ? "active" : ""}`}
                        onClick={() => setEvidenceViewMode("visual")}
                      >
                        <NetworkIcon size={13} />
                        <span>Interactive Graph</span>
                      </button>
                      <button
                        className={`view-toggle-btn ${evidenceViewMode === "raw" ? "active" : ""}`}
                        onClick={() => setEvidenceViewMode("raw")}
                      >
                        <ListIcon size={13} />
                        <span>Paths ({result.graph_evidence.length})</span>
                      </button>
                    </div>
                  </div>
                </div>

                {evidenceViewMode === "visual" ? (
                  <div className="query-graph-wrapper">
                    <KnowledgeGraphVisualizer
                      data={convertEvidenceToGraph(result.graph_evidence)}
                      title="Query Evidence Subgraph"
                      height={400}
                    />
                  </div>
                ) : (
                  <div className="graph-list">
                    {result.graph_evidence.map((evidence, index) => (
                      <div className="graph-item" key={index}>
                        <div className="graph-top">
                          <span className="relationship">{evidence.relationship}</span>
                          <span className="graph-confidence">
                            {Math.round(evidence.confidence * 100)}% confidence
                          </span>
                        </div>

                        <div className="graph-nodes">
                          {evidence.nodes?.map((node, nodeIndex) => (
                            <div className="graph-node" key={nodeIndex}>
                              <span className="node-type">{node.entity_type}</span>
                              <span className="node-name">{node.name}</span>
                              {nodeIndex < evidence.nodes.length - 1 && (
                                <span className="node-arrow">→</span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Source Chunks */}
            {result.sources?.length > 0 && (
              <div className="details-card">
                <div className="details-heading">
                  <div>
                    <div className="card-label">PGVECTOR EVIDENCE</div>
                    <h3>Retrieved Text Chunks</h3>
                  </div>
                  <span className="count">{result.sources.length} Chunks</span>
                </div>

                <div className="source-list">
                  {result.sources.map((source, index) => (
                    <div className="source-item" key={index}>
                      <span className="source-index">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      <span className="source-content">{source}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              className="new-question-btn"
              onClick={() => {
                setResult(null);
                setQuestion("");
              }}
            >
              <ArrowLeftIcon size={14} />
              <span>Ask another question</span>
            </button>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-container">
          <div className="footer-left">
            <span className="footer-brand">Hybrid Graph RAG v2.0</span>
            <span className="footer-sep">/</span>
            <span className="footer-tech">Neo4j × PostgreSQL pgvector × Gemini</span>
          </div>

          <div className="footer-right">
            <button
              className="footer-link-btn"
              onClick={() => setLegalModalTab("privacy")}
            >
              Privacy Policy
            </button>
            <span className="footer-dot">•</span>
            <button
              className="footer-link-btn"
              onClick={() => setLegalModalTab("terms")}
            >
              Terms & Conditions
            </button>
            <span className="footer-dot">•</span>
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="footer-link-btn"
            >
              API Reference
            </a>
          </div>
        </div>
      </footer>

      {/* ============================================================ */}
      {/* FULL KNOWLEDGE GRAPH EXPLORER MODAL */}
      {/* ============================================================ */}
      {showGraphModal && (
        <div className="kg-modal-overlay" onClick={() => setShowGraphModal(false)}>
          <div
            className="kg-modal-content"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="kg-modal-header">
              <div className="kg-modal-title-wrap">
                <div className="kg-modal-title">
                  <NetworkIcon size={18} />
                  <span>Knowledge Graph Explorer</span>
                </div>
                <p className="kg-modal-subtitle">
                  Inspect extracted entities, canonical types, and relational paths persisted in Neo4j.
                </p>
              </div>

              <div className="kg-modal-controls">
                <div className="kg-select-wrap">
                  <label className="kg-select-label">Document Scope:</label>
                  <select
                    className="kg-doc-select"
                    value={graphFilterDocId}
                    onChange={(e) => handleGraphFilterChange(e.target.value)}
                  >
                    <option value="">All Documents (Global Graph)</option>
                    {documents.map((doc) => (
                      <option key={doc.document_id} value={doc.document_id}>
                        {doc.document_id} ({doc.chunk_count} chunks)
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  className="kg-modal-close-btn"
                  onClick={() => setShowGraphModal(false)}
                  title="Close Explorer"
                >
                  <CloseIcon size={16} />
                </button>
              </div>
            </div>

            <div className="kg-modal-body">
              {loadingGraph ? (
                <div className="kg-loading-box">
                  <div className="kg-spinner"></div>
                  <span>Fetching graph nodes and relationships from Neo4j...</span>
                </div>
              ) : fullGraphData && fullGraphData.nodes && fullGraphData.nodes.length > 0 ? (
                <KnowledgeGraphVisualizer
                  data={fullGraphData}
                  title={
                    graphFilterDocId
                      ? `Scope: ${graphFilterDocId}`
                      : "Complete Enterprise Knowledge Graph"
                  }
                  height={620}
                />
              ) : (
                <div className="kg-empty-box">
                  <NetworkIcon size={32} />
                  <h4>No Graph Topology Found</h4>
                  <p>
                    There are no entities or relationships matching the selected document scope in Neo4j.
                  </p>
                  <span className="kg-empty-hint">
                    Upload a document first or switch scope to "All Documents".
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ============================================================ */}
      {/* PRIVACY POLICY & TERMS MODAL */}
      {/* ============================================================ */}
      {legalModalTab && (
        <LegalModal
          initialTab={legalModalTab}
          onClose={() => setLegalModalTab(null)}
        />
      )}
    </div>
  );
}

export default App;
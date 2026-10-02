import React, { useRef, useEffect, useState, useCallback } from "react";
import {
  PlayIcon,
  PauseIcon,
  ResetIcon,
  MaximizeIcon,
  MinimizeIcon,
  CloseIcon,
} from "./Icons";
import "./KnowledgeGraphVisualizer.css";

// Color mapping by entity type (Clean high-contrast technical palette)
const TYPE_COLORS = {
  Product: "#3b82f6",
  Database: "#06b6d4",
  Technology: "#6366f1",
  Company: "#10b981",
  API: "#f59e0b",
  Component: "#14b8a6",
  Feature: "#0ea5e9",
  Version: "#94a3b8",
  Document: "#64748b",
  default: "#10b981",
};

export default function KnowledgeGraphVisualizer({
  data, // { nodes: [{id, name, entity_type}], links: [{source, target, relationship, confidence}] }
  title = "Knowledge Graph",
  height = 520,
  onNodeClick = null,
}) {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);

  // Simulation state refs (avoid React re-render loops on animation frame)
  const simRef = useRef({
    nodes: [],
    links: [],
    transform: { x: 0, y: 0, k: 1 },
    draggedNode: null,
    isPanning: false,
    panStart: { x: 0, y: 0 },
    hoveredNode: null,
    animFrameId: null,
    isRunning: true,
  });

  const [hoverInfo, setHoverInfo] = useState(null);
  const [stats, setStats] = useState({ nodes: 0, links: 0 });
  const [isPaused, setIsPaused] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Initialize and update simulation graph data
  useEffect(() => {
    if (!data || !data.nodes) return;

    const width = containerRef.current?.clientWidth || 800;
    const canvasHeight = isFullscreen ? window.innerHeight - 80 : height;

    // Build node map
    const nodeMap = new Map();
    const simNodes = data.nodes.map((n, i) => {
      // Random circular initial layout
      const angle = (i / data.nodes.length) * 2 * Math.PI;
      const radius = Math.min(width, canvasHeight) * 0.35 * Math.random();
      const node = {
        id: n.id || n.name,
        name: n.name,
        type: n.entity_type || n.type || "Entity",
        x: width / 2 + Math.cos(angle) * radius,
        y: canvasHeight / 2 + Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        radius: 18,
        degree: 0,
      };
      nodeMap.set(node.id, node);
      return node;
    });

    // Build link references and degree counts
    const simLinks = (data.links || [])
      .map((l) => {
        const sourceNode =
          typeof l.source === "object" ? l.source : nodeMap.get(l.source);
        const targetNode =
          typeof l.target === "object" ? l.target : nodeMap.get(l.target);

        if (sourceNode && targetNode) {
          sourceNode.degree = (sourceNode.degree || 0) + 1;
          targetNode.degree = (targetNode.degree || 0) + 1;
          return {
            source: sourceNode,
            target: targetNode,
            relationship: l.relationship || l.type || "CONNECTED_TO",
            confidence: l.confidence || 1.0,
          };
        }
        return null;
      })
      .filter(Boolean);

    // Dynamic node radius by degree
    simNodes.forEach((n) => {
      n.radius = Math.min(32, Math.max(16, 16 + (n.degree || 0) * 2.5));
    });

    simRef.current.nodes = simNodes;
    simRef.current.links = simLinks;
    simRef.current.transform = { x: 0, y: 0, k: 1 };
    setStats({ nodes: simNodes.length, links: simLinks.length });
  }, [data, height, isFullscreen]);

  // Main Canvas Rendering & Physics Engine
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    let isDestroyed = false;

    const render = () => {
      if (isDestroyed) return;

      const width = canvas.width;
      const canvasHeight = canvas.height;
      const { nodes, links, transform, isRunning, draggedNode, hoveredNode } =
        simRef.current;

      // -------------------------------------------------------------
      // 1. PHYSICS SIMULATION STEP (Spring-Charge Force Model)
      // -------------------------------------------------------------
      if (isRunning && nodes.length > 0) {
        const repulsionK = 2200;
        const springK = 0.04;
        const targetDistance = 140;
        const centerGravity = 0.015;
        const damping = 0.86;

        // Node repulsion
        for (let i = 0; i < nodes.length; i++) {
          const n1 = nodes[i];
          for (let j = i + 1; j < nodes.length; j++) {
            const n2 = nodes[j];
            const dx = n2.x - n1.x;
            const dy = n2.y - n1.y;
            const dist = Math.hypot(dx, dy) || 1;
            if (dist < 400) {
              const force = repulsionK / (dist * dist);
              const fx = (dx / dist) * force;
              const fy = (dy / dist) * force;
              n1.vx -= fx;
              n1.vy -= fy;
              n2.vx += fx;
              n2.vy += fy;
            }
          }

          // Center gravity
          n1.vx += (width / 2 - n1.x) * centerGravity;
          n1.vy += (canvasHeight / 2 - n1.y) * centerGravity;
        }

        // Link spring attraction
        links.forEach((link) => {
          const { source, target } = link;
          const dx = target.x - source.x;
          const dy = target.y - source.y;
          const dist = Math.hypot(dx, dy) || 1;
          const force = (dist - targetDistance) * springK;
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;

          source.vx += fx;
          source.vy += fy;
          target.vx -= fx;
          target.vy -= fy;
        });

        // Update positions with damping
        nodes.forEach((n) => {
          if (n !== draggedNode) {
            n.vx *= damping;
            n.vy *= damping;
            n.x += n.vx;
            n.y += n.vy;
          }
        });
      }

      // -------------------------------------------------------------
      // 2. CANVAS DRAWING
      // -------------------------------------------------------------
      ctx.clearRect(0, 0, width, canvasHeight);
      ctx.save();
      ctx.translate(transform.x, transform.y);
      ctx.scale(transform.k, transform.k);

      // Connected nodes/links to hover
      const connectedNodeIds = new Set();
      if (hoveredNode) {
        connectedNodeIds.add(hoveredNode.id);
        links.forEach((l) => {
          if (l.source.id === hoveredNode.id) connectedNodeIds.add(l.target.id);
          if (l.target.id === hoveredNode.id) connectedNodeIds.add(l.source.id);
        });
      }

      // Draw Links
      links.forEach((link) => {
        const isHighlight =
          hoveredNode &&
          (link.source.id === hoveredNode.id ||
            link.target.id === hoveredNode.id);
        const isDim = hoveredNode && !isHighlight;

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(link.source.x, link.source.y);
        ctx.lineTo(link.target.x, link.target.y);

        ctx.strokeStyle = isHighlight
          ? "#3b82f6"
          : isDim
          ? "rgba(255, 255, 255, 0.04)"
          : "rgba(255, 255, 255, 0.16)";
        ctx.lineWidth = isHighlight ? 2.5 : 1.2;

        if (isHighlight) {
          ctx.shadowColor = "#3b82f6";
          ctx.shadowBlur = 8;
        }
        ctx.stroke();
        ctx.restore();

        // Draw Relationship Arrow
        const dx = link.target.x - link.source.x;
        const dy = link.target.y - link.source.y;
        const dist = Math.hypot(dx, dy) || 1;
        const arrowAngle = Math.atan2(dy, dx);
        const arrowDist = dist - link.target.radius - 4;
        const arrowX = link.source.x + Math.cos(arrowAngle) * arrowDist;
        const arrowY = link.source.y + Math.sin(arrowAngle) * arrowDist;

        ctx.save();
        ctx.fillStyle = isHighlight ? "#3b82f6" : "rgba(255, 255, 255, 0.4)";
        ctx.beginPath();
        ctx.moveTo(arrowX, arrowY);
        ctx.lineTo(
          arrowX - 8 * Math.cos(arrowAngle - Math.PI / 6),
          arrowY - 8 * Math.sin(arrowAngle - Math.PI / 6)
        );
        ctx.lineTo(
          arrowX - 8 * Math.cos(arrowAngle + Math.PI / 6),
          arrowY - 8 * Math.sin(arrowAngle + Math.PI / 6)
        );
        ctx.closePath();
        ctx.fill();
        ctx.restore();

        // Draw Relationship Label at midpoint (if zoomed in or highlighted)
        if (transform.k > 0.7 || isHighlight) {
          const midX = (link.source.x + link.target.x) / 2;
          const midY = (link.source.y + link.target.y) / 2;
          ctx.save();
          ctx.font = "9px Inter, sans-serif";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";

          // Label background badge
          const label = link.relationship;
          const textWidth = ctx.measureText(label).width;
          ctx.fillStyle = "rgba(10, 10, 16, 0.85)";
          ctx.beginPath();
          ctx.roundRect(midX - textWidth / 2 - 4, midY - 7, textWidth + 8, 14, 4);
          ctx.fill();
          ctx.strokeStyle = isHighlight
            ? "rgba(59, 130, 246, 0.7)"
            : "rgba(255, 255, 255, 0.12)";
          ctx.stroke();

          ctx.fillStyle = isHighlight ? "#93c5fd" : "#9999a5";
          ctx.fillText(label, midX, midY);
          ctx.restore();
        }
      });

      // Draw Nodes
      nodes.forEach((node) => {
        const isHovered = hoveredNode && node.id === hoveredNode.id;
        const isConnected = connectedNodeIds.has(node.id);
        const isDim = hoveredNode && !isConnected;

        const color = TYPE_COLORS[node.type] || TYPE_COLORS.default;

        ctx.save();
        ctx.globalAlpha = isDim ? 0.25 : 1.0;

        // Outer glow
        ctx.shadowColor = color;
        ctx.shadowBlur = isHovered ? 25 : 12;

        // Node circle
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI);
        ctx.fillStyle = isHovered ? "#ffffff" : color;
        ctx.fill();

        // Dark center core
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius - 3, 0, 2 * Math.PI);
        ctx.fillStyle = "#0c0c14";
        ctx.shadowBlur = 0;
        ctx.fill();

        // Inner entity icon / dot
        ctx.beginPath();
        ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();

        // Node Label
        ctx.font = isHovered
          ? "600 12px Inter, sans-serif"
          : "500 11px Inter, sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "top";

        // Label halo for readability
        ctx.strokeStyle = "rgba(5, 5, 8, 0.9)";
        ctx.lineWidth = 3;
        ctx.strokeText(node.name, node.x, node.y + node.radius + 6);

        ctx.fillStyle = isHovered ? "#ffffff" : "#e6e6ed";
        ctx.fillText(node.name, node.x, node.y + node.radius + 6);

        // Entity Type small badge below
        ctx.font = "8px Inter, sans-serif";
        ctx.fillStyle = color;
        ctx.fillText(
          node.type.toUpperCase(),
          node.x,
          node.y + node.radius + 20
        );

        ctx.restore();
      });

      ctx.restore();
      simRef.current.animFrameId = requestAnimationFrame(render);
    };

    simRef.current.animFrameId = requestAnimationFrame(render);

    return () => {
      isDestroyed = true;
      cancelAnimationFrame(simRef.current.animFrameId);
    };
  }, []);

  // Resize canvas when container size changes
  useEffect(() => {
    const updateCanvasSize = () => {
      const canvas = canvasRef.current;
      const container = containerRef.current;
      if (!canvas || !container) return;
      canvas.width = container.clientWidth;
      canvas.height = isFullscreen ? window.innerHeight - 80 : height;
    };

    updateCanvasSize();
    window.addEventListener("resize", updateCanvasSize);
    return () => window.removeEventListener("resize", updateCanvasSize);
  }, [height, isFullscreen]);

  // Coordinate transforms
  const screenToWorld = useCallback((screenX, screenY) => {
    const { transform } = simRef.current;
    return {
      x: (screenX - transform.x) / transform.k,
      y: (screenY - transform.y) / transform.k,
    };
  }, []);

  const getNodeAt = useCallback(
    (screenX, screenY) => {
      const world = screenToWorld(screenX, screenY);
      const { nodes } = simRef.current;
      for (let i = nodes.length - 1; i >= 0; i--) {
        const n = nodes[i];
        if (Math.hypot(n.x - world.x, n.y - world.y) <= n.radius + 4) {
          return n;
        }
      }
      return null;
    },
    [screenToWorld]
  );

  // Mouse & Touch Interaction Handlers
  const handleMouseDown = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const clickedNode = getNodeAt(x, y);
    if (clickedNode) {
      simRef.current.draggedNode = clickedNode;
      if (onNodeClick) onNodeClick(clickedNode);
    } else {
      simRef.current.isPanning = true;
      simRef.current.panStart = {
        x: e.clientX - simRef.current.transform.x,
        y: e.clientY - simRef.current.transform.y,
      };
    }
  };

  const handleMouseMove = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    // Dragging Node
    if (simRef.current.draggedNode) {
      const world = screenToWorld(x, y);
      simRef.current.draggedNode.x = world.x;
      simRef.current.draggedNode.y = world.y;
      simRef.current.draggedNode.vx = 0;
      simRef.current.draggedNode.vy = 0;
      return;
    }

    // Panning Canvas
    if (simRef.current.isPanning) {
      simRef.current.transform.x = e.clientX - simRef.current.panStart.x;
      simRef.current.transform.y = e.clientY - simRef.current.panStart.y;
      return;
    }

    // Hover detection
    const hovered = getNodeAt(x, y);
    simRef.current.hoveredNode = hovered;
    if (hovered) {
      setHoverInfo({
        name: hovered.name,
        type: hovered.type,
        degree: hovered.degree,
        x: e.clientX,
        y: e.clientY,
      });
    } else {
      setHoverInfo(null);
    }
  };

  const handleMouseUp = () => {
    simRef.current.draggedNode = null;
    simRef.current.isPanning = false;
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const rect = canvasRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
    const { transform } = simRef.current;
    const newK = Math.min(3.5, Math.max(0.25, transform.k * zoomFactor));

    transform.x = mouseX - (mouseX - transform.x) * (newK / transform.k);
    transform.y = mouseY - (mouseY - transform.y) * (newK / transform.k);
    transform.k = newK;
  };

  const resetView = () => {
    simRef.current.transform = { x: 0, y: 0, k: 1 };
  };

  const toggleSimulation = () => {
    simRef.current.isRunning = !simRef.current.isRunning;
    setIsPaused(!simRef.current.isRunning);
  };

  const zoomIn = () => {
    const { transform } = simRef.current;
    transform.k = Math.min(3.5, transform.k * 1.25);
  };

  const zoomOut = () => {
    const { transform } = simRef.current;
    transform.k = Math.max(0.25, transform.k * 0.8);
  };

  return (
    <div
      ref={containerRef}
      className={`kg-visualizer-container ${isFullscreen ? "fullscreen" : ""}`}
      style={{ height: isFullscreen ? "100vh" : `${height}px` }}
    >
      {/* Top Header Bar */}
      <div className="kg-header">
        <div className="kg-title-row">
          <span className="kg-pulse-icon"></span>
          <span className="kg-title">{title}</span>
          <div className="kg-stats-badge">
            <span>{stats.nodes} Nodes</span>
            <span>/</span>
            <span>{stats.links} Edges</span>
          </div>
        </div>

        {/* Action Controls Toolbar */}
        <div className="kg-toolbar">
          <button onClick={zoomIn} title="Zoom In" className="kg-tool-btn">
            +
          </button>
          <button onClick={zoomOut} title="Zoom Out" className="kg-tool-btn">
            -
          </button>
          <button onClick={resetView} title="Reset View" className="kg-tool-btn">
            <ResetIcon size={13} />
          </button>
          <button
            onClick={toggleSimulation}
            title={isPaused ? "Resume Physics" : "Pause Physics"}
            className={`kg-tool-btn ${isPaused ? "active" : ""}`}
          >
            {isPaused ? <PlayIcon size={12} /> : <PauseIcon size={12} />}
          </button>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            title={isFullscreen ? "Exit Fullscreen" : "Fullscreen View"}
            className="kg-tool-btn"
          >
            {isFullscreen ? <CloseIcon size={13} /> : <MaximizeIcon size={13} />}
          </button>
        </div>
      </div>

      {/* Main HTML5 Canvas */}
      <canvas
        ref={canvasRef}
        className="kg-canvas"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      />

      {/* Hover Info Tooltip */}
      {hoverInfo && (
        <div
          className="kg-hover-card"
          style={{
            left: `${hoverInfo.x + 14}px`,
            top: `${hoverInfo.y + 14}px`,
          }}
        >
          <div className="kg-hover-header">
            <span
              className="kg-hover-type-badge"
              style={{
                borderColor: `${TYPE_COLORS[hoverInfo.type] || "#67f59b"}60`,
                color: TYPE_COLORS[hoverInfo.type] || "#67f59b",
              }}
            >
              {hoverInfo.type}
            </span>
            <span className="kg-hover-connections">
              {hoverInfo.degree} relations
            </span>
          </div>
          <div className="kg-hover-name">{hoverInfo.name}</div>
        </div>
      )}

      {/* Bottom Entity Type Legend */}
      <div className="kg-legend">
        {Object.entries(TYPE_COLORS)
          .filter(([k]) => k !== "default")
          .map(([type, color]) => (
            <div key={type} className="kg-legend-item">
              <span
                className="kg-legend-dot"
                style={{ backgroundColor: color, boxShadow: `0 0 8px ${color}` }}
              ></span>
              <span className="kg-legend-label">{type}</span>
            </div>
          ))}
      </div>
    </div>
  );
}

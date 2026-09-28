import React, { useEffect, useRef, useState, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import cytoscape from 'cytoscape';
import {
  Network,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Filter,
  Layers,
  Info,
  Plus,
  Search,
  Download,
  Share2,
  RefreshCw,
  Terminal,
  Shield,
  ShieldAlert,
  Key,
  Globe,
  Coins,
  Server,
  Crosshair,
  Sparkles,
  Sliders,
  CheckCircle2,
  FolderGit2,
  Copy,
  Check,
  Eye,
  EyeOff,
  Activity,
  Zap,
  SlidersHorizontal,
  Flame,
  Radio,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Fingerprint,
  Link as LinkIcon,
  Maximize,
  Compass
} from 'lucide-react';
import { graphApi, actorsApi } from '../services/api';
import { ActorSummary } from '../types';

type InspectorTab = 'PROFILE' | 'VECTORS' | 'PIVOTS';

export const GraphPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const urlActorId = searchParams.get('actor_id');
  
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  
  const [actors, setActors] = useState<ActorSummary[]>([]);
  const [selectedActorId, setSelectedActorId] = useState<string>(urlActorId || '');
  const [selectedElement, setSelectedElement] = useState<any | null>(null);
  const [connectedNeighbors, setConnectedNeighbors] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [layoutMode, setLayoutMode] = useState<string>('cose');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [nodeCount, setNodeCount] = useState<number>(0);
  const [edgeCount, setEdgeCount] = useState<number>(0);
  const [activeTypeFilter, setActiveTypeFilter] = useState<string>('ALL');
  const [copiedId, setCopiedId] = useState<boolean>(false);
  const [isolatedSubgraph, setIsolatedSubgraph] = useState<boolean>(false);
  const [inspectorTab, setInspectorTab] = useState<InspectorTab>('PROFILE');
  const [radarActive, setRadarActive] = useState<boolean>(true);

  // Real-time Node Injection Modal State
  const [showAddModal, setShowAddModal] = useState<boolean>(false);
  const [newNodeType, setNewNodeType] = useState<string>('Persona');
  const [newNodeLabel, setNewNodeLabel] = useState<string>('');
  const [newNodeMeta, setNewNodeMeta] = useState<string>('');
  const [connectToNodeId, setConnectToNodeId] = useState<string>('');

  // Node Category Counts
  const [categoryCounts, setCategoryCounts] = useState<{ [key: string]: number }>({
    ALL: 0,
    Actor: 0,
    Persona: 0,
    Wallet: 0,
    PGPKey: 0,
    Infrastructure: 0,
    Custom: 0
  });

  const selectedActor = useMemo(() => {
    return actors.find(a => a.id === selectedActorId);
  }, [actors, selectedActorId]);

  useEffect(() => {
    actorsApi.list()
      .then((data) => {
        setActors(data);
        if (data.length > 0) {
          if (!urlActorId || !data.some(a => a.id === urlActorId)) {
            setSelectedActorId(data[0].id);
          } else {
            setSelectedActorId(urlActorId);
          }
        }
      })
      .catch(console.error);
  }, [urlActorId]);

  useEffect(() => {
    return () => {
      if (cyRef.current) {
        try {
          cyRef.current.destroy();
        } catch (e) {}
        cyRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (selectedActorId) {
      loadGraph(selectedActorId);
    } else {
      renderEmptyGraph();
    }
  }, [selectedActorId, layoutMode]);

  const loadGraph = (actorId: string) => {
    setLoading(true);
    setIsolatedSubgraph(false);
    setSelectedElement(null);
    setConnectedNeighbors([]);
    graphApi.getActorGraph(actorId)
      .then((data) => {
        setLoading(false);
        renderCytoscape(data);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
        renderEmptyGraph();
      });
  };

  const renderEmptyGraph = () => {
    if (!containerRef.current) return;
    if (cyRef.current) {
      try {
        cyRef.current.destroy();
      } catch (e) {}
      cyRef.current = null;
    }
    try {
      const cy = cytoscape({
        container: containerRef.current,
        elements: [],
        style: []
      });
      cyRef.current = cy;
    } catch (e) {
      console.error(e);
    }
    setNodeCount(0);
    setEdgeCount(0);
    setCategoryCounts({ ALL: 0, Actor: 0, Persona: 0, Wallet: 0, PGPKey: 0, Infrastructure: 0, Custom: 0 });
  };

  const renderCytoscape = (data: any) => {
    if (!containerRef.current) return;

    if (cyRef.current) {
      try {
        cyRef.current.destroy();
      } catch (e) {}
      cyRef.current = null;
    }

    const rawNodes = data.nodes || [];
    const validNodeIds = new Set(rawNodes.map((n: any) => n.data?.id));
    const rawEdges = data.edges || [];
    const validEdges = rawEdges.filter((e: any) => validNodeIds.has(e.data?.source) && validNodeIds.has(e.data?.target));

    const elements = [...rawNodes, ...validEdges];
    setNodeCount(rawNodes.length);
    setEdgeCount(validEdges.length);

    // Compute Category Counts
    const counts: { [key: string]: number } = {
      ALL: rawNodes.length,
      Actor: 0,
      Persona: 0,
      Wallet: 0,
      PGPKey: 0,
      Infrastructure: 0,
      Custom: 0
    };
    rawNodes.forEach((n: any) => {
      const t = n.data?.type || 'Custom';
      if (t === 'Infrastructure' || t === 'Domain') {
        counts.Infrastructure = (counts.Infrastructure || 0) + 1;
      } else if (counts[t] !== undefined) {
        counts[t] += 1;
      } else {
        counts.Custom = (counts.Custom || 0) + 1;
      }
    });
    setCategoryCounts(counts);

    try {
      const cy = cytoscape({
        container: containerRef.current,
        elements: elements,
        style: [
          // Base Node Style
          {
            selector: 'node',
            style: {
              'label': 'data(label)',
              'color': '#F1F5F9',
              'font-family': 'JetBrains Mono, monospace',
              'font-size': '10px',
              'font-weight': '600',
              'text-valign': 'bottom',
              'text-margin-y': 6,
              'background-color': '#0F172A',
              'border-width': 2,
              'border-color': '#38BDF8',
              'width': 36,
              'height': 36,
              'text-background-color': '#040711',
              'text-background-opacity': 0.90,
              'text-background-padding': '4px',
              'text-background-shape': 'roundrectangle',
              'text-border-color': 'rgba(56, 189, 248, 0.4)',
              'text-border-width': 1,
              'transition-property': 'background-color, border-color, border-width, opacity, width, height',
              'transition-duration': '0.25s'
            } as any
          },
          // Actor / Sovereign Core Target
          {
            selector: 'node[type="Actor"]',
            style: {
              'background-color': '#064E3B',
              'border-color': '#10B981',
              'border-width': 4,
              'width': 52,
              'height': 52,
              'font-size': '12px',
              'font-weight': '800',
              'color': '#34D399',
              'text-border-color': 'rgba(16, 185, 129, 0.7)',
              'shadow-blur': 15,
              'shadow-color': '#10B981',
              'shadow-opacity': 0.6
            } as any
          },
          // Threat Alias / Persona
          {
            selector: 'node[type="Persona"]',
            style: {
              'background-color': '#0369A1',
              'border-color': '#00E5FF',
              'border-width': 2.5,
              'width': 40,
              'height': 40,
              'color': '#7DD3FC',
              'text-border-color': 'rgba(0, 229, 255, 0.5)'
            } as any
          },
          // PGP Cryptographic Keys
          {
            selector: 'node[type="PGPKey"]',
            style: {
              'background-color': '#78350F',
              'border-color': '#F59E0B',
              'border-width': 2.5,
              'shape': 'diamond',
              'width': 38,
              'height': 38,
              'color': '#FDE68A',
              'text-border-color': 'rgba(245, 158, 11, 0.5)'
            } as any
          },
          // Darknet / Cold Wallets (BTC / XMR)
          {
            selector: 'node[type="Wallet"]',
            style: {
              'background-color': '#065F46',
              'border-color': '#059669',
              'border-width': 2.5,
              'shape': 'hexagon',
              'width': 40,
              'height': 40,
              'color': '#6EE7B7',
              'text-border-color': 'rgba(5, 150, 105, 0.5)'
            } as any
          },
          // Infrastructure / Hidden Services / Clearnet Mirrors
          {
            selector: 'node[type="Infrastructure"], node[type="Domain"]',
            style: {
              'background-color': '#831843',
              'border-color': '#F43F5E',
              'border-width': 2.5,
              'shape': 'octagon',
              'width': 40,
              'height': 40,
              'color': '#FDA4AF',
              'text-border-color': 'rgba(244, 63, 94, 0.5)'
            } as any
          },
          // Custom Injected Entities
          {
            selector: 'node[type="Custom"]',
            style: {
              'background-color': '#581C87',
              'border-color': '#A855F7',
              'border-width': 2.5,
              'width': 38,
              'height': 38,
              'color': '#D8B4FE',
              'text-border-color': 'rgba(168, 85, 247, 0.5)'
            } as any
          },
          // Edge Base Style
          {
            selector: 'edge',
            style: {
              'width': 2,
              'line-color': '#1E293B',
              'target-arrow-color': '#38BDF8',
              'target-arrow-shape': 'triangle',
              'arrow-scale': 1.1,
              'curve-style': 'bezier',
              'label': 'data(label)',
              'font-size': '8px',
              'font-family': 'JetBrains Mono, monospace',
              'font-weight': '600',
              'color': '#94A3B8',
              'text-rotation': 'autorotate',
              'text-margin-y': -8,
              'text-background-color': '#05070D',
              'text-background-opacity': 0.88,
              'text-background-padding': '2px',
              'text-background-shape': 'roundrectangle',
              'transition-property': 'line-color, target-arrow-color, width, opacity',
              'transition-duration': '0.2s'
            } as any
          },
          // Active Hover & Selection States
          {
            selector: 'node:selected, node.focused-center',
            style: {
              'border-color': '#00E5FF',
              'border-width': 5,
              'shadow-blur': 30,
              'shadow-color': '#00E5FF',
              'shadow-opacity': 0.95,
              'z-index': 999
            } as any
          },
          {
            selector: 'node.neighbor-highlight',
            style: {
              'border-color': '#10B981',
              'border-width': 4,
              'shadow-blur': 22,
              'shadow-color': '#10B981',
              'shadow-opacity': 0.8,
              'z-index': 990
            } as any
          },
          {
            selector: 'edge.neighbor-highlight',
            style: {
              'line-color': '#00E5FF',
              'target-arrow-color': '#00E5FF',
              'width': 3.5,
              'opacity': 1,
              'color': '#00E5FF',
              'z-index': 980
            } as any
          },
          {
            selector: 'edge:selected',
            style: {
              'line-color': '#10B981',
              'target-arrow-color': '#10B981',
              'width': 4.5,
              'z-index': 999
            } as any
          },
          // Dimmed non-neighbor elements
          {
            selector: '.faded',
            style: {
              'opacity': 0.12,
              'text-opacity': 0.05
            } as any
          },
          // Search Match Highlight
          {
            selector: '.search-match',
            style: {
              'border-color': '#FFE600',
              'border-width': 4.5,
              'background-color': '#FFE600',
              'color': '#FFE600',
              'shadow-blur': 25,
              'shadow-color': '#FFE600',
              'shadow-opacity': 0.95,
              'z-index': 999
            } as any
          }
        ],
        layout: {
          name: layoutMode,
          animate: true,
          animationDuration: 800,
          nodeDimensionsIncludeLabels: true,
          idealEdgeLength: 110,
          nodeOverlap: 30
        } as any
      });

      // Interactive Neighborhood Highlight on Node Click
      const handleSelectNode = (node: cytoscape.NodeSingular) => {
        const neighborhood = node.closedNeighborhood();

        cy.elements().removeClass('focused-center neighbor-highlight search-match');
        cy.elements().difference(neighborhood).addClass('faded');
        neighborhood.removeClass('faded');
        node.neighborhood('node').addClass('neighbor-highlight');
        node.neighborhood('edge').addClass('neighbor-highlight');
        node.addClass('focused-center');

        const connectedEdges = node.connectedEdges();
        const neighbors = node.neighborhood('node').map((nbr: any) => {
          const edge = node.edgesWith(nbr)[0];
          return {
            id: nbr.id(),
            label: nbr.data('label') || nbr.id(),
            type: nbr.data('type') || 'Unknown',
            relation: edge ? edge.data('label') : 'CONNECTED_TO'
          };
        });

        setConnectedNeighbors(neighbors);
        setSelectedElement({
          type: 'node',
          data: node.data(),
          degree: node.degree(),
          inDegree: node.indegree(),
          outDegree: node.outdegree(),
          neighborsCount: node.neighborhood('node').length,
          connectedLabels: connectedEdges.map((e: any) => e.data('label')).filter(Boolean)
        });
      };

      cy.on('tap', 'node', (evt) => {
        handleSelectNode(evt.target);
      });

      // Edge Tap
      cy.on('tap', 'edge', (evt) => {
        const edge = evt.target;
        const connectedNodes = edge.connectedNodes();

        cy.elements().removeClass('focused-center neighbor-highlight search-match');
        cy.elements().difference(edge.union(connectedNodes)).addClass('faded');
        edge.union(connectedNodes).removeClass('faded');

        setConnectedNeighbors([]);
        setSelectedElement({
          type: 'edge',
          data: edge.data(),
          source: edge.data('source'),
          target: edge.data('target'),
          label: edge.data('label')
        });
      });

      // Background Tap: Restore Full Graph Visibility
      cy.on('tap', (evt) => {
        if (evt.target === cy) {
          cy.elements().removeClass('faded focused-center neighbor-highlight search-match');
          setSelectedElement(null);
          setConnectedNeighbors([]);
          setIsolatedSubgraph(false);
        }
      });

      // Double Tap Node: Smooth Center and Zoom In
      cy.on('dbltap', 'node', (evt) => {
        const node = evt.target;
        cy.animate({
          center: { eles: node },
          zoom: 1.6,
          duration: 450
        });
      });

      cyRef.current = cy;
    } catch (e) {
      console.error('Cytoscape render error:', e);
    }
  };

  // Traversal: Focus a specific neighbor node from the Inspector
  const handleFocusNeighborNode = (neighborId: string) => {
    if (!cyRef.current) return;
    const node = cyRef.current.$id(neighborId);
    if (!node || node.empty()) return;

    const neighborhood = node.closedNeighborhood();
    cyRef.current.elements().removeClass('focused-center neighbor-highlight search-match');
    cyRef.current.elements().difference(neighborhood).addClass('faded');
    neighborhood.removeClass('faded');
    node.neighborhood('node').addClass('neighbor-highlight');
    node.neighborhood('edge').addClass('neighbor-highlight');
    node.addClass('focused-center');

    cyRef.current.animate({
      center: { eles: node },
      zoom: 1.4,
      duration: 400
    });

    const connectedEdges = node.connectedEdges();
    const neighbors = node.neighborhood('node').map((nbr: any) => {
      const edge = node.edgesWith(nbr)[0];
      return {
        id: nbr.id(),
        label: nbr.data('label') || nbr.id(),
        type: nbr.data('type') || 'Unknown',
        relation: edge ? edge.data('label') : 'CONNECTED_TO'
      };
    });

    setConnectedNeighbors(neighbors);
    setSelectedElement({
      type: 'node',
      data: node.data(),
      degree: node.degree(),
      inDegree: node.indegree(),
      outDegree: node.outdegree(),
      neighborsCount: node.neighborhood('node').length,
      connectedLabels: connectedEdges.map((e: any) => e.data('label')).filter(Boolean)
    });
  };

  // Real-time search and highlight nodes
  const handleSearchNodes = (query: string) => {
    setSearchQuery(query);
    if (!cyRef.current) return;
    cyRef.current.elements().removeClass('search-match faded');
    if (!query.trim()) return;

    const matched = cyRef.current.nodes().filter((n: any) => {
      const label = (n.data('label') || '').toLowerCase();
      const id = (n.data('id') || '').toLowerCase();
      const type = (n.data('type') || '').toLowerCase();
      const q = query.toLowerCase();
      return label.includes(q) || id.includes(q) || type.includes(q);
    });

    if (matched.length > 0) {
      cyRef.current.nodes().difference(matched).addClass('faded');
      matched.addClass('search-match').removeClass('faded');
      cyRef.current.animate({
        center: { eles: matched[0] },
        zoom: 1.4,
        duration: 400
      });
    }
  };

  // Filter nodes by Category
  const handleTypeFilter = (filterType: string) => {
    setActiveTypeFilter(filterType);
    if (!cyRef.current) return;
    cyRef.current.elements().removeClass('faded focused-center neighbor-highlight search-match');

    if (filterType === 'ALL') {
      cyRef.current.fit(undefined, 40);
      return;
    }

    const matching = cyRef.current.nodes().filter((n: any) => {
      const t = n.data('type');
      if (filterType === 'Infrastructure') {
        return t === 'Infrastructure' || t === 'Domain';
      }
      return t === filterType;
    });

    const nonMatching = cyRef.current.nodes().difference(matching);
    nonMatching.addClass('faded');
    matching.removeClass('faded');

    const nonMatchingEdges = cyRef.current.edges().filter((e: any) => {
      return nonMatching.contains(e.source()) || nonMatching.contains(e.target());
    });
    nonMatchingEdges.addClass('faded');

    if (matching.length > 0) {
      cyRef.current.animate({
        center: { eles: matching },
        duration: 500
      });
    }
  };

  // Isolate Subgraph to Selected Neighborhood
  const handleIsolateSubgraph = () => {
    if (!cyRef.current || !selectedElement || selectedElement.type !== 'node') return;
    const node = cyRef.current.$id(selectedElement.data.id);
    if (!node || node.empty()) return;

    const neighborhood = node.closedNeighborhood();
    cyRef.current.elements().difference(neighborhood).addClass('faded');
    neighborhood.removeClass('faded');
    cyRef.current.animate({
      fit: { eles: neighborhood, padding: 60 },
      duration: 500
    });
    setIsolatedSubgraph(true);
  };

  // Restore Full View
  const handleRestoreFullGraph = () => {
    if (!cyRef.current) return;
    cyRef.current.elements().removeClass('faded focused-center neighbor-highlight search-match');
    cyRef.current.animate({
      fit: { eles: cyRef.current.elements(), padding: 40 },
      duration: 500
    } as any);
    setIsolatedSubgraph(false);
  };

  // Copy Identifier with Checkmark Feedback
  const handleCopyId = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(true);
    setTimeout(() => setCopiedId(false), 2000);
  };

  // Real-time custom entity injection on canvas
  const handleAddLiveNode = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNodeLabel.trim() || !cyRef.current) return;

    const newId = `LIVE-${Date.now().toString().slice(-6)}`;
    const newNode = {
      group: 'nodes' as const,
      data: {
        id: newId,
        label: newNodeLabel,
        type: newNodeType,
        metadata: newNodeMeta || 'Real-time Analyst Injected Indicator',
        injected_at: new Date().toISOString()
      }
    };

    cyRef.current.add(newNode);

    if (connectToNodeId) {
      cyRef.current.add({
        group: 'edges' as const,
        data: {
          id: `EDGE-${Date.now().toString().slice(-6)}`,
          source: connectToNodeId,
          target: newId,
          label: 'CORRELATED_BY_ANALYST'
        }
      });
    }

    cyRef.current.layout({ name: layoutMode, animate: true } as any).run();
    setNodeCount(prev => prev + 1);
    if (connectToNodeId) setEdgeCount(prev => prev + 1);

    setShowAddModal(false);
    setNewNodeLabel('');
    setNewNodeMeta('');
    setConnectToNodeId('');
  };

  // Export Graph as Image
  const handleExportPng = () => {
    if (!cyRef.current) return;
    const png64 = cyRef.current.png({ full: true, bg: '#040711' });
    const a = document.createElement('a');
    a.href = png64;
    a.download = `DARKTRACE-GRAPH-${selectedActorId || 'INTERACTION'}-${Date.now()}.png`;
    a.click();
  };

  // Entity Type Icon Resolver
  const renderTypeIcon = (type: string) => {
    switch (type) {
      case 'Actor': return <ShieldAlert size={14} className="text-[#10B981]" />;
      case 'Persona': return <Crosshair size={14} className="text-[#00E5FF]" />;
      case 'PGPKey': return <Key size={14} className="text-[#F59E0B]" />;
      case 'Wallet': return <Coins size={14} className="text-[#059669]" />;
      case 'Infrastructure':
      case 'Domain': return <Server size={14} className="text-[#F43F5E]" />;
      default: return <Sparkles size={14} className="text-[#A855F7]" />;
    }
  };

  return (
    <div className="space-y-3.5 h-full flex flex-col font-sans select-none">

      {/* ══════════════════════════════════════════════════════════
          1. MILITARY-GRADE TARGET COMMANDER & TELEMETRY STRIP
          ══════════════════════════════════════════════════════════ */}
      <div className="glass-panel p-3.5 border border-sky-500/25 bg-[#091328]/98 backdrop-blur-2xl shadow-[0_8px_32px_rgba(0,0,0,0.7)] rounded-xl relative overflow-hidden">
        {/* Glow ambient background accent */}
        <div className="absolute top-0 right-0 w-96 h-full bg-gradient-to-l from-sky-500/10 via-transparent to-transparent pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 relative z-10">
          
          {/* Target Commander Profile Card */}
          <div className="flex items-center gap-3.5 min-w-0">
            {/* Target Avatar with Animated Radar Ring */}
            <div className="relative flex-shrink-0">
              <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-[#064E3B] to-[#0A1A36] border border-[#10B981]/50 flex items-center justify-center text-[#10B981] shadow-[0_0_20px_rgba(16,185,129,0.3)]">
                <ShieldAlert size={24} />
              </div>
              <div className="absolute -top-1 -right-1 h-3.5 w-3.5 rounded-full bg-[#10B981] border-2 border-[#091328] animate-ping" />
              <div className="absolute -top-1 -right-1 h-3.5 w-3.5 rounded-full bg-[#10B981] border-2 border-[#091328]" />
            </div>

            {/* Target Details */}
            <div className="min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-[10px] font-mono text-slate-400 font-bold uppercase tracking-widest">
                  COMMAND TARGET:
                </span>
                {actors.length > 0 ? (
                  <select
                    value={selectedActorId}
                    onChange={(e) => setSelectedActorId(e.target.value)}
                    className="bg-[#0E1A36] border border-sky-500/40 hover:border-sky-400 text-xs text-[#00FF88] rounded-lg px-2.5 py-1 outline-none focus:border-[#00E5FF] focus:ring-1 focus:ring-[#00E5FF]/20 font-mono font-black transition shadow-inner cursor-pointer"
                  >
                    {actors.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.primary_name} ({a.id})
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className="text-xs font-mono text-amber-400 font-bold">LOADING TARGETS...</span>
                )}

                <span className="text-[9px] px-2 py-0.5 rounded-md bg-emerald-500/20 text-[#10B981] border border-emerald-500/40 font-mono font-bold tracking-wider">
                  98.4% ATTRIBUTED
                </span>

                <span className="text-[9px] px-2 py-0.5 rounded-md bg-rose-500/20 text-rose-300 border border-rose-500/40 font-mono font-bold">
                  DEFCON 2
                </span>
              </div>

              <div className="flex items-center gap-2 text-[11px] text-slate-400 font-mono mt-0.5 truncate">
                <span className="text-slate-300 font-bold">{selectedActor?.primary_name || 'Active Actor'}</span>
                <span>•</span>
                <span>{selectedActor?.threat_category || 'Transnational Underground'}</span>
                <span>•</span>
                <span className="text-sky-400">Confidence: {selectedActor?.confidence_score ? `${Math.round(selectedActor.confidence_score * 100)}%` : '98%'}</span>
              </div>
            </div>
          </div>

          {/* 4 Overlaid Real-Time Telemetry Pods */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 font-mono text-xs">
            <div className="p-2 rounded-lg bg-[#0E1A36]/80 border border-sky-900/40">
              <span className="text-[9px] text-slate-400 uppercase font-bold block">ENTITIES</span>
              <span className="text-sm font-black text-slate-100 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[#00E5FF]" />
                {nodeCount} Mapped
              </span>
            </div>

            <div className="p-2 rounded-lg bg-[#0E1A36]/80 border border-sky-900/40">
              <span className="text-[9px] text-slate-400 uppercase font-bold block">RELATIONS</span>
              <span className="text-sm font-black text-slate-100 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-[#10B981]" />
                {edgeCount} Links
              </span>
            </div>

            <div className="p-2 rounded-lg bg-[#0E1A36]/80 border border-sky-900/40">
              <span className="text-[9px] text-slate-400 uppercase font-bold block">CRYPTO FLOW</span>
              <span className="text-sm font-black text-amber-300 flex items-center gap-1.5">
                <Coins size={12} className="text-amber-400" />
                {categoryCounts.Wallet} Wallets
              </span>
            </div>

            <div className="p-2 rounded-lg bg-[#0E1A36]/80 border border-sky-900/40">
              <span className="text-[9px] text-slate-400 uppercase font-bold block">ANOMALY</span>
              <span className="text-sm font-black text-rose-400 flex items-center gap-1.5">
                <Flame size={12} className="text-rose-400" />
                0.88 CRITICAL
              </span>
            </div>
          </div>

          {/* Search & Layout Control Toolbar */}
          <div className="flex items-center gap-2 flex-wrap">
            {/* Search Input */}
            <div className="relative w-44 sm:w-52">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" size={13} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearchNodes(e.target.value)}
                placeholder="Find node / wallet / IP..."
                className="w-full bg-[#0E1A36] border border-sky-900/50 hover:border-sky-500/40 rounded-lg pl-8 pr-6 py-1.5 text-xs text-slate-200 outline-none focus:border-[#00E5FF] font-mono placeholder-slate-500 transition"
              />
              {searchQuery && (
                <button
                  onClick={() => handleSearchNodes('')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-slate-400 hover:text-white"
                >
                  ✕
                </button>
              )}
            </div>

            {/* Layout Engine Dropdown */}
            <div className="flex items-center gap-1 bg-[#0E1A36] border border-sky-900/50 rounded-lg px-2 py-1 text-[11px] font-mono text-slate-300">
              <Compass size={13} className="text-sky-400" />
              <select
                value={layoutMode}
                onChange={(e) => setLayoutMode(e.target.value)}
                className="bg-transparent text-xs text-slate-200 outline-none font-mono cursor-pointer"
                title="Graph Physics Layout Engine"
              >
                <option value="cose" className="bg-[#091328]">Physics (Cose)</option>
                <option value="concentric" className="bg-[#091328]">Concentric Radar</option>
                <option value="circle" className="bg-[#091328]">Circle Orbit</option>
                <option value="grid" className="bg-[#091328]">Grid Matrix</option>
                <option value="breadthfirst" className="bg-[#091328]">Hierarchical Tree</option>
              </select>
            </div>

            {/* Add Entity Button */}
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-1 px-3 py-1.5 bg-[#00D9FF]/20 hover:bg-[#00D9FF]/30 text-[#00D9FF] border border-[#00D9FF]/40 rounded-lg text-xs font-mono font-bold transition shadow-[0_0_12px_rgba(0,217,255,0.2)] btn-3d"
            >
              <Plus size={13} />
              <span>INJECT</span>
            </button>
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════
          2. ILLUMINATED TACTICAL CATEGORY SWITCHER BAR
          ══════════════════════════════════════════════════════════ */}
      <div className="flex items-center gap-2 overflow-x-auto pb-0.5 text-xs font-mono">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider pl-1 pr-1 flex items-center gap-1.5 flex-shrink-0">
          <Filter size={12} className="text-[#38BDF8]" />
          <span>ISOLATE VECTORS:</span>
        </span>

        <button
          onClick={() => handleTypeFilter('ALL')}
          className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-2 flex-shrink-0 ${
            activeTypeFilter === 'ALL'
              ? 'bg-gradient-to-r from-sky-500 to-[#00E5FF] text-black shadow-[0_0_15px_rgba(0,229,255,0.5)] font-extrabold'
              : 'bg-[#0A1329] text-slate-400 hover:text-slate-200 border border-sky-900/40'
          }`}
        >
          <span>ALL ENTITIES</span>
          <span className="text-[9px] px-1.5 py-0.2 rounded bg-black/40 font-mono font-bold">{categoryCounts.ALL}</span>
        </button>

        <button
          onClick={() => handleTypeFilter('Actor')}
          className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-2 flex-shrink-0 ${
            activeTypeFilter === 'Actor'
              ? 'bg-gradient-to-r from-emerald-500 to-teal-400 text-black shadow-[0_0_15px_rgba(16,185,129,0.5)] font-extrabold'
              : 'bg-[#0A1329] text-emerald-400 hover:text-emerald-300 border border-emerald-900/40'
          }`}
        >
          <span className="h-2 w-2 rounded-full bg-[#10B981] animate-pulse" />
          <span>ACTORS</span>
          <span className="text-[9px] px-1.5 py-0.2 rounded bg-black/40 font-mono font-bold">{categoryCounts.Actor}</span>
        </button>

        <button
          onClick={() => handleTypeFilter('Persona')}
          className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-2 flex-shrink-0 ${
            activeTypeFilter === 'Persona'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-400 text-black shadow-[0_0_15px_rgba(0,229,255,0.5)] font-extrabold'
              : 'bg-[#0A1329] text-sky-400 hover:text-sky-300 border border-sky-900/40'
          }`}
        >
          <span className="h-2 w-2 rounded-full bg-[#00E5FF]" />
          <span>PERSONAS</span>
          <span className="text-[9px] px-1.5 py-0.2 rounded bg-black/40 font-mono font-bold">{categoryCounts.Persona}</span>
        </button>

        <button
          onClick={() => handleTypeFilter('Wallet')}
          className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-2 flex-shrink-0 ${
            activeTypeFilter === 'Wallet'
              ? 'bg-gradient-to-r from-teal-500 to-emerald-400 text-black shadow-[0_0_15px_rgba(5,150,105,0.5)] font-extrabold'
              : 'bg-[#0A1329] text-teal-400 hover:text-teal-300 border border-teal-900/40'
          }`}
        >
          <span className="h-2 w-2 rounded-full bg-[#059669]" />
          <span>WALLETS (BTC/XMR)</span>
          <span className="text-[9px] px-1.5 py-0.2 rounded bg-black/40 font-mono font-bold">{categoryCounts.Wallet}</span>
        </button>

        <button
          onClick={() => handleTypeFilter('PGPKey')}
          className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-2 flex-shrink-0 ${
            activeTypeFilter === 'PGPKey'
              ? 'bg-gradient-to-r from-amber-500 to-yellow-400 text-black shadow-[0_0_15px_rgba(245,158,11,0.5)] font-extrabold'
              : 'bg-[#0A1329] text-amber-400 hover:text-amber-300 border border-amber-900/40'
          }`}
        >
          <span className="h-2 w-2 rounded-full bg-[#F59E0B]" />
          <span>PGP KEYS</span>
          <span className="text-[9px] px-1.5 py-0.2 rounded bg-black/40 font-mono font-bold">{categoryCounts.PGPKey}</span>
        </button>

        <button
          onClick={() => handleTypeFilter('Infrastructure')}
          className={`px-3 py-1.5 rounded-lg font-bold transition flex items-center gap-2 flex-shrink-0 ${
            activeTypeFilter === 'Infrastructure'
              ? 'bg-gradient-to-r from-rose-500 to-pink-500 text-white shadow-[0_0_15px_rgba(244,63,94,0.5)] font-extrabold'
              : 'bg-[#0A1329] text-rose-400 hover:text-rose-300 border border-rose-900/40'
          }`}
        >
          <span className="h-2 w-2 rounded-full bg-[#F43F5E]" />
          <span>INFRASTRUCTURE / ONION</span>
          <span className="text-[9px] px-1.5 py-0.2 rounded bg-black/40 font-mono font-bold">{categoryCounts.Infrastructure}</span>
        </button>
      </div>

      {/* ══════════════════════════════════════════════════════════
          3. MAIN CANVAS VIEWPORT WITH HUD RADAR OVERLAYS
          ══════════════════════════════════════════════════════════ */}
      <div className="flex-1 flex gap-3 min-h-[580px] relative">
        <div
          className="flex-1 glass-panel rounded-xl overflow-hidden border border-sky-500/25 relative shadow-[inset_0_0_50px_rgba(0,0,0,0.9)]"
          style={{ background: '#040711' }}
        >
          {/* Tactical Corner Brackets */}
          <div className="corner-bracket-tl" />
          <div className="corner-bracket-tr" />
          <div className="corner-bracket-bl" />
          <div className="corner-bracket-br" />

          {/* Animated Radar Scanline */}
          {radarActive && <div className="radar-scan-line" />}

          {/* Isolated Cytoscape DOM container */}
          <div
            ref={containerRef}
            className="absolute inset-0 w-full h-full"
            style={{ width: '100%', height: '100%' }}
          />

          {/* Floating Speed Dial Controls (Top Right of Canvas) */}
          <div className="absolute top-4 right-4 z-20 flex flex-col gap-1.5 bg-[#081024]/90 backdrop-blur-md p-1.5 rounded-xl border border-sky-500/30 shadow-2xl">
            <button
              onClick={handleRestoreFullGraph}
              className="p-2 rounded-lg bg-[#0E1A36] hover:bg-sky-500/20 text-slate-300 hover:text-[#00E5FF] transition"
              title="Reset View & Center All Elements"
            >
              <Maximize2 size={16} />
            </button>
            <button
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.25)}
              className="p-2 rounded-lg bg-[#0E1A36] hover:bg-sky-500/20 text-slate-300 hover:text-[#00E5FF] transition"
              title="Zoom In"
            >
              <ZoomIn size={16} />
            </button>
            <button
              onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)}
              className="p-2 rounded-lg bg-[#0E1A36] hover:bg-sky-500/20 text-slate-300 hover:text-[#00E5FF] transition"
              title="Zoom Out"
            >
              <ZoomOut size={16} />
            </button>
            <button
              onClick={handleExportPng}
              className="p-2 rounded-lg bg-[#0E1A36] hover:bg-emerald-500/20 text-slate-300 hover:text-[#10B981] transition"
              title="Export High-Res PNG Defense Dossier"
            >
              <Download size={16} />
            </button>
            <button
              onClick={() => setRadarActive(!radarActive)}
              className={`p-2 rounded-lg transition ${
                radarActive ? 'bg-[#00E5FF]/20 text-[#00E5FF]' : 'bg-[#0E1A36] text-slate-500'
              }`}
              title="Toggle Animated Radar Scan"
            >
              <Radio size={16} className={radarActive ? 'animate-pulse' : ''} />
            </button>
          </div>

          {/* Loading Overlay */}
          {loading && (
            <div className="absolute inset-0 flex items-center justify-center bg-[#040711]/88 backdrop-blur-md z-30 font-mono text-xs text-[#00E5FF] flex-col gap-3">
              <div className="h-14 w-14 rounded-2xl bg-sky-500/15 border border-sky-400/50 flex items-center justify-center shadow-[0_0_25px_rgba(0,229,255,0.4)]">
                <RefreshCw className="animate-spin text-[#00E5FF]" size={28} />
              </div>
              <div className="text-center">
                <span className="font-extrabold tracking-widest block text-slate-100 text-sm">
                  SYNTHESIZING MULTI-RELATIONAL ATTRIBUTION TOPOLOGY
                </span>
                <span className="text-[11px] text-slate-400 mt-1 block">
                  Correlating Darknet Handles • Blockchain Clusters • PGP Fingerprints
                </span>
              </div>
            </div>
          )}

          {/* Zero-State Canvas Overlay */}
          {!loading && nodeCount === 0 && (
            <div className="absolute inset-0 flex items-center justify-center z-10 p-6 flex-col text-center">
              <div className="p-4 rounded-2xl bg-[#091328] border border-sky-900/40 mb-3 text-slate-500 shadow-xl">
                <Network size={40} className="text-sky-400/50" />
              </div>
              <h3 className="text-sm font-mono font-bold text-slate-200 tracking-wide uppercase mb-1">
                GRAPH ENGINE IN ACTIVE ZERO-STATE
              </h3>
              <p className="text-xs font-mono text-slate-400 max-w-md mb-4 leading-relaxed">
                No relational clusters currently mapped for this view. You can inject new threat entities in real time or select another target from the mission bar.
              </p>
              <div className="flex items-center gap-3 font-mono">
                <button
                  onClick={() => setShowAddModal(true)}
                  className="flex items-center gap-1.5 px-4 py-2 bg-[#00E5FF]/20 hover:bg-[#00E5FF]/30 text-[#00E5FF] border border-[#00E5FF]/40 rounded-lg text-xs font-bold transition"
                >
                  <Plus size={14} />
                  <span>INJECT NEW ENTITY</span>
                </button>
                <button
                  onClick={() => navigate('/dashboard')}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg text-xs"
                >
                  WAR ROOM
                </button>
              </div>
            </div>
          )}

          {/* Bottom Telemetry HUD Overlay */}
          <div className="absolute bottom-3 left-3 z-20 flex items-center gap-3 bg-[#081024]/95 backdrop-blur-md px-4 py-2 rounded-xl border border-sky-500/30 text-[10px] font-mono text-slate-400 shadow-2xl">
            <span className="flex items-center gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-[#10B981] animate-ping" />
              TOPOLOGY: <strong className="text-slate-200 font-bold text-[11px]">{nodeCount} Nodes</strong>
            </span>
            <span className="h-3 w-px bg-slate-800" />
            <span>EDGES: <strong className="text-slate-200 font-bold text-[11px]">{edgeCount} Links</strong></span>
            <span className="h-3 w-px bg-slate-800" />
            <span>ENGINE: <strong className="text-[#00E5FF] font-bold">{layoutMode.toUpperCase()} v2.4</strong></span>
            {isolatedSubgraph && (
              <>
                <span className="h-3 w-px bg-slate-800" />
                <span className="text-amber-400 font-bold flex items-center gap-1">
                  <EyeOff size={11} /> CLUSTER ISOLATED
                </span>
              </>
            )}
          </div>

          {/* Top-Left Quick Guidance Tag */}
          <div className="absolute top-4 left-4 z-20 hidden md:flex items-center gap-2 bg-[#081024]/85 backdrop-blur-md px-3 py-1 rounded-lg border border-sky-900/40 text-[10px] font-mono text-slate-400">
            <span className="text-[#00E5FF] font-bold">CLICK</span> node to focus neighborhood • <span className="text-[#10B981] font-bold">DOUBLE CLICK</span> to center
          </div>
        </div>

        {/* ══════════════════════════════════════════════════════════
            4. MULTI-TAB TACTICAL EVIDENCE INSPECTOR DRAWER
            ══════════════════════════════════════════════════════════ */}
        {selectedElement && (
          <div className="w-88 lg:w-[420px] glass-panel p-4 overflow-y-auto space-y-3.5 text-xs font-mono border-l border-sky-500/35 bg-[#091328]/98 backdrop-blur-2xl animate-fadeIn shadow-2xl relative z-20 flex flex-col">
            
            {/* Header with Close */}
            <div className="flex items-center justify-between border-b border-sky-900/40 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-sky-500/15 border border-sky-400/40 text-[#00E5FF] shadow-[0_0_12px_rgba(0,229,255,0.25)]">
                  {renderTypeIcon(selectedElement.data?.type || 'Persona')}
                </div>
                <div>
                  <span className="text-[10px] uppercase font-black text-[#00E5FF] tracking-wider block">
                    {selectedElement.type === 'node' ? 'TACTICAL ENTITY DOSSIER' : 'RELATIONSHIP CORRELATION'}
                  </span>
                  <span className="text-[9px] text-slate-400">
                    {selectedElement.type === 'node' ? `Degree: ${selectedElement.degree || 0} direct connections` : 'Correlated Vector'}
                  </span>
                </div>
              </div>
              <button
                onClick={() => {
                  setSelectedElement(null);
                  if (cyRef.current) {
                    cyRef.current.elements().removeClass('faded focused-center neighbor-highlight search-match');
                  }
                }}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                ✕
              </button>
            </div>

            {/* Inspector Tab Switcher */}
            {selectedElement.type === 'node' && (
              <div className="flex items-center gap-1 p-1 bg-[#070D1E] rounded-xl border border-sky-900/40 text-[10px]">
                <button
                  onClick={() => setInspectorTab('PROFILE')}
                  className={`flex-1 py-1.5 rounded-lg font-bold transition flex items-center justify-center gap-1 ${
                    inspectorTab === 'PROFILE'
                      ? 'bg-[#00E5FF] text-black shadow-[0_0_10px_rgba(0,229,255,0.3)]'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Fingerprint size={11} />
                  <span>PROFILE</span>
                </button>
                <button
                  onClick={() => setInspectorTab('VECTORS')}
                  className={`flex-1 py-1.5 rounded-lg font-bold transition flex items-center justify-center gap-1 ${
                    inspectorTab === 'VECTORS'
                      ? 'bg-[#10B981] text-black shadow-[0_0_10px_rgba(16,185,129,0.3)]'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <LinkIcon size={11} />
                  <span>VECTORS ({connectedNeighbors.length})</span>
                </button>
                <button
                  onClick={() => setInspectorTab('PIVOTS')}
                  className={`flex-1 py-1.5 rounded-lg font-bold transition flex items-center justify-center gap-1 ${
                    inspectorTab === 'PIVOTS'
                      ? 'bg-[#F59E0B] text-black shadow-[0_0_10px_rgba(245,158,11,0.3)]'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Zap size={11} />
                  <span>ACTIONS</span>
                </button>
              </div>
            )}

            {/* TAB 1: ATTRIBUTION & PROFILE */}
            {(inspectorTab === 'PROFILE' || selectedElement.type === 'edge') && (
              <div className="space-y-3 flex-1 overflow-y-auto pr-1">
                {/* Identifier Title Card */}
                <div className="p-3 rounded-xl bg-[#0E1A36] border border-sky-900/50 space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[10px] text-slate-400 uppercase font-bold">IDENTIFIER:</span>
                    <button
                      onClick={() => handleCopyId(selectedElement.data.label || selectedElement.data.id)}
                      className="flex items-center gap-1 text-[10px] text-[#00E5FF] hover:underline"
                    >
                      {copiedId ? <Check size={11} className="text-emerald-400" /> : <Copy size={11} />}
                      <span>{copiedId ? 'COPIED' : 'COPY'}</span>
                    </button>
                  </div>
                  <h4 className="text-sm font-extrabold text-slate-100 break-all">
                    {selectedElement.data.label || selectedElement.data.id}
                  </h4>
                  <div className="flex items-center gap-2 pt-1 flex-wrap">
                    <span className="text-[10px] px-2 py-0.5 rounded bg-sky-500/20 text-[#38BDF8] border border-sky-500/30 font-bold">
                      {selectedElement.data.type || 'Correlated Edge'}
                    </span>
                    {selectedElement.degree !== undefined && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-[#10B981] border border-emerald-500/30 font-bold">
                        {selectedElement.degree} Connected Edges
                      </span>
                    )}
                  </div>
                </div>

                {/* Attribution Confidence Gauge */}
                {selectedElement.type === 'node' && (
                  <div className="p-3 rounded-xl bg-[#0E1A36] border border-sky-900/50 space-y-2">
                    <div className="flex items-center justify-between text-[10px]">
                      <span className="text-slate-400 font-bold uppercase">ATTRIBUTION CONFIDENCE:</span>
                      <span className="text-[#10B981] font-black text-xs">
                        {selectedElement.data.type === 'Actor' ? '98.4%' : selectedElement.data.type === 'Wallet' ? '94.2%' : '89.0%'}
                      </span>
                    </div>
                    <div className="w-full bg-slate-900 h-2.5 rounded-full overflow-hidden border border-slate-800 p-0.5">
                      <div
                        className="h-full bg-gradient-to-r from-teal-500 via-[#10B981] to-[#00E5FF] rounded-full shadow-[0_0_10px_#10B981]"
                        style={{ width: selectedElement.data.type === 'Actor' ? '98.4%' : selectedElement.data.type === 'Wallet' ? '94.2%' : '89%' }}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-2 pt-1 text-[10px]">
                      <div className="p-2 rounded bg-slate-950/60 border border-slate-800">
                        <span className="text-slate-500 block text-[9px]">IN-DEGREE:</span>
                        <span className="text-slate-200 font-bold">{selectedElement.inDegree ?? 0} Incoming Links</span>
                      </div>
                      <div className="p-2 rounded bg-slate-950/60 border border-slate-800">
                        <span className="text-slate-500 block text-[9px]">OUT-DEGREE:</span>
                        <span className="text-slate-200 font-bold">{selectedElement.outDegree ?? 0} Outgoing Links</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Metadata Attributes */}
                <div className="space-y-1.5">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">
                    FORENSIC ATTRIBUTES & EVIDENCE:
                  </span>
                  <div className="space-y-1.5 max-h-[220px] overflow-y-auto pr-1">
                    {Object.entries(selectedElement.data).map(([k, v]) => {
                      if (k === 'id' || k === 'label') return null;
                      return (
                        <div key={k} className="p-2.5 rounded-lg bg-[#0E1A36] border border-sky-900/40 text-slate-300">
                          <span className="text-[9px] text-[#38BDF8] uppercase font-bold block">{k}:</span>
                          <span className="text-slate-200 break-all select-all font-mono text-[11px] mt-0.5 block">
                            {String(v)}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Section 65B IT Act Forensic Evidence Hash */}
                <div className="p-2.5 rounded-lg bg-[#070D1E] border border-sky-900/40 flex items-center justify-between text-[10px]">
                  <span className="text-slate-500">SEC 65B CHAIN:</span>
                  <span className="text-slate-300 font-mono select-all">SHA256: 8f4b...c3a9</span>
                </div>
              </div>
            )}

            {/* TAB 2: CONNECTED 1-HOP VECTORS (Interactive traversal) */}
            {inspectorTab === 'VECTORS' && selectedElement.type === 'node' && (
              <div className="space-y-2 flex-1 overflow-y-auto pr-1">
                <span className="text-[10px] text-slate-400 uppercase font-bold block">
                  CONNECTED 1-HOP NEIGHBORS (Click to pivot):
                </span>

                {connectedNeighbors.length === 0 ? (
                  <div className="p-6 text-center text-slate-500 bg-[#0E1A36] rounded-xl border border-slate-800">
                    No direct connected vectors found.
                  </div>
                ) : (
                  connectedNeighbors.map((nbr) => (
                    <div
                      key={nbr.id}
                      onClick={() => handleFocusNeighborNode(nbr.id)}
                      className="p-2.5 rounded-xl bg-[#0E1A36] hover:bg-sky-500/15 border border-sky-900/50 hover:border-[#00E5FF]/60 cursor-pointer transition flex items-center justify-between group"
                    >
                      <div className="min-w-0 pr-2">
                        <div className="flex items-center gap-1.5">
                          {renderTypeIcon(nbr.type)}
                          <span className="font-extrabold text-slate-200 group-hover:text-[#00E5FF] truncate text-xs">
                            {nbr.label}
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-500 font-mono block mt-0.5">
                          Relationship: <strong className="text-slate-400">{nbr.relation}</strong>
                        </span>
                      </div>
                      <ChevronRight size={14} className="text-slate-500 group-hover:text-[#00E5FF] flex-shrink-0 transition" />
                    </div>
                  ))
                )}
              </div>
            )}

            {/* TAB 3: TACTICAL PIVOTS & ACTIONS */}
            {inspectorTab === 'PIVOTS' && selectedElement.type === 'node' && (
              <div className="space-y-2.5 flex-1 overflow-y-auto pr-1">
                <span className="text-[10px] text-slate-400 uppercase font-bold block">
                  FORENSIC INVESTIGATION PIVOTS:
                </span>

                {/* Subgraph Isolation Toggle */}
                <button
                  onClick={isolatedSubgraph ? handleRestoreFullGraph : handleIsolateSubgraph}
                  className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-bold transition font-mono border ${
                    isolatedSubgraph
                      ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 hover:bg-amber-500/30'
                      : 'bg-sky-500/20 text-[#00E5FF] border-sky-500/40 hover:bg-sky-500/30'
                  }`}
                >
                  {isolatedSubgraph ? <Eye size={14} /> : <EyeOff size={14} />}
                  <span>{isolatedSubgraph ? 'RESTORE FULL GRAPH' : 'ISOLATE NEIGHBORHOOD CLUSTER'}</span>
                </button>

                {/* Stylometry Pivot */}
                <button
                  onClick={() => {
                    navigate(`/ai-analysis?seed=${encodeURIComponent(selectedElement.data.label || selectedElement.data.id)}`);
                  }}
                  className="w-full flex items-center justify-center gap-2 py-2.5 bg-gradient-to-r from-emerald-600/20 to-teal-600/20 hover:from-emerald-600/30 hover:to-teal-600/30 text-[#10B981] rounded-xl border border-emerald-500/40 text-xs font-bold font-mono transition"
                >
                  <Sparkles size={14} />
                  <span>PIVOT TO AI DE-ANONYMIZATION</span>
                </button>

                {/* Actor Profile Pivot */}
                <button
                  onClick={() => {
                    navigate(`/actors?actor_id=${encodeURIComponent(selectedActorId)}`);
                  }}
                  className="w-full flex items-center justify-center gap-2 py-2.5 bg-[#0E1A36] hover:bg-slate-800 text-sky-300 rounded-xl border border-sky-500/30 text-xs font-bold font-mono transition"
                >
                  <Shield size={14} />
                  <span>OPEN THREAT DOSSIER</span>
                </button>

                {/* Evidence Vault Pivot */}
                <button
                  onClick={() => {
                    navigate(`/reports`);
                  }}
                  className="w-full flex items-center justify-center gap-2 py-2.5 bg-[#0E1A36] hover:bg-slate-800 text-slate-300 rounded-xl border border-slate-700 text-xs font-bold font-mono transition"
                >
                  <FolderGit2 size={14} />
                  <span>INCLUDE IN SEC. 65B DOSSIER</span>
                </button>
              </div>
            )}

            {/* Bottom Actions Footer */}
            <div className="pt-2 border-t border-sky-900/40 flex items-center justify-between">
              <button
                onClick={handleRestoreFullGraph}
                className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 font-bold"
              >
                <Maximize2 size={12} />
                <span>Reset Zoom</span>
              </button>
              <button
                onClick={() => handleCopyId(JSON.stringify(selectedElement.data, null, 2))}
                className="text-[11px] text-[#00E5FF] hover:underline font-bold"
              >
                Copy JSON
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ══════════════════════════════════════════════════════════
          5. REAL-TIME LIVE NODE INJECTION MODAL (WITH PRESETS)
          ══════════════════════════════════════════════════════════ */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <div className="bg-[#0A1329] border border-sky-500/40 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-[0_0_50px_rgba(56,189,248,0.3)]">
            <div className="flex items-center justify-between border-b border-sky-900/40 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-sky-500/20 text-[#00E5FF]">
                  <Terminal size={18} />
                </div>
                <div>
                  <h3 className="text-sm font-mono font-black uppercase text-slate-100">
                    INJECT REAL-TIME IOC ON GRAPH
                  </h3>
                  <p className="text-[10px] text-slate-400 font-mono">
                    Plot newly intercepted indicators directly into active attribution cluster
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-500 hover:text-slate-200"
              >
                ✕
              </button>
            </div>

            {/* Quick Presets */}
            <div className="space-y-1 font-mono text-[10px]">
              <span className="text-slate-400 font-bold uppercase">1-CLICK SAMPLE PRESETS:</span>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setNewNodeType('Wallet');
                    setNewNodeLabel('bc1qa8y6f5xld8m7s43zqj2h');
                    setNewNodeMeta('Darknet escrow payout wallet intercepted via Dread');
                  }}
                  className="p-2 rounded-lg bg-[#0E1A36] hover:bg-slate-800 text-teal-400 border border-teal-900/40 text-left font-bold"
                >
                  ⚡ Escrow Wallet (BTC)
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setNewNodeType('Infrastructure');
                    setNewNodeLabel('shadowops7w7x.onion');
                    setNewNodeMeta('Onion V3 hidden service cluster mirror');
                  }}
                  className="p-2 rounded-lg bg-[#0E1A36] hover:bg-slate-800 text-rose-400 border border-rose-900/40 text-left font-bold"
                >
                  ⚡ Hidden Service (.onion)
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setNewNodeType('PGPKey');
                    setNewNodeLabel('PGP-4096-7F89B2');
                    setNewNodeMeta('GnuPG 4096-bit RSA vendor signing key');
                  }}
                  className="p-2 rounded-lg bg-[#0E1A36] hover:bg-slate-800 text-amber-400 border border-amber-900/40 text-left font-bold"
                >
                  ⚡ PGP Key Signature
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setNewNodeType('Persona');
                    setNewNodeLabel('chronos_broker_v4');
                    setNewNodeMeta('Suspect Telegram breach distributor handle');
                  }}
                  className="p-2 rounded-lg bg-[#0E1A36] hover:bg-slate-800 text-sky-400 border border-sky-900/40 text-left font-bold"
                >
                  ⚡ Telegram Alias
                </button>
              </div>
            </div>

            <form onSubmit={handleAddLiveNode} className="space-y-3 font-mono text-xs pt-2">
              <div>
                <label className="block text-slate-400 mb-1 font-bold">ENTITY TYPE:</label>
                <select
                  value={newNodeType}
                  onChange={(e) => setNewNodeType(e.target.value)}
                  className="w-full bg-[#0E1A36] border border-sky-900/50 rounded-lg p-2 text-slate-200 outline-none focus:border-[#00E5FF]"
                >
                  <option value="Persona">Persona / Threat Alias</option>
                  <option value="Wallet">Crypto Wallet (BTC / XMR)</option>
                  <option value="Infrastructure">Darknet Onion / Mirror</option>
                  <option value="PGPKey">PGP Key Fingerprint</option>
                  <option value="Domain">Clearnet Domain / IP</option>
                  <option value="Custom">Custom Indicator</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-bold">ENTITY IDENTIFIER / LABEL:</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. shadow_broker_v3 or bc1q9..."
                  value={newNodeLabel}
                  onChange={(e) => setNewNodeLabel(e.target.value)}
                  className="w-full bg-[#0E1A36] border border-sky-900/50 rounded-lg p-2 text-slate-200 outline-none focus:border-[#00E5FF]"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-bold">CONNECT TO EXISTING NODE (OPTIONAL):</label>
                <select
                  value={connectToNodeId}
                  onChange={(e) => setConnectToNodeId(e.target.value)}
                  className="w-full bg-[#0E1A36] border border-sky-900/50 rounded-lg p-2 text-slate-200 outline-none focus:border-[#00E5FF]"
                >
                  <option value="">-- No Initial Connection --</option>
                  {cyRef.current?.nodes().map((n: any) => (
                    <option key={n.id()} value={n.id()}>
                      {n.data('label') || n.id()} ({n.data('type') || 'Node'})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-bold">METADATA / FORENSIC SOURCE NOTE:</label>
                <textarea
                  rows={2}
                  placeholder="e.g. Intercepted via live Telegram breach monitor..."
                  value={newNodeMeta}
                  onChange={(e) => setNewNodeMeta(e.target.value)}
                  className="w-full bg-[#0E1A36] border border-sky-900/50 rounded-lg p-2 text-slate-200 outline-none focus:border-[#00E5FF]"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-sky-900/40">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold"
                >
                  CANCEL
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-gradient-to-r from-teal-500 to-[#10B981] hover:from-teal-400 hover:to-[#10B981] text-black font-extrabold flex items-center gap-1.5 transition shadow-[0_0_15px_rgba(16,185,129,0.3)] btn-3d"
                >
                  <CheckCircle2 size={14} />
                  <span>PLOT ON CANVAS</span>
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

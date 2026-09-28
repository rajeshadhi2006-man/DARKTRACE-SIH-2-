// Interactive Network Graph Controller
let networkInstance = null;
let graphData = { nodes: [], edges: [] };

document.addEventListener('DOMContentLoaded', () => {
  const actorSelect = document.getElementById('graph-focus-actor');
  const fitBtn = document.getElementById('btn-fit-graph');

  if (actorSelect) {
    actorSelect.addEventListener('change', (e) => {
      fetchAndRenderGraph(e.target.value);
    });
  }

  if (fitBtn) {
    fitBtn.addEventListener('click', () => {
      if (networkInstance) {
        networkInstance.fit({ animation: { duration: 600, easingFunction: 'easeInOutQuad' } });
      }
    });
  }
});

window.refreshNetworkGraph = function() {
  const actorSelect = document.getElementById('graph-focus-actor');
  const actorId = actorSelect ? actorSelect.value : null;
  fetchAndRenderGraph(actorId);
};

async function fetchAndRenderGraph(actorFilter = '') {
  const container = document.getElementById('network-graph-container');
  if (!container) return;

  try {
    const url = actorFilter ? `/api/graph?actor_id=${encodeURIComponent(actorFilter)}` : '/api/graph';
    const res = await fetch(url);
    const data = await res.json();
    graphData = data;

    // Convert data to vis datasets
    const nodes = new vis.DataSet(data.nodes);
    const edges = new vis.DataSet(data.edges);

    const options = {
      nodes: {
        borderWidth: 2,
        shadow: {
          enabled: true,
          color: 'rgba(0,0,0,0.5)',
          size: 10,
          x: 4,
          y: 4
        },
        font: {
          color: '#f8fafc',
          face: 'Inter, sans-serif',
          size: 12
        }
      },
      edges: {
        width: 1.5,
        smooth: {
          type: 'continuous',
          forceDirection: 'none',
          roundness: 0.3
        },
        arrows: {
          to: { enabled: true, scaleFactor: 0.6 }
        }
      },
      physics: {
        solver: 'forceAtlas2Based',
        forceAtlas2Based: {
          gravitationalConstant: -70,
          centralGravity: 0.015,
          springLength: 90,
          springConstant: 0.08,
          damping: 0.75
        },
        maxVelocity: 50,
        minVelocity: 0.1,
        stabilization: {
          iterations: 150
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 100,
        zoomView: true,
        dragView: true
      }
    };

    if (networkInstance) {
      networkInstance.destroy();
    }

    networkInstance = new vis.Network(container, { nodes, edges }, options);

    // Double click or click event
    networkInstance.on('selectNode', (params) => {
      const selectedId = params.nodes[0];
      const clickedNode = data.nodes.find(n => n.id === selectedId);
      
      if (clickedNode && clickedNode.type === 'actor' && window.viewActorModal) {
        window.viewActorModal(selectedId);
      }
    });

  } catch (err) {
    console.error('Failed to load relationship graph:', err);
  }
}

/**
 * Visual Workflow Designer
 * Drag-and-drop workflow builder with JSON generation
 *
 * Copyright © 2025-2030, All Rights Reserved
 * Ashutosh Sinha | Email: ajsinha@gmail.com
 */

class WorkflowDesigner {
    constructor() {
        this.nodes = new Map();
        this.connections = [];
        this.selectedNode = null;
        this.selectedConnection = null;
        this.nodeCounter = 0;
        this.connectionMode = false;
        this.connectionStart = null;
        this.tempLine = null;
        this.zoomLevel = 1.0;  // Default zoom 100%

        this.canvas = document.getElementById('workflowCanvas');
        this.svgCanvas = document.getElementById('connectionCanvas');
        this.canvasContainer = document.getElementById('canvasContainer');

        this.initializeSVG();
        this.setupEventListeners();
    }

    initializeSVG() {
        // Create arrow marker for connections
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('markerWidth', '10');
        marker.setAttribute('markerHeight', '10');
        marker.setAttribute('refX', '9');
        marker.setAttribute('refY', '3');
        marker.setAttribute('orient', 'auto');

        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 10 3, 0 6');
        polygon.setAttribute('fill', '#6c757d');

        marker.appendChild(polygon);
        defs.appendChild(marker);
        this.svgCanvas.appendChild(defs);

        // Set SVG size
        this.updateSVGSize();
    }

    updateSVGSize() {
        // Set fixed SVG dimensions to match workflow canvas
        this.svgCanvas.setAttribute('width', '3000');
        this.svgCanvas.setAttribute('height', '2500');
    }

    setupEventListeners() {
        // Drag and drop from palette
        document.querySelectorAll('.node-template').forEach(template => {
            template.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('nodeType', e.target.dataset.nodeType);
            });
        });

        this.canvas.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        this.canvas.addEventListener('drop', (e) => {
            e.preventDefault();
            const nodeType = e.dataTransfer.getData('nodeType');
            if (nodeType) {
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left + this.canvas.parentElement.scrollLeft;
                const y = e.clientY - rect.top + this.canvas.parentElement.scrollTop;
                this.addNode(nodeType, x, y);
            }
        });

        // Canvas click to deselect
        this.canvas.addEventListener('click', (e) => {
            if (e.target === this.canvas) {
                this.deselectAll();
            }
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.updateSVGSize();
            this.redrawConnections();
        });
    }

    addNode(type, x, y) {
        const nodeId = `node_${++this.nodeCounter}`;

        const nodeConfig = this.getNodeConfig(type);
        const node = {
            id: nodeId,
            type: type,
            x: x,
            y: y,
            config: nodeConfig
        };

        this.nodes.set(nodeId, node);
        this.renderNode(node);

        return nodeId;
    }

    getNodeConfig(type) {
        const configs = {
            start: {},
            end: {},
            llm: {
                model: 'gpt-4',
                prompt_template: '',
                temperature: 0.7
            },
            tool: {
                tool_name: '',
                parameters: {}
            },
            human: {
                assigned_to: 'admin',
                task_type: 'approval',
                instructions: '',
                timeout: 3600
            },
            conditional: {
                condition: '',
                true_target: '',
                false_target: ''
            },
            parallel: {
                branches: []
            }
        };

        return configs[type] || {};
    }

    renderNode(node) {
        const nodeEl = document.createElement('div');
        nodeEl.className = `workflow-node ${node.type}`;
        nodeEl.id = node.id;
        nodeEl.style.left = `${node.x}px`;
        nodeEl.style.top = `${node.y}px`;

        const icon = this.getNodeIcon(node.type);
        const title = node.config.node_id || `${node.type}_${node.id.split('_')[1]}`;

        nodeEl.innerHTML = `
            <div class="node-header">
                <div class="node-title">
                    ${icon} ${title}
                </div>
                <span class="node-type-badge">${node.type}</span>
            </div>
            <div class="node-actions">
                <button class="btn btn-sm btn-outline-danger" onclick="designer.deleteNode('${node.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            ${node.type !== 'start' ? '<div class="node-port input"></div>' : ''}
            ${node.type !== 'end' ? '<div class="node-port output"></div>' : ''}
        `;

        // Make draggable
        this.makeDraggable(nodeEl, node);

        // Click to select
        nodeEl.addEventListener('click', (e) => {
            e.stopPropagation();
            this.selectNode(node.id);
        });

        // Connection ports
        const outputPort = nodeEl.querySelector('.node-port.output');
        if (outputPort) {
            outputPort.addEventListener('mousedown', (e) => {
                e.stopPropagation();
                this.startConnection(node.id);
            });
        }

        const inputPort = nodeEl.querySelector('.node-port.input');
        if (inputPort) {
            inputPort.addEventListener('mouseup', (e) => {
                e.stopPropagation();
                this.endConnection(node.id);
            });
        }

        this.canvas.appendChild(nodeEl);
    }

    getNodeIcon(type) {
        const icons = {
            start: '<i class="fas fa-play-circle text-success"></i>',
            end: '<i class="fas fa-stop-circle text-danger"></i>',
            llm: '<i class="fas fa-brain text-primary"></i>',
            tool: '<i class="fas fa-wrench text-warning"></i>',
            human: '<i class="fas fa-user text-purple"></i>',
            conditional: '<i class="fas fa-code-branch text-warning"></i>',
            parallel: '<i class="fas fa-layer-group text-info"></i>'
        };
        return icons[type] || '<i class="fas fa-circle"></i>';
    }

    makeDraggable(element, node) {
        let isDragging = false;
        let startX, startY, startNodeX, startNodeY;

        element.addEventListener('mousedown', (e) => {
            if (e.target.closest('.node-port') || e.target.closest('button')) return;

            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startNodeX = node.x;
            startNodeY = node.y;

            element.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;

            const dx = e.clientX - startX;
            const dy = e.clientY - startY;

            node.x = startNodeX + dx;
            node.y = startNodeY + dy;

            element.style.left = `${node.x}px`;
            element.style.top = `${node.y}px`;

            this.redrawConnections();
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                element.style.cursor = 'move';
            }
        });
    }

    selectNode(nodeId) {
        this.deselectAll();

        const nodeEl = document.getElementById(nodeId);
        if (nodeEl) {
            nodeEl.classList.add('selected');
            this.selectedNode = nodeId;
            this.showNodeProperties(nodeId);
        }
    }

    deselectAll() {
        document.querySelectorAll('.workflow-node.selected').forEach(el => {
            el.classList.remove('selected');
        });
        document.querySelectorAll('.connection-line.selected').forEach(el => {
            el.classList.remove('selected');
        });
        this.selectedNode = null;
        this.selectedConnection = null;
        this.showEmptyProperties();
    }

    deleteNode(nodeId) {
        // Remove connections
        this.connections = this.connections.filter(conn =>
            conn.source !== nodeId && conn.target !== nodeId
        );

        // Remove node
        const nodeEl = document.getElementById(nodeId);
        if (nodeEl) nodeEl.remove();

        this.nodes.delete(nodeId);
        this.redrawConnections();
        this.deselectAll();
    }

    startConnection(nodeId) {
        this.connectionMode = true;
        this.connectionStart = nodeId;

        document.addEventListener('mousemove', this.drawTempConnection.bind(this));
        document.addEventListener('mouseup', this.cancelConnection.bind(this));
    }

    drawTempConnection(e) {
        if (!this.connectionMode) return;

        const startNode = this.nodes.get(this.connectionStart);
        const startEl = document.getElementById(this.connectionStart);
        const outputPort = startEl.querySelector('.node-port.output');

        if (!outputPort) return;

        const rect = outputPort.getBoundingClientRect();
        const canvasRect = this.svgCanvas.getBoundingClientRect();

        const x1 = rect.left - canvasRect.left + rect.width / 2;
        const y1 = rect.top - canvasRect.top + rect.height / 2;
        const x2 = e.clientX - canvasRect.left;
        const y2 = e.clientY - canvasRect.top;

        if (this.tempLine) {
            this.tempLine.remove();
        }

        this.tempLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        this.tempLine.setAttribute('class', 'temp-connection');
        this.tempLine.setAttribute('d', this.createCurvedPath(x1, y1, x2, y2));
        this.svgCanvas.appendChild(this.tempLine);
    }

    endConnection(targetId) {
        if (!this.connectionMode) return;

        this.connectionMode = false;
        document.removeEventListener('mousemove', this.drawTempConnection.bind(this));
        document.removeEventListener('mouseup', this.cancelConnection.bind(this));

        if (this.tempLine) {
            this.tempLine.remove();
            this.tempLine = null;
        }

        if (this.connectionStart && targetId && this.connectionStart !== targetId) {
            // Check if connection already exists
            const exists = this.connections.some(c =>
                c.source === this.connectionStart && c.target === targetId
            );

            if (!exists) {
                this.connections.push({
                    source: this.connectionStart,
                    target: targetId
                });
                this.redrawConnections();
            }
        }

        this.connectionStart = null;
    }

    cancelConnection() {
        this.connectionMode = false;
        this.connectionStart = null;
        if (this.tempLine) {
            this.tempLine.remove();
            this.tempLine = null;
        }
        document.removeEventListener('mousemove', this.drawTempConnection.bind(this));
        document.removeEventListener('mouseup', this.cancelConnection.bind(this));
    }

    redrawConnections() {
        // Clear existing connections
        const existingLines = this.svgCanvas.querySelectorAll('.connection-line');
        existingLines.forEach(line => line.remove());

        // Draw all connections
        this.connections.forEach((conn, index) => {
            const sourceNode = this.nodes.get(conn.source);
            const targetNode = this.nodes.get(conn.target);

            if (!sourceNode || !targetNode) return;

            const sourceEl = document.getElementById(conn.source);
            const targetEl = document.getElementById(conn.target);

            if (!sourceEl || !targetEl) return;

            const outputPort = sourceEl.querySelector('.node-port.output');
            const inputPort = targetEl.querySelector('.node-port.input');

            if (!outputPort || !inputPort) return;

            const canvasRect = this.svgCanvas.getBoundingClientRect();
            const outRect = outputPort.getBoundingClientRect();
            const inRect = inputPort.getBoundingClientRect();

            const x1 = outRect.left - canvasRect.left + outRect.width / 2;
            const y1 = outRect.top - canvasRect.top + outRect.height / 2;
            const x2 = inRect.left - canvasRect.left + inRect.width / 2;
            const y2 = inRect.top - canvasRect.top + inRect.height / 2;

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('class', 'connection-line');
            path.setAttribute('d', this.createCurvedPath(x1, y1, x2, y2));
            path.setAttribute('data-connection-index', index);

            path.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectConnection(index);
            });

            this.svgCanvas.appendChild(path);
        });
    }

    createCurvedPath(x1, y1, x2, y2) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const cx = x1 + dx / 2;

        return `M ${x1} ${y1} C ${cx} ${y1}, ${cx} ${y2}, ${x2} ${y2}`;
    }

    selectConnection(index) {
        this.deselectAll();
        const line = this.svgCanvas.querySelector(`[data-connection-index="${index}"]`);
        if (line) {
            line.classList.add('selected');
            this.selectedConnection = index;
            this.showConnectionProperties(index);
        }
    }

    showNodeProperties(nodeId) {
        const node = this.nodes.get(nodeId);
        if (!node) return;

        const panel = document.getElementById('propertiesContent');
        let html = `
            <h6 class="mb-3">${this.getNodeIcon(node.type)} ${node.type.toUpperCase()} Node</h6>

            <div class="mb-3">
                <label class="form-label">Node ID</label>
                <input type="text" class="form-control" id="prop_node_id"
                       value="${node.config.node_id || ''}"
                       placeholder="${node.type}_${node.id.split('_')[1]}">
            </div>
        `;

        // Type-specific properties
        if (node.type === 'llm') {
            html += `
                <div class="mb-3">
                    <label class="form-label">Model</label>
                    <select class="form-select" id="prop_model">
                        <option value="gpt-4" ${node.config.model === 'gpt-4' ? 'selected' : ''}>GPT-4</option>
                        <option value="gpt-3.5-turbo" ${node.config.model === 'gpt-3.5-turbo' ? 'selected' : ''}>GPT-3.5 Turbo</option>
                        <option value="claude-3" ${node.config.model === 'claude-3' ? 'selected' : ''}>Claude 3</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Prompt Template</label>
                    <textarea class="form-control" id="prop_prompt_template" rows="3">${node.config.prompt_template || ''}</textarea>
                </div>
                <div class="mb-3">
                    <label class="form-label">Temperature</label>
                    <input type="number" class="form-control" id="prop_temperature"
                           value="${node.config.temperature || 0.7}" step="0.1" min="0" max="2">
                </div>
            `;
        } else if (node.type === 'tool') {
            html += `
                <div class="mb-3">
                    <label class="form-label">Tool Name</label>
                    <select class="form-select" id="prop_tool_name">
                        <option value="">Select a tool...</option>
                        <option value="text_analysis" ${node.config.tool_name === 'text_analysis' ? 'selected' : ''}>Text Analysis</option>
                        <option value="data_transform" ${node.config.tool_name === 'data_transform' ? 'selected' : ''}>Data Transform</option>
                        <option value="math_calculator" ${node.config.tool_name === 'math_calculator' ? 'selected' : ''}>Math Calculator</option>
                        <option value="data_validator" ${node.config.tool_name === 'data_validator' ? 'selected' : ''}>Data Validator</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Parameters (JSON)</label>
                    <textarea class="form-control" id="prop_parameters" rows="3">${JSON.stringify(node.config.parameters || {}, null, 2)}</textarea>
                </div>
            `;
        } else if (node.type === 'human') {
            html += `
                <div class="mb-3">
                    <label class="form-label">Assigned To</label>
                    <input type="text" class="form-control" id="prop_assigned_to"
                           value="${node.config.assigned_to || 'admin'}">
                </div>
                <div class="mb-3">
                    <label class="form-label">Task Type</label>
                    <select class="form-select" id="prop_task_type">
                        <option value="approval" ${node.config.task_type === 'approval' ? 'selected' : ''}>Approval</option>
                        <option value="review" ${node.config.task_type === 'review' ? 'selected' : ''}>Review</option>
                        <option value="input" ${node.config.task_type === 'input' ? 'selected' : ''}>Input</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label">Instructions</label>
                    <textarea class="form-control" id="prop_instructions" rows="3">${node.config.instructions || ''}</textarea>
                </div>
                <div class="mb-3">
                    <label class="form-label">Timeout (seconds)</label>
                    <input type="number" class="form-control" id="prop_timeout"
                           value="${node.config.timeout || 3600}">
                </div>
            `;
        } else if (node.type === 'conditional') {
            html += `
                <div class="mb-3">
                    <label class="form-label">Condition</label>
                    <textarea class="form-control" id="prop_condition" rows="2">${node.config.condition || ''}</textarea>
                </div>
            `;
        }

        html += `
            <button class="btn btn-primary w-100 mt-3" onclick="designer.saveNodeProperties('${nodeId}')">
                <i class="fas fa-save"></i> Save Properties
            </button>
        `;

        panel.innerHTML = html;
    }

    showConnectionProperties(index) {
        const conn = this.connections[index];
        const sourceNode = this.nodes.get(conn.source);
        const targetNode = this.nodes.get(conn.target);

        const panel = document.getElementById('propertiesContent');
        panel.innerHTML = `
            <h6 class="mb-3"><i class="fas fa-arrow-right"></i> Connection</h6>

            <div class="mb-3">
                <label class="form-label">From</label>
                <input type="text" class="form-control" value="${sourceNode.config.node_id || sourceNode.id}" disabled>
            </div>

            <div class="mb-3">
                <label class="form-label">To</label>
                <input type="text" class="form-control" value="${targetNode.config.node_id || targetNode.id}" disabled>
            </div>

            <button class="btn btn-danger w-100 mt-3" onclick="designer.deleteConnection(${index})">
                <i class="fas fa-trash"></i> Delete Connection
            </button>
        `;
    }

    showEmptyProperties() {
        const panel = document.getElementById('propertiesContent');
        panel.innerHTML = `
            <div class="text-muted text-center py-5">
                <i class="fas fa-mouse-pointer fa-3x mb-3"></i>
                <p>Select a node or connection to edit properties</p>
            </div>
        `;
    }

    saveNodeProperties(nodeId) {
        const node = this.nodes.get(nodeId);
        if (!node) return;

        // Save common properties
        const nodeIdInput = document.getElementById('prop_node_id');
        if (nodeIdInput) {
            node.config.node_id = nodeIdInput.value || `${node.type}_${node.id.split('_')[1]}`;
        }

        // Save type-specific properties
        if (node.type === 'llm') {
            node.config.model = document.getElementById('prop_model').value;
            node.config.prompt_template = document.getElementById('prop_prompt_template').value;
            node.config.temperature = parseFloat(document.getElementById('prop_temperature').value);
        } else if (node.type === 'tool') {
            node.config.tool_name = document.getElementById('prop_tool_name').value;
            try {
                node.config.parameters = JSON.parse(document.getElementById('prop_parameters').value);
            } catch (e) {
                alert('Invalid JSON in parameters');
                return;
            }
        } else if (node.type === 'human') {
            node.config.assigned_to = document.getElementById('prop_assigned_to').value;
            node.config.task_type = document.getElementById('prop_task_type').value;
            node.config.instructions = document.getElementById('prop_instructions').value;
            node.config.timeout = parseInt(document.getElementById('prop_timeout').value);
        } else if (node.type === 'conditional') {
            node.config.condition = document.getElementById('prop_condition').value;
        }

        // Update node display
        const nodeEl = document.getElementById(nodeId);
        const titleEl = nodeEl.querySelector('.node-title');
        if (titleEl) {
            titleEl.innerHTML = `${this.getNodeIcon(node.type)} ${node.config.node_id}`;
        }

        this.showToast('Properties saved successfully', 'success');
    }

    deleteConnection(index) {
        this.connections.splice(index, 1);
        this.redrawConnections();
        this.deselectAll();
    }

    generateJSON() {
        const nodes = [];
        const edges = [];

        // Convert nodes
        this.nodes.forEach((node, id) => {
            const nodeData = {
                node_id: node.config.node_id || `${node.type}_${node.id.split('_')[1]}`,
                node_type: node.type
            };

            if (Object.keys(node.config).length > 1 || (Object.keys(node.config).length === 1 && !node.config.node_id)) {
                const config = {...node.config};
                delete config.node_id;
                if (Object.keys(config).length > 0) {
                    nodeData.config = config;
                }
            }

            nodes.push(nodeData);
        });

        // Convert connections
        this.connections.forEach(conn => {
            const sourceNode = this.nodes.get(conn.source);
            const targetNode = this.nodes.get(conn.target);

            edges.push({
                source: sourceNode.config.node_id || `${sourceNode.type}_${sourceNode.id.split('_')[1]}`,
                target: targetNode.config.node_id || `${targetNode.type}_${targetNode.id.split('_')[1]}`
            });
        });

        return {
            nodes: nodes,
            edges: edges
        };
    }

    validate() {
        const errors = [];
        const warnings = [];

        // Check for start node
        const startNodes = Array.from(this.nodes.values()).filter(n => n.type === 'start');
        if (startNodes.length === 0) {
            errors.push('Workflow must have a Start node');
        } else if (startNodes.length > 1) {
            errors.push('Workflow can only have one Start node');
        }

        // Check for end node
        const endNodes = Array.from(this.nodes.values()).filter(n => n.type === 'end');
        if (endNodes.length === 0) {
            errors.push('Workflow must have an End node');
        }

        // Check for disconnected nodes
        this.nodes.forEach((node, id) => {
            if (node.type === 'start') {
                const hasOutgoing = this.connections.some(c => c.source === id);
                if (!hasOutgoing) {
                    errors.push(`Start node has no outgoing connections`);
                }
            } else if (node.type === 'end') {
                const hasIncoming = this.connections.some(c => c.target === id);
                if (!hasIncoming) {
                    warnings.push(`End node has no incoming connections`);
                }
            } else {
                const hasIncoming = this.connections.some(c => c.target === id);
                const hasOutgoing = this.connections.some(c => c.source === id);

                if (!hasIncoming) {
                    warnings.push(`Node ${node.config.node_id || id} has no incoming connections`);
                }
                if (!hasOutgoing) {
                    warnings.push(`Node ${node.config.node_id || id} has no outgoing connections`);
                }
            }
        });

        // Check required configurations
        this.nodes.forEach((node, id) => {
            if (node.type === 'llm' && !node.config.prompt_template) {
                warnings.push(`LLM node ${node.config.node_id || id} has no prompt template`);
            }
            if (node.type === 'tool' && !node.config.tool_name) {
                errors.push(`Tool node ${node.config.node_id || id} has no tool selected`);
            }
            if (node.type === 'conditional' && !node.config.condition) {
                errors.push(`Conditional node ${node.config.node_id || id} has no condition`);
            }
        });

        return { errors, warnings, isValid: errors.length === 0 };
    }

    showToast(message, type = 'info') {
        // Simple toast implementation
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        document.body.appendChild(toast);

        setTimeout(() => toast.remove(), 3000);
    }

    clear() {
        if (!confirm('Are you sure you want to clear the canvas? This cannot be undone.')) {
            return;
        }

        this.nodes.clear();
        this.connections = [];
        this.canvas.innerHTML = '';
        this.redrawConnections();
        this.deselectAll();
        this.nodeCounter = 0;
    }

    setZoom(level) {
        // Clamp zoom between 25% and 200%
        this.zoomLevel = Math.max(0.25, Math.min(2.0, level));

        // Apply transform to canvas
        this.canvas.style.transform = `scale(${this.zoomLevel})`;
        this.canvas.style.transformOrigin = 'top left';

        // Update SVG canvas size to match zoom
        const baseWidth = 3000;
        const baseHeight = 2500;
        this.svgCanvas.setAttribute('width', baseWidth * this.zoomLevel);
        this.svgCanvas.setAttribute('height', baseHeight * this.zoomLevel);
        this.svgCanvas.style.transform = `scale(${this.zoomLevel})`;
        this.svgCanvas.style.transformOrigin = 'top left';

        // Redraw connections to match new scale
        this.redrawConnections();

        // Show zoom level
        this.showToast(`Zoom: ${Math.round(this.zoomLevel * 100)}%`, 'info');
    }

    zoomIn() {
        this.setZoom(this.zoomLevel + 0.1);
    }

    zoomOut() {
        this.setZoom(this.zoomLevel - 0.1);
    }

    resetZoom() {
        this.setZoom(1.0);
    }
}

// Global designer instance
let designer;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    designer = new WorkflowDesigner();
});

// Global functions for UI
function saveWorkflow() {
    const validation = designer.validate();

    const resultsDiv = document.getElementById('validationResults');
    let html = '';

    if (validation.errors.length > 0) {
        html += validation.errors.map(err =>
            `<div class="validation-message error"><i class="fas fa-exclamation-circle"></i> ${err}</div>`
        ).join('');
    }

    if (validation.warnings.length > 0) {
        html += validation.warnings.map(warn =>
            `<div class="validation-message warning"><i class="fas fa-exclamation-triangle"></i> ${warn}</div>`
        ).join('');
    }

    if (validation.isValid) {
        html += `<div class="validation-message success"><i class="fas fa-check-circle"></i> Workflow is valid!</div>`;
    }

    resultsDiv.innerHTML = html;

    const modal = new bootstrap.Modal(document.getElementById('saveModal'));
    modal.show();
}

function submitWorkflow() {
    const validation = designer.validate();
    if (!validation.isValid) {
        alert('Please fix validation errors before saving');
        return;
    }

    const name = document.getElementById('workflowName').value;
    const description = document.getElementById('workflowDescription').value;

    if (!name) {
        alert('Please enter a workflow name');
        return;
    }

    const workflowJSON = designer.generateJSON();

    const data = {
        name: name,
        description: description,
        definition_json: workflowJSON,
        created_by: 'current_user' // Replace with actual user
    };

    fetch('/workflow/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            designer.showToast('Workflow saved successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('saveModal')).hide();

            setTimeout(() => {
                window.location.href = '/workflow/list';
            }, 1500);
        } else {
            alert('Error saving workflow: ' + result.message);
        }
    })
    .catch(error => {
        alert('Error saving workflow: ' + error);
    });
}

function loadWorkflow() {
    // Create a hidden file input element
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.json,application/json';
    fileInput.style.display = 'none';

    // Handle file selection
    fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) {
            return;
        }

        console.log('Loading file:', file.name);

        // Check file extension
        if (!file.name.endsWith('.json')) {
            alert('Please select a JSON file (.json)');
            return;
        }

        // Read file content
        const reader = new FileReader();

        reader.onload = (event) => {
            try {
                const jsonText = event.target.result;
                console.log('File content loaded, length:', jsonText.length);

                // Parse JSON to validate
                const workflowData = JSON.parse(jsonText);
                console.log('Parsed workflow data:', workflowData);

                // Validate structure
                if (!workflowData.nodes || !Array.isArray(workflowData.nodes)) {
                    throw new Error('JSON must contain a "nodes" array');
                }

                if (!workflowData.edges || !Array.isArray(workflowData.edges)) {
                    throw new Error('JSON must contain an "edges" array');
                }

                // Confirm before clearing
                if (designer.nodes.size > 0) {
                    if (!confirm(`Load workflow from "${file.name}"? This will clear the current workflow.`)) {
                        return;
                    }
                }

                // Clear canvas
                designer.nodes.clear();
                designer.connections = [];
                designer.canvas.innerHTML = '';
                designer.redrawConnections();
                designer.deselectAll();
                designer.nodeCounter = 0;

                // Import nodes
                const nodeIdMap = new Map();
                let xPos = 100;
                let yPos = 100;
                const xSpacing = 250;
                const ySpacing = 150;
                let nodesPerRow = 4;
                let nodeCount = 0;

                console.log(`Loading ${workflowData.nodes.length} nodes...`);

                workflowData.nodes.forEach((nodeData, index) => {
                    console.log(`Processing node ${index}:`, nodeData);

                    const col = nodeCount % nodesPerRow;
                    const row = Math.floor(nodeCount / nodesPerRow);
                    const x = xPos + (col * xSpacing);
                    const y = yPos + (row * ySpacing);

                    const internalId = designer.addNode(nodeData.node_type, x, y);
                    const node = designer.nodes.get(internalId);

                    if (nodeData.node_id) {
                        node.config.node_id = nodeData.node_id;
                    }

                    if (nodeData.config) {
                        Object.assign(node.config, nodeData.config);
                    }

                    // Update node title
                    const nodeElement = document.getElementById(internalId);
                    if (nodeElement) {
                        const titleElement = nodeElement.querySelector('.node-title');
                        if (titleElement) {
                            titleElement.textContent = nodeData.name || node.config.node_id || node.type;
                        }
                    }

                    nodeIdMap.set(nodeData.node_id, internalId);
                    nodeCount++;
                });

                console.log(`Loading ${workflowData.edges.length} edges...`);

                // Import connections
                workflowData.edges.forEach((edge, index) => {
                    console.log(`Processing edge ${index}:`, edge);

                    const sourceId = nodeIdMap.get(edge.source);
                    const targetId = nodeIdMap.get(edge.target);

                    if (sourceId && targetId) {
                        const exists = designer.connections.some(
                            c => c.source === sourceId && c.target === targetId
                        );

                        if (!exists) {
                            designer.connections.push({
                                source: sourceId,
                                target: targetId
                            });
                            console.log(`Created connection: ${sourceId} -> ${targetId}`);
                        }
                    } else {
                        console.warn(`Could not create connection from ${edge.source} to ${edge.target}`);
                    }
                });

                // Redraw connections
                designer.redrawConnections();

                designer.showToast(`Workflow loaded from "${file.name}"!`, 'success');
                console.log('Load complete!');

            } catch (error) {
                console.error('Error loading file:', error);
                alert(`Error loading workflow: ${error.message}\n\nCheck browser console for details.`);
            }
        };

        reader.onerror = (error) => {
            console.error('FileReader error:', error);
            alert('Error reading file. Please try again.');
        };

        // Read file as text
        reader.readAsText(file);
    };

    // Trigger file selection
    document.body.appendChild(fileInput);
    fileInput.click();

    // Cleanup
    setTimeout(() => {
        document.body.removeChild(fileInput);
    }, 1000);
}

function clearCanvas() {
    designer.clear();
}

function validateWorkflow() {
    const validation = designer.validate();

    let message = '';

    if (validation.errors.length > 0) {
        message += '<strong>Errors:</strong><ul>';
        validation.errors.forEach(err => {
            message += `<li>${err}</li>`;
        });
        message += '</ul>';
    }

    if (validation.warnings.length > 0) {
        message += '<strong>Warnings:</strong><ul>';
        validation.warnings.forEach(warn => {
            message += `<li>${warn}</li>`;
        });
        message += '</ul>';
    }

    if (validation.isValid && validation.warnings.length === 0) {
        message = '<div class="alert alert-success"><i class="fas fa-check-circle"></i> Workflow is valid with no warnings!</div>';
    }

    const modal = document.createElement('div');
    modal.innerHTML = `
        <div class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Validation Results</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">${message}</div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal.firstElementChild);
    const bsModal = new bootstrap.Modal(document.querySelector('.modal:last-child'));
    bsModal.show();

    document.querySelector('.modal:last-child').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

function showJSONPreview() {
    const json = designer.generateJSON();
    const formatted = JSON.stringify(json, null, 2);

    document.getElementById('jsonPreview').textContent = formatted;

    const modal = new bootstrap.Modal(document.getElementById('jsonModal'));
    modal.show();
}

function copyJSON() {
    const json = document.getElementById('jsonPreview').textContent;
    navigator.clipboard.writeText(json).then(() => {
        designer.showToast('JSON copied to clipboard!', 'success');
    });
}

function zoomIn() {
    if (designer) {
        designer.zoomIn();
    }
}

function zoomOut() {
    if (designer) {
        designer.zoomOut();
    }
}

// Export Functions

function showExportModal() {
    // Check if modal exists
    const modalElement = document.getElementById('exportJsonModal');
    if (!modalElement) {
        console.error('Export modal not found in HTML. Please update workflow_designer.html');
        alert('Export modal not found. Please refresh the page and ensure workflow_designer.html is updated.');
        return;
    }

    // Generate current workflow JSON
    const json = designer.generateJSON();
    const formatted = JSON.stringify(json, null, 2);

    // Set textarea content - with null check
    const textarea = document.getElementById('exportJsonTextarea');
    if (textarea) {
        textarea.value = formatted;
    }

    // Hide copy success message - with null check
    const successDiv = document.getElementById('copySuccess');
    if (successDiv) {
        successDiv.style.display = 'none';
    }

    // Show modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}

function copyExportJson() {
    const textarea = document.getElementById('exportJsonTextarea');
    const successDiv = document.getElementById('copySuccess');

    // Check if elements exist
    if (!textarea) {
        console.error('Export textarea not found');
        alert('Export functionality error: Elements not found.');
        return;
    }

    // Select and copy text
    textarea.select();
    textarea.setSelectionRange(0, 99999); // For mobile devices

    navigator.clipboard.writeText(textarea.value).then(() => {
        // Show success message
        if (successDiv) {
            successDiv.style.display = 'block';

            // Hide after 2 seconds
            setTimeout(() => {
                successDiv.style.display = 'none';
            }, 2000);
        }

        designer.showToast('JSON copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        alert('Failed to copy to clipboard. Please manually select and copy.');
    });
}

function downloadWorkflowJson() {
    const textarea = document.getElementById('exportJsonTextarea');

    // Check if element exists
    if (!textarea) {
        console.error('Export textarea not found');
        alert('Export functionality error: Elements not found.');
        return;
    }

    const json = textarea.value;

    // Create blob
    const blob = new Blob([json], { type: 'application/json' });

    // Create download link
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;

    // Generate filename with timestamp
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    a.download = `workflow-${timestamp}.json`;

    // Trigger download
    document.body.appendChild(a);
    a.click();

    // Cleanup
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    designer.showToast('Workflow JSON downloaded!', 'success');
}
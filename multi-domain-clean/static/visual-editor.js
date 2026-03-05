/**
 * Visual Editor for Preview Website
 * Allows click-to-edit CSS, text content, and HTML injection
 */

(function() {
  'use strict';

  const EDITOR_STATE = {
    enabled: false,
    selectedElement: null,
    domainId: null,
    customCSS: {},
    customHTML: {},
    textOverrides: {}
  };

  // Initialize editor
  function initVisualEditor(domainId) {
    EDITOR_STATE.domainId = domainId;
    loadCustomizations();
    createEditorUI();
    attachEventListeners();
  }

  // Create editor UI (toggle button + panels)
  function createEditorUI() {
    // Toggle button (fixed position)
    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'visual-editor-toggle';
    toggleBtn.innerHTML = '✏️ Edit Mode';
    toggleBtn.style.cssText = 'position:fixed;top:10px;right:10px;z-index:99999;padding:8px 16px;background:#6C8AE4;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:14px;font-weight:600;box-shadow:0 2px 8px rgba(0,0,0,0.2);';
    toggleBtn.onclick = toggleEditMode;
    document.body.appendChild(toggleBtn);

    // CSS Editor Panel
    const cssPanel = document.createElement('div');
    cssPanel.id = 'visual-editor-css-panel';
    cssPanel.style.cssText = 'display:none;position:fixed;top:60px;right:10px;width:320px;max-height:80vh;overflow-y:auto;background:#fff;border:1px solid #ddd;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:99998;padding:16px;';
    cssPanel.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <h3 style="margin:0;font-size:16px;font-weight:600;">CSS Editor</h3>
        <button id="css-panel-close" style="background:none;border:none;font-size:20px;cursor:pointer;padding:0;line-height:1;">&times;</button>
      </div>
      <div id="css-editor-content"></div>
      <div style="margin-top:12px;display:flex;gap:8px;">
        <button id="css-apply-btn" style="flex:1;padding:8px;background:#22c55e;color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:600;">Apply</button>
        <button id="css-reset-btn" style="padding:8px 12px;background:#ef4444;color:#fff;border:none;border-radius:4px;cursor:pointer;">Reset</button>
      </div>
    `;
    document.body.appendChild(cssPanel);

    // Text Editor Panel
    const textPanel = document.createElement('div');
    textPanel.id = 'visual-editor-text-panel';
    textPanel.style.cssText = 'display:none;position:fixed;top:60px;right:10px;width:400px;background:#fff;border:1px solid #ddd;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:99998;padding:16px;';
    textPanel.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <h3 style="margin:0;font-size:16px;font-weight:600;">Text Editor</h3>
        <button id="text-panel-close" style="background:none;border:none;font-size:20px;cursor:pointer;padding:0;line-height:1;">&times;</button>
      </div>
      <div style="background:#fff3cd;border:1px solid #ffc107;padding:8px;border-radius:4px;margin-bottom:12px;font-size:12px;">
        ⚠️ <strong>Note:</strong> Text from DB will be overridden. Changes are static and won't update if article is regenerated.
      </div>
      <textarea id="text-editor-input" style="width:100%;min-height:120px;padding:8px;border:1px solid #ddd;border-radius:4px;font-family:inherit;resize:vertical;"></textarea>
      <div style="margin-top:12px;display:flex;gap:8px;">
        <button id="text-apply-btn" style="flex:1;padding:8px;background:#22c55e;color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:600;">Apply</button>
        <button id="text-reset-btn" style="padding:8px 12px;background:#ef4444;color:#fff;border:none;border-radius:4px;cursor:pointer;">Reset</button>
      </div>
    `;
    document.body.appendChild(textPanel);

    // HTML Insertion Panel
    const htmlPanel = document.createElement('div');
    htmlPanel.id = 'visual-editor-html-panel';
    htmlPanel.style.cssText = 'display:none;position:fixed;top:60px;right:10px;width:450px;max-height:80vh;overflow-y:auto;background:#fff;border:1px solid #ddd;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:99998;padding:16px;';
    htmlPanel.innerHTML = `
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
        <h3 style="margin:0;font-size:16px;font-weight:600;">Insert HTML/Script</h3>
        <button id="html-panel-close" style="background:none;border:none;font-size:20px;cursor:pointer;padding:0;line-height:1;">&times;</button>
      </div>
      <div style="margin-bottom:12px;">
        <label style="display:block;margin-bottom:4px;font-size:13px;font-weight:600;">Position:</label>
        <select id="html-position-select" style="width:100%;padding:6px;border:1px solid #ddd;border-radius:4px;">
          <option value="before">Before element</option>
          <option value="after">After element</option>
          <option value="prepend">Inside (start)</option>
          <option value="append">Inside (end)</option>
        </select>
      </div>
      <div style="margin-bottom:12px;">
        <label style="display:block;margin-bottom:4px;font-size:13px;font-weight:600;">HTML/Script:</label>
        <textarea id="html-editor-input" style="width:100%;min-height:200px;padding:8px;border:1px solid #ddd;border-radius:4px;font-family:monospace;font-size:12px;resize:vertical;" placeholder="<div>Your HTML here</div>&#10;<script>console.log('Hello');</script>"></textarea>
      </div>
      <div style="display:flex;gap:8px;">
        <button id="html-insert-btn" style="flex:1;padding:8px;background:#6C8AE4;color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:600;">Insert</button>
        <button id="html-remove-btn" style="padding:8px 12px;background:#ef4444;color:#fff;border:none;border-radius:4px;cursor:pointer;">Remove</button>
      </div>
    `;
    document.body.appendChild(htmlPanel);

    // Context Menu
    const contextMenu = document.createElement('div');
    contextMenu.id = 'visual-editor-context-menu';
    contextMenu.style.cssText = 'display:none;position:fixed;background:#fff;border:1px solid #ddd;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,0.15);z-index:99999;padding:4px 0;min-width:160px;';
    contextMenu.innerHTML = `
      <div class="context-menu-item" data-action="css" style="padding:8px 16px;cursor:pointer;font-size:14px;">✏️ Edit CSS</div>
      <div class="context-menu-item" data-action="text" style="padding:8px 16px;cursor:pointer;font-size:14px;">📝 Edit Text</div>
      <div class="context-menu-item" data-action="html" style="padding:8px 16px;cursor:pointer;font-size:14px;">➕ Insert HTML</div>
      <div class="context-menu-item" data-action="inspect" style="padding:8px 16px;cursor:pointer;font-size:14px;">🔍 Inspect</div>
    `;
    document.body.appendChild(contextMenu);

    // Save Bar (fixed bottom)
    const saveBar = document.createElement('div');
    saveBar.id = 'visual-editor-save-bar';
    saveBar.style.cssText = 'display:none;position:fixed;bottom:0;left:0;right:0;background:#2D2D2D;color:#fff;padding:12px 20px;z-index:99997;display:flex;justify-content:space-between;align-items:center;box-shadow:0 -2px 8px rgba(0,0,0,0.2);';
    saveBar.innerHTML = `
      <span style="font-size:14px;">✏️ <strong>Edit Mode Active</strong> — Changes are live but not saved</span>
      <div style="display:flex;gap:12px;">
        <button id="save-all-btn" style="padding:8px 20px;background:#22c55e;color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:600;">💾 Save All</button>
        <button id="discard-all-btn" style="padding:8px 16px;background:#ef4444;color:#fff;border:none;border-radius:4px;cursor:pointer;">❌ Discard</button>
      </div>
    `;
    document.body.appendChild(saveBar);

    // Event listeners for panels
    document.getElementById('css-panel-close').onclick = () => hidePanel('css');
    document.getElementById('text-panel-close').onclick = () => hidePanel('text');
    document.getElementById('html-panel-close').onclick = () => hidePanel('html');
    document.getElementById('css-apply-btn').onclick = applyCSSChanges;
    document.getElementById('css-reset-btn').onclick = resetCSSForElement;
    document.getElementById('text-apply-btn').onclick = applyTextChanges;
    document.getElementById('text-reset-btn').onclick = resetTextForElement;
    document.getElementById('html-insert-btn').onclick = insertHTML;
    document.getElementById('html-remove-btn').onclick = removeInsertedHTML;
    document.getElementById('save-all-btn').onclick = saveAllCustomizations;
    document.getElementById('discard-all-btn').onclick = discardAllChanges;

    // Context menu items
    document.querySelectorAll('.context-menu-item').forEach(item => {
      item.onmouseover = () => item.style.background = '#f0f0f0';
      item.onmouseout = () => item.style.background = 'transparent';
      item.onclick = () => {
        const action = item.dataset.action;
        hideContextMenu();
        if (action === 'css') openCSSEditor();
        else if (action === 'text') openTextEditor();
        else if (action === 'html') openHTMLInserter();
        else if (action === 'inspect') inspectElement();
      };
    });
  }

  // Toggle edit mode
  function toggleEditMode() {
    EDITOR_STATE.enabled = !EDITOR_STATE.enabled;
    const btn = document.getElementById('visual-editor-toggle');
    const saveBar = document.getElementById('visual-editor-save-bar');
    
    if (EDITOR_STATE.enabled) {
      btn.innerHTML = '👁️ View Mode';
      btn.style.background = '#22c55e';
      saveBar.style.display = 'flex';
      document.body.style.cursor = 'crosshair';
    } else {
      btn.innerHTML = '✏️ Edit Mode';
      btn.style.background = '#6C8AE4';
      saveBar.style.display = 'none';
      document.body.style.cursor = 'default';
      clearSelection();
      hideAllPanels();
    }
  }

  // Attach event listeners
  function attachEventListeners() {
    // Click to select element (when edit mode is on)
    document.addEventListener('click', (e) => {
      if (!EDITOR_STATE.enabled) return;
      
      // Ignore clicks on editor UI
      if (e.target.closest('#visual-editor-toggle') || 
          e.target.closest('#visual-editor-css-panel') ||
          e.target.closest('#visual-editor-text-panel') ||
          e.target.closest('#visual-editor-html-panel') ||
          e.target.closest('#visual-editor-context-menu') ||
          e.target.closest('#visual-editor-save-bar')) {
        return;
      }

      e.preventDefault();
      e.stopPropagation();
      selectElement(e.target);
    }, true);

    // Right-click for context menu
    document.addEventListener('contextmenu', (e) => {
      if (!EDITOR_STATE.enabled) return;
      
      if (e.target.closest('#visual-editor-toggle') || 
          e.target.closest('#visual-editor-css-panel') ||
          e.target.closest('#visual-editor-text-panel') ||
          e.target.closest('#visual-editor-html-panel') ||
          e.target.closest('#visual-editor-save-bar')) {
        return;
      }

      e.preventDefault();
      selectElement(e.target);
      showContextMenu(e.pageX, e.pageY);
    }, true);

    // Click outside context menu to close
    document.addEventListener('click', (e) => {
      if (!e.target.closest('#visual-editor-context-menu')) {
        hideContextMenu();
      }
    });

    // Hover highlight
    document.addEventListener('mouseover', (e) => {
      if (!EDITOR_STATE.enabled) return;
      if (e.target.closest('#visual-editor-toggle') || 
          e.target.closest('#visual-editor-css-panel') ||
          e.target.closest('#visual-editor-text-panel') ||
          e.target.closest('#visual-editor-html-panel') ||
          e.target.closest('#visual-editor-context-menu') ||
          e.target.closest('#visual-editor-save-bar')) {
        return;
      }
      highlightElement(e.target);
    });

    document.addEventListener('mouseout', (e) => {
      if (!EDITOR_STATE.enabled) return;
      removeHighlight(e.target);
    });
  }

  // Element selection
  function selectElement(el) {
    clearSelection();
    EDITOR_STATE.selectedElement = el;
    el.classList.add('visual-editor-selected');
    el.style.outline = '2px solid #6C8AE4';
    el.style.outlineOffset = '2px';
  }

  function clearSelection() {
    if (EDITOR_STATE.selectedElement) {
      EDITOR_STATE.selectedElement.classList.remove('visual-editor-selected');
      EDITOR_STATE.selectedElement.style.outline = '';
      EDITOR_STATE.selectedElement.style.outlineOffset = '';
      EDITOR_STATE.selectedElement = null;
    }
  }

  function highlightElement(el) {
    if (el !== EDITOR_STATE.selectedElement) {
      el.style.outline = '1px dashed #6C8AE4';
      el.style.outlineOffset = '1px';
    }
  }

  function removeHighlight(el) {
    if (el !== EDITOR_STATE.selectedElement) {
      el.style.outline = '';
      el.style.outlineOffset = '';
    }
  }

  // Context menu
  function showContextMenu(x, y) {
    const menu = document.getElementById('visual-editor-context-menu');
    menu.style.display = 'block';
    menu.style.left = x + 'px';
    menu.style.top = y + 'px';
  }

  function hideContextMenu() {
    document.getElementById('visual-editor-context-menu').style.display = 'none';
  }

  // CSS Editor
  function openCSSEditor() {
    if (!EDITOR_STATE.selectedElement) return;
    
    hideAllPanels();
    const panel = document.getElementById('visual-editor-css-panel');
    const content = document.getElementById('css-editor-content');
    
    const el = EDITOR_STATE.selectedElement;
    const computed = window.getComputedStyle(el);
    const selector = getElementSelector(el);
    
    content.innerHTML = `
      <div style="margin-bottom:8px;padding:8px;background:#f8f9fa;border-radius:4px;font-size:12px;font-family:monospace;word-break:break-all;">${selector}</div>
      ${createCSSInput('color', 'Color', computed.color, 'color')}
      ${createCSSInput('background-color', 'Background', computed.backgroundColor, 'color')}
      ${createCSSInput('font-size', 'Font Size', computed.fontSize)}
      ${createCSSInput('font-weight', 'Font Weight', computed.fontWeight)}
      ${createCSSInput('width', 'Width', computed.width)}
      ${createCSSInput('height', 'Height', computed.height)}
      ${createCSSInput('margin', 'Margin', computed.margin)}
      ${createCSSInput('padding', 'Padding', computed.padding)}
      ${createCSSInput('border', 'Border', computed.border)}
      ${createCSSInput('border-radius', 'Border Radius', computed.borderRadius)}
      ${createCSSInput('display', 'Display', computed.display)}
      ${createCSSInput('position', 'Position', computed.position)}
    `;
    
    panel.style.display = 'block';
  }

  function createCSSInput(prop, label, value, type = 'text') {
    const id = 'css-' + prop.replace(/[^a-z0-9]/gi, '-');
    if (type === 'color') {
      const rgb = value.match(/\d+/g);
      const hex = rgb ? '#' + rgb.map(x => parseInt(x).toString(16).padStart(2, '0')).join('') : '#000000';
      return `
        <div style="margin-bottom:10px;">
          <label style="display:block;margin-bottom:4px;font-size:13px;font-weight:600;">${label}</label>
          <div style="display:flex;gap:8px;align-items:center;">
            <input type="color" id="${id}" value="${hex}" data-prop="${prop}" style="width:50px;height:32px;border:1px solid #ddd;border-radius:4px;cursor:pointer;">
            <input type="text" id="${id}-text" value="${value}" data-prop="${prop}" style="flex:1;padding:6px;border:1px solid #ddd;border-radius:4px;font-size:13px;">
          </div>
        </div>
      `;
    }
    return `
      <div style="margin-bottom:10px;">
        <label style="display:block;margin-bottom:4px;font-size:13px;font-weight:600;">${label}</label>
        <input type="text" id="${id}" value="${value}" data-prop="${prop}" style="width:100%;padding:6px;border:1px solid #ddd;border-radius:4px;font-size:13px;">
      </div>
    `;
  }

  function applyCSSChanges() {
    if (!EDITOR_STATE.selectedElement) return;
    
    const el = EDITOR_STATE.selectedElement;
    const selector = getElementSelector(el);
    const inputs = document.querySelectorAll('#css-editor-content input[data-prop]');
    
    if (!EDITOR_STATE.customCSS[selector]) {
      EDITOR_STATE.customCSS[selector] = {};
    }
    
    inputs.forEach(input => {
      const prop = input.dataset.prop;
      const value = input.value;
      if (value && value !== 'initial' && value !== 'auto') {
        el.style[prop] = value;
        EDITOR_STATE.customCSS[selector][prop] = value;
      }
    });
    
    hidePanel('css');
    showNotification('CSS applied! Click "Save All" to persist changes.');
  }

  function resetCSSForElement() {
    if (!EDITOR_STATE.selectedElement) return;
    
    const el = EDITOR_STATE.selectedElement;
    const selector = getElementSelector(el);
    
    // Remove inline styles
    el.removeAttribute('style');
    
    // Clear from state
    delete EDITOR_STATE.customCSS[selector];
    
    hidePanel('css');
    showNotification('CSS reset for this element.');
  }

  // Text Editor
  function openTextEditor() {
    if (!EDITOR_STATE.selectedElement) return;
    
    hideAllPanels();
    const panel = document.getElementById('visual-editor-text-panel');
    const textarea = document.getElementById('text-editor-input');
    
    const el = EDITOR_STATE.selectedElement;
    textarea.value = el.textContent || el.innerText || '';
    
    panel.style.display = 'block';
  }

  function applyTextChanges() {
    if (!EDITOR_STATE.selectedElement) return;
    
    const el = EDITOR_STATE.selectedElement;
    const textarea = document.getElementById('text-editor-input');
    const newText = textarea.value;
    const selector = getElementSelector(el);
    
    el.textContent = newText;
    EDITOR_STATE.textOverrides[selector] = newText;
    
    hidePanel('text');
    showNotification('Text updated! Click "Save All" to persist changes.');
  }

  function resetTextForElement() {
    if (!EDITOR_STATE.selectedElement) return;
    
    const el = EDITOR_STATE.selectedElement;
    const selector = getElementSelector(el);
    
    // Would need to reload original from server - for now just clear override
    delete EDITOR_STATE.textOverrides[selector];
    
    hidePanel('text');
    showNotification('Text override removed. Reload page to see original.');
  }

  // HTML Insertion
  function openHTMLInserter() {
    if (!EDITOR_STATE.selectedElement) return;
    
    hideAllPanels();
    const panel = document.getElementById('visual-editor-html-panel');
    panel.style.display = 'block';
  }

  function insertHTML() {
    if (!EDITOR_STATE.selectedElement) return;
    
    const el = EDITOR_STATE.selectedElement;
    const textarea = document.getElementById('html-editor-input');
    const position = document.getElementById('html-position-select').value;
    const html = textarea.value;
    
    if (!html.trim()) {
      showNotification('Please enter HTML to insert.', 'error');
      return;
    }
    
    const wrapper = document.createElement('div');
    wrapper.className = 'visual-editor-inserted';
    wrapper.innerHTML = html;
    wrapper.dataset.insertedAt = Date.now();
    
    const selector = getElementSelector(el);
    
    if (position === 'before') {
      el.parentNode.insertBefore(wrapper, el);
    } else if (position === 'after') {
      el.parentNode.insertBefore(wrapper, el.nextSibling);
    } else if (position === 'prepend') {
      el.insertBefore(wrapper, el.firstChild);
    } else if (position === 'append') {
      el.appendChild(wrapper);
    }
    
    if (!EDITOR_STATE.customHTML[selector]) {
      EDITOR_STATE.customHTML[selector] = [];
    }
    EDITOR_STATE.customHTML[selector].push({ position, html, timestamp: Date.now() });
    
    hidePanel('html');
    showNotification('HTML inserted! Click "Save All" to persist changes.');
  }

  function removeInsertedHTML() {
    if (!EDITOR_STATE.selectedElement) return;
    
    const el = EDITOR_STATE.selectedElement;
    
    if (el.classList.contains('visual-editor-inserted')) {
      el.remove();
      showNotification('Inserted HTML removed.');
    } else {
      // Remove all inserted elements near this element
      const inserted = el.querySelectorAll('.visual-editor-inserted');
      if (inserted.length > 0) {
        inserted.forEach(ins => ins.remove());
        showNotification(`Removed ${inserted.length} inserted element(s).`);
      } else {
        showNotification('No inserted HTML found in this element.', 'error');
      }
    }
    
    hidePanel('html');
  }

  // Inspect element (show in console)
  function inspectElement() {
    if (!EDITOR_STATE.selectedElement) {
      console.log('No element selected');
      return;
    }
    console.log('Selected element:', EDITOR_STATE.selectedElement);
    console.log('Computed styles:', window.getComputedStyle(EDITOR_STATE.selectedElement));
    showNotification('Element logged to console (F12)');
  }

  // Save/Load customizations
  async function saveAllCustomizations() {
    if (!EDITOR_STATE.domainId) {
      showNotification('Domain ID not found', 'error');
      return;
    }
    
    const data = {
      customCSS: EDITOR_STATE.customCSS,
      customHTML: EDITOR_STATE.customHTML,
      textOverrides: EDITOR_STATE.textOverrides
    };
    
    try {
      const response = await fetch(`/api/domains/${EDITOR_STATE.domainId}/visual-customizations`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      const result = await response.json();
      
      if (result.success) {
        showNotification('✅ All customizations saved!', 'success');
      } else {
        showNotification('❌ Save failed: ' + (result.error || 'Unknown error'), 'error');
      }
    } catch (err) {
      showNotification('❌ Network error: ' + err.message, 'error');
    }
  }

  async function loadCustomizations() {
    if (!EDITOR_STATE.domainId) return;
    
    try {
      const response = await fetch(`/api/domains/${EDITOR_STATE.domainId}/visual-customizations`);
      const data = await response.json();
      
      if (data.customCSS) {
        EDITOR_STATE.customCSS = data.customCSS;
        applyLoadedCSS();
      }
      if (data.customHTML) {
        EDITOR_STATE.customHTML = data.customHTML;
        applyLoadedHTML();
      }
      if (data.textOverrides) {
        EDITOR_STATE.textOverrides = data.textOverrides;
        applyLoadedText();
      }
    } catch (err) {
      console.warn('Could not load customizations:', err);
    }
  }

  function applyLoadedCSS() {
    Object.keys(EDITOR_STATE.customCSS).forEach(selector => {
      const el = document.querySelector(selector);
      if (el) {
        const styles = EDITOR_STATE.customCSS[selector];
        Object.keys(styles).forEach(prop => {
          el.style[prop] = styles[prop];
        });
      }
    });
  }

  function applyLoadedHTML() {
    // Would need more complex logic to re-insert HTML at saved positions
    console.log('HTML customizations loaded (not yet applied):', EDITOR_STATE.customHTML);
  }

  function applyLoadedText() {
    Object.keys(EDITOR_STATE.textOverrides).forEach(selector => {
      const el = document.querySelector(selector);
      if (el) {
        el.textContent = EDITOR_STATE.textOverrides[selector];
      }
    });
  }

  function discardAllChanges() {
    if (!confirm('Discard all unsaved changes?')) return;
    
    EDITOR_STATE.customCSS = {};
    EDITOR_STATE.customHTML = {};
    EDITOR_STATE.textOverrides = {};
    
    location.reload();
  }

  // Utility functions
  function getElementSelector(el) {
    if (el.id) return '#' + el.id;
    
    let path = [];
    while (el && el.nodeType === Node.ELEMENT_NODE) {
      let selector = el.nodeName.toLowerCase();
      if (el.className && typeof el.className === 'string') {
        selector += '.' + el.className.trim().split(/\s+/).join('.');
      }
      path.unshift(selector);
      el = el.parentNode;
      if (path.length > 3) break; // Limit depth
    }
    return path.join(' > ');
  }

  function hidePanel(type) {
    document.getElementById(`visual-editor-${type}-panel`).style.display = 'none';
  }

  function hideAllPanels() {
    hidePanel('css');
    hidePanel('text');
    hidePanel('html');
    hideContextMenu();
  }

  function showNotification(message, type = 'info') {
    const notif = document.createElement('div');
    notif.style.cssText = `position:fixed;top:70px;right:10px;z-index:100000;padding:12px 20px;background:${type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : '#6C8AE4'};color:#fff;border-radius:6px;box-shadow:0 2px 8px rgba(0,0,0,0.2);font-size:14px;font-weight:600;max-width:300px;`;
    notif.textContent = message;
    document.body.appendChild(notif);
    
    setTimeout(() => {
      notif.style.transition = 'opacity 0.3s';
      notif.style.opacity = '0';
      setTimeout(() => notif.remove(), 300);
    }, 3000);
  }

  // Auto-initialize if domain ID is in URL
  const match = window.location.pathname.match(/\/preview-website\/(\d+)/);
  if (match) {
    const domainId = parseInt(match[1], 10);
    if (window.location.search.includes('edit=1') || window.localStorage.getItem('visualEditorEnabled') === 'true') {
      window.addEventListener('DOMContentLoaded', () => initVisualEditor(domainId));
    } else {
      // Add init button for manual activation
      window.addEventListener('DOMContentLoaded', () => {
        const initBtn = document.createElement('button');
        initBtn.innerHTML = '🎨 Enable Visual Editor';
        initBtn.style.cssText = 'position:fixed;bottom:20px;right:20px;z-index:99999;padding:10px 20px;background:#6C8AE4;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:14px;font-weight:600;box-shadow:0 2px 8px rgba(0,0,0,0.2);';
        initBtn.onclick = () => {
          initBtn.remove();
          initVisualEditor(domainId);
        };
        document.body.appendChild(initBtn);
      });
    }
  }

  // Expose to window for manual init
  window.initVisualEditor = initVisualEditor;
})();

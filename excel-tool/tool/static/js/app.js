// Global state
let currentFileId = null;
let currentColumns = [];
let currentPreviewData = [];
let currentConversionId = null;
let currentSkipRows = 0;

// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-upload');
const uploadForm = document.getElementById('upload-form');
const uploadStatus = document.getElementById('upload-status');
const previewSection = document.getElementById('preview-section');
const emptyState = document.getElementById('empty-state');
const tableHeader = document.getElementById('table-header');
const tableBody = document.getElementById('table-body');
const fileInfo = document.getElementById('file-info');
const processBtn = document.getElementById('process-btn');
const downloadBtn = document.getElementById('download-btn');
const copyBtn = document.getElementById('copy-btn');
const selectAllBtn = document.getElementById('select-all-btn');
const deselectAllBtn = document.getElementById('deselect-all-btn');
const processStatus = document.getElementById('process-status');
const skipRowsInput = document.getElementById('skip-rows');

// Load saved preference
const savedSkipRows = localStorage.getItem('excel_tool_skip_rows');
if (savedSkipRows !== null && skipRowsInput) {
    skipRowsInput.value = savedSkipRows;
}

// Save preference on change
if (skipRowsInput) {
    skipRowsInput.addEventListener('change', () => {
        localStorage.setItem('excel_tool_skip_rows', skipRowsInput.value);
    });
}

// Drag and drop handlers
dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drop-zone-active');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drop-zone-active');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drop-zone-active');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFileUpload();
    }
});

fileInput.addEventListener('change', handleFileUpload);

// File upload handler
async function handleFileUpload() {
    const file = fileInput.files[0];
    if (!file) return;

    const skipRows = document.getElementById('skip-rows').value || '0';

    const formData = new FormData();
    formData.append('file_path', file);
    formData.append('skip_rows', skipRows);
    formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

    uploadStatus.classList.remove('hidden');
    
    try {
        const response = await fetch('/excel/upload/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();

        if (data.success) {
            currentFileId = data.file_id;
            currentColumns = data.columns;
            currentPreviewData = data.preview_data;
            currentSkipRows = data.skip_rows || 0;
            
            displayPreview(data);
            showNotification('Document analyzed successfully', 'success');
        } else {
            showNotification('Analysis failed: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('System error: ' + error.message, 'error');
    } finally {
        uploadStatus.classList.add('hidden');
        fileInput.value = '';
    }
}

// Display preview
function displayPreview(data, isResult = false) {
    emptyState.classList.add('hidden');
    previewSection.classList.remove('hidden');
    
    fileInfo.textContent = `${data.filename} • ${data.total_rows} rows • ${data.columns.length} columns`;
    
    // Create table header with checkboxes (only if not a result)
    tableHeader.innerHTML = '';
    data.columns.forEach(col => {
        const th = document.createElement('th');
        th.className = 'px-6 py-4 text-left text-[11px] font-bold text-slate-400 uppercase tracking-widest bg-slate-50/50';
        if (isResult) {
            th.innerHTML = `<span class="text-indigo-600">${col}</span>`;
        } else {
            th.innerHTML = `
                <label class="flex items-center gap-2 cursor-pointer group">
                    <input type="checkbox" class="column-checkbox h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500/20 transition-all" value="${col}" checked>
                    <span class="group-hover:text-slate-600 transition-colors">${col}</span>
                </label>
            `;
        }
        tableHeader.appendChild(th);
    });
    
    // Create table body
    tableBody.innerHTML = '';
    data.preview_data.forEach(row => {
        const tr = document.createElement('tr');
        tr.className = isResult ? 'bg-indigo-50/30' : 'hover:bg-slate-50/50 transition-colors cursor-default';
        
        data.columns.forEach(col => {
            const td = document.createElement('td');
            td.className = 'px-6 py-4 whitespace-nowrap text-xs text-slate-600 border-r border-slate-50 last:border-0';
            td.textContent = row[col] || '';
            tr.appendChild(td);
        });
        
        tableBody.appendChild(tr);
    });
    
    // Reset buttons
    downloadBtn.classList.add('hidden');
    copyBtn.classList.add('hidden');
    processBtn.classList.remove('hidden');
    processBtn.innerHTML = '<i data-lucide="zap" class="w-4 h-4"></i> Execute Transformation';
    lucide.createIcons();
}

// Select/Deselect all columns
selectAllBtn.addEventListener('click', () => {
    document.querySelectorAll('.column-checkbox').forEach(cb => cb.checked = true);
});

deselectAllBtn.addEventListener('click', () => {
    document.querySelectorAll('.column-checkbox').forEach(cb => cb.checked = false);
});

// Process file
processBtn.addEventListener('click', async () => {
    const selectedColumns = Array.from(document.querySelectorAll('.column-checkbox:checked'))
        .map(cb => cb.value);
    
    if (selectedColumns.length === 0) {
        showNotification('Selection required: Please select at least one column', 'error');
        return;
    }
    
    processBtn.disabled = true;
    processBtn.innerHTML = '<div class="spinner mr-2"></div> Working...';
    
    try {
        const response = await fetch('/excel/process/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({
                file_id: currentFileId,
                columns: selectedColumns,
                skip_rows: currentSkipRows
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentConversionId = data.conversion_id;
            window.csvText = data.csv_text;
            
            downloadBtn.classList.remove('hidden');
            downloadBtn.onclick = () => window.location.href = data.download_url;
            
            copyBtn.classList.remove('hidden');
            processBtn.classList.add('hidden');
            
            // Show result preview in table
            displayPreview(data, true);
            
            showNotification(`Transformation successful: ${data.rows_processed} rows processed`, 'success');
            loadHistory();
        } else {
            showNotification('Error: ' + data.error, 'error');
        }
    } catch (error) {
        showNotification('Execution failed: ' + error.message, 'error');
    } finally {
        processBtn.disabled = false;
        processBtn.innerHTML = '<i data-lucide="zap" class="w-4 h-4"></i> Execute Transformation';
        lucide.createIcons();
    }
});

// Copy to clipboard
copyBtn.addEventListener('click', async () => {
    try {
        await navigator.clipboard.writeText(window.csvText);
        
        const originalContent = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i data-lucide="check" class="w-4 h-4 text-green-500"></i> Buffer Copied';
        
        setTimeout(() => {
            copyBtn.innerHTML = originalContent;
            lucide.createIcons();
        }, 2000);
        
        showNotification('CSV blueprint copied to clipboard', 'success');
    } catch (error) {
        showNotification('Clipboard access denied: ' + error.message, 'error');
    }
});

// Load history
async function loadHistory() {
    try {
        const response = await fetch('/excel/history/');
        const data = await response.json();
        
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';
        
        if (data.history.length === 0) {
            historyList.innerHTML = `
                <div class="text-center py-10">
                    <i data-lucide="inbox" class="mx-auto h-8 w-8 text-slate-200 mb-2"></i>
                    <p class="text-slate-400 text-[11px]">No recent data converted</p>
                </div>
            `;
            lucide.createIcons();
            return;
        }
        
        data.history.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item bg-slate-50/50 border border-slate-100 rounded-lg p-3 cursor-pointer hover:bg-white hover:border-indigo-200 hover:shadow-sm transition-all group';
            div.dataset.conversionId = item.id;
            div.innerHTML = `
                <div class="flex justify-between items-start gap-3">
                    <div class="flex-1 min-w-0">
                        <p class="text-slate-700 font-medium text-[13px] truncate group-hover:text-indigo-600 transition-colors">${item.filename}</p>
                        <p class="text-slate-400 text-[10px] uppercase font-bold mt-1 tracking-tight">${item.timestamp}</p>
                    </div>
                    <span class="text-[10px] font-bold bg-slate-100 text-slate-500 px-2 py-0.5 rounded uppercase flex-shrink-0 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors">${item.rows_processed}r</span>
                </div>
            `;
            
            div.addEventListener('click', () => loadConversion(item.id));
            historyList.appendChild(div);
        });
        lucide.createIcons();
    } catch (error) {
        console.error('History sync failed:', error);
    }
}

// Load conversion from history
async function loadConversion(conversionId) {
    try {
        const response = await fetch(`/excel/load/${conversionId}/`);
        const data = await response.json();
        
        if (data.success) {
            displayPreview(data);
            currentConversionId = data.conversion_id;
            
            downloadBtn.classList.remove('hidden');
            downloadBtn.onclick = () => window.location.href = `/excel/download/${conversionId}/`;
            processBtn.classList.add('hidden');
            
            showNotification('Context restored from archive', 'success');
        }
    } catch (error) {
        showNotification('Restore failed: ' + error.message, 'error');
    }
}

// Notification system
function showNotification(message, type = 'info') {
    const icons = {
        success: 'check-circle-2',
        error: 'alert-circle',
        info: 'info'
    };
    
    const colors = {
        success: 'bg-white border-green-100 text-green-800 shadow-green-100/50',
        error: 'bg-white border-red-100 text-red-800 shadow-red-100/50',
        info: 'bg-white border-indigo-100 text-indigo-800 shadow-indigo-100/50'
    };

    const iconColors = {
        success: 'text-green-500',
        error: 'text-red-500',
        info: 'text-indigo-500'
    };
    
    const notification = document.createElement('div');
    notification.className = `fixed bottom-6 right-6 border ${colors[type]} px-5 py-3.5 rounded-xl shadow-xl flex items-center gap-3 z-50 transition-all duration-300 transform translate-y-10 opacity-0`;
    notification.innerHTML = `
        <i data-lucide="${icons[type]}" class="w-5 h-5 ${iconColors[type]}"></i>
        <span class="text-[13px] font-semibold tracking-tight">${message}</span>
    `;
    
    document.body.appendChild(notification);
    lucide.createIcons();
    
    // Animate in
    requestAnimationFrame(() => {
        notification.classList.remove('translate-y-10', 'opacity-0');
    });
    
    setTimeout(() => {
        notification.classList.add('opacity-0', 'translate-y-4');
        setTimeout(() => notification.remove(), 400);
    }, 4000);
}

// Load history on page load
document.addEventListener('DOMContentLoaded', () => {
    // Initial history click handlers - these are now handled by loadHistory() but let's keep static ones too
    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
            const conversionId = item.dataset.conversionId;
            loadConversion(conversionId);
        });
    });
});

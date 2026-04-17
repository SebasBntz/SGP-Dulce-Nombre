// Depends on auth.js for authentication and authFetch
let currentSection = 'dashboard';
let aportesChart = null;
let currentEditingId = null;
let currentSearchQuery = '';
let searchTimeout = null;

// Pagination
let currentPage = 0;
const pageSize = 50;

const sectionConfig = {
    'dashboard': {
        title: 'Inicio',
        desc: 'Resumen general de registros parroquiales y estadísticas',
        endpoint: '/parroquia/dashboard/stats',
        headers: []
    },
    'bautizos': {
        title: 'Gestión de Bautizos',
        desc: 'Registro detallado de actas de bautismo.',
        endpoint: '/actas/bautizos/',
        headers: ['Libro', 'Folio', 'Número', 'Nombre', 'Apellidos', 'Fecha Bautizo', 'Acciones']
    },
    'matrimonios': {
        title: 'Gestión de Matrimonios',
        desc: 'Registro de uniones matrimoniales.',
        endpoint: '/actas/matrimonios/',
        headers: ['Libro', 'Folio', 'Número', 'Esposo', 'Esposa', 'Fecha Matrimonio', 'Acciones']
    },
    'confirmaciones': {
        title: 'Confirmaciones',
        desc: 'Registro de sacramentos de confirmación.',
        endpoint: '/actas/confirmaciones/',
        headers: ['Libro', 'Folio', 'Número', 'Nombre', 'Apellidos', 'Fecha Confirmación', 'Acciones']
    },
    'comuniones': {
        title: 'Primeras Comuniones',
        desc: 'Registro de sacramentos de primera eucaristía.',
        endpoint: '/actas/comuniones/',
        headers: ['Libro', 'Folio', 'Número', 'Nombre', 'Apellidos', 'Fecha Comunión', 'Acciones']
    },
    'personas': {
        title: 'Feligreses',
        desc: 'Directorio general de personas vinculadas.',
        endpoint: '/parroquia/personas/',
        headers: ['ID', 'Nombres', 'Apellidos', 'Teléfono', 'Email', 'Acciones']
    },
    'sacerdotes': {
        title: 'Sacerdotes',
        desc: 'Directorio de ministros de la iglesia.',
        endpoint: '/parroquia/sacerdotes/',
        headers: ['ID', 'Nombres', 'Apellidos', 'Teléfono', 'Email', 'Acciones']
    },
    'grupos': {
        title: 'Grupos Parroquiales',
        desc: 'Gestión de comunidades y grupos.',
        endpoint: '/parroquia/grupos/',
        headers: ['ID', 'Nombre', 'Descripción', 'Acciones']
    },
    'aportes': {
        title: 'Control de Aportes',
        desc: 'Gestión de contribuciones económicas.',
        endpoint: '/parroquia/aportes/',
        headers: ['ID', 'Persona', 'Monto', 'Fecha', 'Tipo', 'Acciones']
    }
};

document.addEventListener('DOMContentLoaded', () => {
    updateDate();
    setInterval(updateDate, 1000 * 60 * 30); // Update every 30 mins
    showSection('dashboard');
    
    // Optimized Global Search with Debounce
    const searchInput = document.getElementById('main-search');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                currentPage = 0; // Reset pagination on search
                loadRecords();
            }, 300);
        });
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                clearTimeout(searchTimeout);
                currentPage = 0;
                loadRecords();
            }
        });
    }

    // Form submit
    const form = document.getElementById('record-form');
    if (form) {
        form.addEventListener('submit', saveRecord);
    }
});

function updateDate() {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateEl = document.getElementById('current-date');
    if (dateEl) dateEl.innerText = new Date().toLocaleDateString('es-ES', options);
}

function showSection(section) {
    try {
        if (window.innerWidth <= 992) {
            document.querySelector('.sidebar')?.classList.remove('mobile-open');
        }

        currentSection = section;
        const config = sectionConfig[section];
        
        // Update labels
        const titleEl = document.getElementById('section-title');
        const descEl = document.getElementById('section-desc');
        if(titleEl) titleEl.innerText = config?.title || '';
        if(descEl) descEl.innerText = config?.desc || '';
        
        // Update sidebar active state
        document.querySelectorAll('.sidebar li').forEach(li => {
            const onClick = li.getAttribute('onclick');
            li.classList.toggle('active', onClick && onClick.includes(`'${section}'`));
        });
        
        const crudControls = document.getElementById('crud-controls');
        const tableWrapper = document.querySelector('.table-wrapper');
        const dashboardSection = document.getElementById('dashboard-section');
        const balanceSection = document.getElementById('balance-section');
        const paginationControls = document.getElementById('pagination-controls');

        // UI Toggle logic
        const isDashboard = section === 'dashboard';
        
        const btnGlobal = document.getElementById('btn-nuevo-acta-global');
        if (btnGlobal) {
            btnGlobal.style.display = isDashboard ? 'none' : 'flex';
        }

        if (crudControls) {
            crudControls.style.display = isDashboard ? 'none' : 'flex';
        }
        
        if (tableWrapper) tableWrapper.style.display = isDashboard ? 'none' : 'block';
        if (dashboardSection) dashboardSection.style.display = isDashboard ? 'block' : 'none';
        if (paginationControls) paginationControls.style.display = isDashboard ? 'none' : 'flex';
        
        if (isDashboard) {
            loadDashboardStats();
        } else {
            const headersRow = document.getElementById('table-headers');
            if (headersRow && config) headersRow.innerHTML = (config.headers || []).map(h => `<th>${h}</th>`).join('');
            
            if (balanceSection) balanceSection.style.display = (section === 'aportes' ? 'block' : 'none');
            
            currentPage = 0;
            closePanel();
            loadRecords();
        }
    } catch (err) {
        console.error("Error in showSection:", err);
        if (typeof showToast === 'function') showToast("Error al cambiar sección: " + err.message, "error");
    }
}

function changePage(delta) {
    currentPage += delta;
    if (currentPage < 0) currentPage = 0;
    loadRecords();
}

async function loadRecords() {
    const config = sectionConfig[currentSection];
    const tbody = document.getElementById('records-body');
    if(!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="100%"><div class="spinner"></div></td></tr>';

    const skip = currentPage * pageSize;
    const limit = pageSize;
    const q = document.getElementById('main-search')?.value.trim() || '';

    try {
        let url = `${API_BASE}${config.endpoint}?skip=${skip}&limit=${limit}`;
        if (q) url += `&search=${encodeURIComponent(q)}`;
        
        const response = await authFetch(url);
        const data = await response.json();
        const records = data.records || [];
        const total = data.total || 0;

        if (records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="100%" style="text-align:center; padding:40px; color:var(--text-muted);">No se encontraron registros.</td></tr>';
            updatePaginationUI(0, 0, 0);
            return;
        }

        // Optimized DOM updates with document fragment could go here, but strings are fine for this scale
        tbody.innerHTML = records.map(record => {
            const recordId = record.id || record.id_persona || record.id_sacerdote || record.id_grupo || record.id_aporte;
            let rowBody = '';
            
            if (['bautizos', 'confirmaciones', 'comuniones', 'matrimonios'].includes(currentSection)) {
                rowBody += `<td>${record.libro || '-'}</td><td>${record.folio || '-'}</td><td>${record.numero || '-'}</td>`;
                
                if (currentSection === 'matrimonios') {
                    rowBody += `<td>${record.nombre_esposo}</td><td>${record.nombre_esposa}</td><td>${record.fecha_matrimonio}</td>`;
                } else {
                    rowBody += `<td>${record.nombre}</td><td>${record.apellidos}</td><td>${record.fecha_bautizo || record.fecha_confirmacion || record.fecha_comunion || '-'}</td>`;
                }
            } else {
                rowBody += `<td>${recordId}</td>`;
                if (['personas', 'sacerdotes'].includes(currentSection)) {
                    rowBody += `<td>${record.nombres}</td><td>${record.apellidos}</td><td>${record.telefono || '-'}</td><td>${record.email || '-'}</td>`;
                } else if (currentSection === 'grupos') {
                    rowBody += `<td><strong>${record.nombre}</strong></td><td>${record.descripcion || '-'}</td>`;
                } else if (currentSection === 'aportes') {
                    rowBody += `<td>${record.persona_nombre || '<span style="color:#94a3b8; font-style:italic;">Anónimo</span>'}</td><td><strong>$${new Intl.NumberFormat('es-CO').format(record.monto)}</strong></td><td>${record.fecha}</td><td><span class="badge">${record.tipo || '-'}</span></td>`;
                }
            }

            rowBody += `<td class="actions">`;
            if (config.endpoint.includes('/actas/')) {
                rowBody += `<button class="btn-pdf" onclick="downloadPDF(${recordId}, '${currentSection}')" title="Descargar PDF"><i class="fas fa-file-pdf"></i></button>`;
            }
            rowBody += `<button class="btn-view" onclick="viewRecord(${recordId})" title="Ver Detalles"><i class="fas fa-eye"></i></button>`;
            rowBody += `<button class="btn-delete" style="color:#ef4444; background:#fee2e2; border:none; width:38px; height:38px; border-radius:10px; cursor:pointer;" onclick="deleteRecord(${recordId})" title="Eliminar"><i class="fas fa-trash"></i></button>`;
            rowBody += `</td>`;
            
            return `<tr>${rowBody}</tr>`;
        }).join('');

        updatePaginationUI(skip, records.length, total);
        window.currentRecordsData = records; 
        
        if (currentSection === 'aportes') loadBalance();
    } catch (error) {
        console.error("Error loading records:", error);
        tbody.innerHTML = '<tr><td colspan="100%" style="text-align:center; color:red; padding:20px;">Error al cargar datos. Compruebe la conexión con el servidor.</td></tr>';
    }
}

function updatePaginationUI(skip, count, total) {
    const controls = document.getElementById('pagination-controls');
    if (!controls) return;

    if (total <= pageSize && currentPage === 0) {
        controls.style.display = 'none';
        return;
    }

    controls.style.display = 'flex';
    document.getElementById('pag-range').innerText = total === 0 ? '0-0' : `${skip + 1}-${skip + count}`;
    document.getElementById('pag-total').innerText = total;

    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    
    if (btnPrev) {
        btnPrev.disabled = currentPage === 0;
        btnPrev.style.opacity = btnPrev.disabled ? '0.3' : '1';
    }
    if (btnNext) {
        btnNext.disabled = (skip + count) >= total;
        btnNext.style.opacity = btnNext.disabled ? '0.3' : '1';
    }
}

async function loadDashboardStats() {
    try {
        const response = await authFetch(`${API_BASE}/parroquia/dashboard/stats`);
        const stats = await response.json();
        
        const updateVal = (id, val, isPrice = false) => {
            const el = document.getElementById(id);
            if (!el) return;
            el.innerText = isPrice ? `$${new Intl.NumberFormat('es-CO').format(val || 0)}` : (val || 0);
        };

        updateVal('dash-bautizos', stats.bautizos);
        updateVal('dash-matrimonios', stats.matrimonios);
        updateVal('dash-confirmaciones', stats.confirmaciones);
        updateVal('dash-comuniones', stats.comuniones);
        updateVal('dash-aportes', stats.aportes, true);
    } catch (error) {
        console.error("Stats Error:", error);
    }
}

async function downloadPDF(id, section) {
    try {
        const response = await authFetch(`${API_BASE}/actas/${section}/${id}/pdf`);
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `acta_${section}_${id}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            showToast("Error al generar PDF", "error");
        }
    } catch (error) {
        showToast("Error de conexión al generar PDF", "error");
    }
}

function viewRecord(id) {
    const record = window.currentRecordsData?.find(r => (r.id || r.id_persona || r.id_sacerdote || r.id_grupo || r.id_aporte) == id);
    if (!record) return;

    const modal = document.getElementById('details-modal');
    const content = document.getElementById('modal-content');
    
    let html = '<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:20px;">';
    for (const [key, val] of Object.entries(record)) {
        if (val !== null && val !== undefined && typeof val !== 'object') {
            const label = key.replace(/_/g, ' ').toUpperCase();
            html += `<div class="detail-item">
                <label style="color:var(--text-muted); font-size:0.75rem; font-weight:700;">${label}</label>
                <div style="font-weight:600; color:var(--text-main); margin-top:4px;">${val}</div>
            </div>`;
        }
    }
    html += '</div>';
    
    content.innerHTML = html;
    modal.style.display = 'flex';
}

function closeDetailsModal() {
    document.getElementById('details-modal').style.display = 'none';
}

async function deleteRecord(id) {
    if (!confirm("¿Estás seguro de eliminar este registro permanentemente?")) return;
    
    try {
        const config = sectionConfig[currentSection];
        const response = await authFetch(`${API_BASE}${config.endpoint}${id}`, { method: 'DELETE' });
        if (response.ok) {
            showToast("Registro eliminado con éxito", "success");
            loadRecords();
            if (currentSection !== 'dashboard') loadDashboardStats();
        } else {
            showToast("No se pudo eliminar el registro", "error");
        }
    } catch (error) {
        showToast("Error al procesar eliminación", "error");
    }
}

function openPanel() {
    const panel = document.getElementById('side-panel');
    const title = document.getElementById('panel-title');
    const fields = document.getElementById('form-fields');
    
    title.innerText = `Nuevo: ${sectionConfig[currentSection].title}`;
    
    // Dynamic Fields optimization
    let html = '';
    const s = currentSection;
    
    if (s === 'bautizos') {
        html = `
            <div class="form-group"><label>Libro</label><input type="text" name="libro" required></div>
            <div class="form-group"><label>Folio</label><input type="text" name="folio" required></div>
            <div class="form-group"><label>Número</label><input type="text" name="numero" required></div>
            <div class="form-group"><label>Nombre</label><input type="text" name="nombre" required></div>
            <div class="form-group"><label>Apellidos</label><input type="text" name="apellidos" required></div>
            <div class="form-group"><label>Fecha Nac.</label><input type="date" name="fecha_nacimiento"></div>
            <div class="form-group"><label>Fecha Bautizo</label><input type="date" name="fecha_bautizo" required></div>
            <div class="form-group"><label>Lugar Nac.</label><input type="text" name="lugar_nacimiento"></div>
            <div class="form-group"><label>Nombre Padre</label><input type="text" name="nombre_padre"></div>
            <div class="form-group"><label>Nombre Madre</label><input type="text" name="nombre_madre"></div>
            <div class="form-group full-width"><label>Abuelos Paternos</label><input type="text" name="abuelos_paternos"></div>
            <div class="form-group full-width"><label>Abuelos Maternos</label><input type="text" name="abuelos_maternos"></div>
            <div class="form-group"><label>Padrinos</label><input type="text" name="nombre_padrino"></div>
            <div class="form-group"><label>Ministro</label><input type="text" name="nombre_cura" list="priests-list"></div>
            <div class="form-group"><label>Párroco (Doy Fe)</label><input type="text" name="da_fe" list="priests-list"></div>
            <div class="form-group full-width"><label>Nota al Margen</label><textarea name="nota_al_margen" rows="3"></textarea></div>
        `;
    } else if (s === 'matrimonios') {
        html = `
            <div class="form-group"><label>Libro</label><input type="text" name="libro" required></div>
            <div class="form-group"><label>Folio</label><input type="text" name="folio" required></div>
            <div class="form-group"><label>Número</label><input type="text" name="numero" required></div>
            <div class="form-group"><label>Fecha de Matrimonio</label><input type="date" name="fecha_matrimonio" required></div>
            <h4 class="full-width" style="margin:15px 0 5px 0; color:var(--primary); font-size:0.9rem; border-bottom:2px solid var(--primary); padding-bottom:5px;"><i class="fas fa-male" style="margin-right:6px;"></i>Datos del Esposo</h4>
            <div class="form-group full-width"><label>El Esposo (Nombre Completo)</label><input type="text" name="nombre_esposo" required placeholder=""></div>
            <div class="form-group full-width"><label>Hijo de</label><input type="text" name="padres_esposo" placeholder=""></div>
            <div class="form-group full-width"><label>Bautizado en (Parroquia)</label><input type="text" name="parroquia_bautizo_esposo" placeholder=""></div>
            <div class="form-group"><label>El día (Fecha Bautizo)</label><input type="date" name="fecha_bautizo_esposo"></div>
            <h4 class="full-width" style="margin:15px 0 5px 0; color:#e91e8c; font-size:0.9rem; border-bottom:2px solid #e91e8c; padding-bottom:5px;"><i class="fas fa-female" style="margin-right:6px;"></i>Datos de la Esposa</h4>
            <div class="form-group full-width"><label>La Esposa (Nombre Completo)</label><input type="text" name="nombre_esposa" required placeholder=""></div>
            <div class="form-group full-width"><label>Hija de</label><input type="text" name="padres_esposa" placeholder=""></div>
            <div class="form-group full-width"><label>Bautizada en (Parroquia)</label><input type="text" name="parroquia_bautizo_esposa" placeholder=""></div>
            <div class="form-group"><label>El día (Fecha Bautizo)</label><input type="date" name="fecha_bautizo_esposa"></div>
            <h4 class="full-width" style="margin:15px 0 5px 0; color:#64748b; font-size:0.9rem; border-bottom:2px solid #94a3b8; padding-bottom:5px;"><i class="fas fa-info-circle" style="margin-right:6px;"></i>Datos Adicionales</h4>
            <div class="form-group full-width"><label>Testigos</label><input type="text" name="testigos" placeholder=""></div>
            <div class="form-group"><label>Presenció (Ministro)</label><input type="text" name="nombre_cura" list="priests-list" placeholder=""></div>
            <div class="form-group full-width"><label>Legitimación de Hijos</label><input type="text" name="legitimacion_hijos" placeholder=""></div>
            <div class="form-group"><label>Da Fe (Párroco)</label><input type="text" name="da_fe" list="priests-list" placeholder=""></div>
            <div class="form-group full-width"><label>Nota al Margen</label><textarea name="nota_al_margen" rows="3" placeholder=""></textarea></div>
        `;
    } else if (s === 'confirmaciones') {
        html = `
            <div class="form-group"><label>Libro</label><input type="text" name="libro" required></div>
            <div class="form-group"><label>Folio</label><input type="text" name="folio" required></div>
            <div class="form-group"><label>Número</label><input type="text" name="numero" required></div>
            <div class="form-group"><label>Nombre</label><input type="text" name="nombre" required></div>
            <div class="form-group"><label>Apellidos</label><input type="text" name="apellidos" required></div>
            <div class="form-group"><label>Fecha Nac.</label><input type="date" name="fecha_nacimiento"></div>
            <div class="form-group"><label>Fecha Bautizo</label><input type="date" name="fecha_bautizo"></div>
            <div class="form-group full-width"><label>Parroquia de Bautizo</label><input type="text" name="parroquia_bautizo"></div>
            <div class="form-group full-width"><label>Lugar de Bautismo</label><input type="text" name="lugar_bautismo"></div>
            <div class="form-group"><label>Fecha Confirmación</label><input type="date" name="fecha_confirmacion" required></div>
            <div class="form-group"><label>Lugar Confirmación</label><input type="text" name="lugar_confirmacion"></div>
            <div class="form-group"><label>Nombre Padre</label><input type="text" name="nombre_padre"></div>
            <div class="form-group"><label>Nombre Madre</label><input type="text" name="nombre_madre"></div>
            <div class="form-group"><label>Nombre Padrino</label><input type="text" name="nombre_padrino"></div>
            <div class="form-group"><label>Nombre Madrina</label><input type="text" name="nombre_madrina"></div>
            <div class="form-group"><label>Obispo (Quien Confirma)</label><input type="text" name="obispo"></div>
            <div class="form-group"><label>Ministro (Párroco)</label><input type="text" name="nombre_cura" list="priests-list"></div>
            <div class="form-group"><label>Doy Fe (Párroco)</label><input type="text" name="da_fe" list="priests-list"></div>
            <div class="form-group full-width"><label>Nota al Margen</label><textarea name="nota_al_margen" rows="3"></textarea></div>
        `;
    } else if (s === 'comuniones') {
        html = `
            <div class="form-group"><label>Libro</label><input type="text" name="libro" required></div>
            <div class="form-group"><label>Folio</label><input type="text" name="folio" required></div>
            <div class="form-group"><label>Número</label><input type="text" name="numero" required></div>
            <div class="form-group"><label>Nombre</label><input type="text" name="nombre" required></div>
            <div class="form-group"><label>Apellidos</label><input type="text" name="apellidos" required></div>
            <div class="form-group"><label>Fecha Nac.</label><input type="date" name="fecha_nacimiento"></div>
            <div class="form-group"><label>Fecha Bautizo</label><input type="date" name="fecha_bautizo"></div>
            <div class="form-group full-width"><label>Parroquia de Bautizo</label><input type="text" name="parroquia_bautizo"></div>
            <div class="form-group full-width"><label>Lugar de Bautismo</label><input type="text" name="lugar_bautismo"></div>
            <div class="form-group"><label>Fecha Primera Comunión</label><input type="date" name="fecha_comunion" required></div>
            <div class="form-group"><label>Lugar Comunión</label><input type="text" name="lugar_comunion"></div>
            <div class="form-group"><label>Nombre Padre</label><input type="text" name="nombre_padre"></div>
            <div class="form-group"><label>Nombre Madre</label><input type="text" name="nombre_madre"></div>
            <div class="form-group"><label>Padrino</label><input type="text" name="padrino"></div>
            <div class="form-group"><label>Madrina</label><input type="text" name="madrina"></div>
            <div class="form-group"><label>Ministro (Párroco)</label><input type="text" name="nombre_cura" list="priests-list"></div>
            <div class="form-group"><label>Doy Fe (Párroco)</label><input type="text" name="da_fe" list="priests-list"></div>
            <div class="form-group full-width"><label>Nota al Margen</label><textarea name="nota_al_margen" rows="3"></textarea></div>
        `;
    } else if (['personas', 'sacerdotes'].includes(s)) {
        html = `
            <div class="form-group"><label>Nombres</label><input type="text" name="nombres" required></div>
            <div class="form-group"><label>Apellidos</label><input type="text" name="apellidos" required></div>
            <div class="form-group"><label>Teléfono</label><input type="text" name="telefono"></div>
            <div class="form-group"><label>Email</label><input type="email" name="email"></div>
        `;
    } else if (s === 'aportes') {
        html = `
            <div class="form-group"><label>Feligrés</label><input type="text" name="persona_nombre" list="personas-list"></div>
            <div class="form-group"><label>Monto</label><input type="number" name="monto" required min="0"></div>
            <div class="form-group"><label>Tipo</label><select name="tipo"><option>Diezmo</option><option>Ofrenda</option><option>Donación</option><option>Otro</option></select></div>
            <div class="form-group"><label>Fecha</label><input type="date" name="fecha" value="${new Date().toISOString().split('T')[0]}"></div>
            <div class="form-group full-width"><label>Descripción</label><textarea name="descripcion" rows="2"></textarea></div>
        `;
    } else {
        // Fallback or simple groups
        html = `
            <div class="form-group full-width"><label>Nombre</label><input type="text" name="nombre" required></div>
            <div class="form-group full-width"><label>Descripción</label><textarea name="descripcion"></textarea></div>
        `;
    }
    
    fields.innerHTML = html;
    panel.classList.add('open');
    initSelectors();
}

function closePanel() {
    document.getElementById('side-panel')?.classList.remove('open');
    document.getElementById('record-form')?.reset();
}

async function saveRecord(e) {
    e.preventDefault();
    const btn = e.target.querySelector('.btn-save');
    const oldText = btn.innerText;
    btn.disabled = true;
    btn.innerText = 'Guardando...';

    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const config = sectionConfig[currentSection];

    try {
        const response = await authFetch(`${API_BASE}${config.endpoint}`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showToast("Guardado con éxito", "success");
            closePanel();
            loadRecords();
            loadDashboardStats();
        } else {
            showToast("Error al guardar registro", "error");
        }
    } catch (error) {
        showToast("Error de conexión", "error");
    } finally {
        btn.disabled = false;
        btn.innerText = oldText;
    }
}

async function initSelectors() {
    try {
        // Only load if needed
        const loadDatalist = async (endpoint, listId, formatter) => {
            const res = await authFetch(`${API_BASE}${endpoint}?limit=50`);
            const data = await res.json();
            const list = document.getElementById(listId) || createDatalist(listId);
            list.innerHTML = (data.records || data).map(formatter).join('');
        };

        if (document.querySelector('[list="priests-list"]')) {
            await loadDatalist('/parroquia/sacerdotes/', 'priests-list', p => `<option value="${p.nombres} ${p.apellidos}">`);
        }
        if (document.querySelector('[list="personas-list"]')) {
            await loadDatalist('/parroquia/personas/', 'personas-list', p => `<option value="${p.nombres} ${p.apellidos}">`);
        }
    } catch (e) {}
}

function createDatalist(id) {
    const dl = document.createElement('datalist');
    dl.id = id;
    document.body.appendChild(dl);
    return dl;
}

// Balance and Charts Optimization
async function loadBalance() {
    try {
        const res = await authFetch(`${API_BASE}/parroquia/aportes/balance?_=${Date.now()}`);
        const data = await res.json();
        const cardContainer = document.getElementById('balance-cards');
        
        if (cardContainer) {
            if (data && data.length > 0) {
                const total = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' }).format(data[0].total);
                cardContainer.innerHTML = `<div class="balance-badge">Último Mes: <strong>${total}</strong></div>`;
            } else {
                cardContainer.innerHTML = '<div class="muted">Sin datos</div>';
            }
        }
        renderChart(data);
    } catch (e) {
        console.error("Balance Error:", e);
    }
}

function renderChart(data) {
    const canvas = document.getElementById('aportesChart');
    if (!canvas || !window.Chart) return;
    
    if (aportesChart) {
        aportesChart.destroy();
    }
    
    if (!data || data.length === 0) return;
    
    const labels = data.map(d => d.mes).reverse();
    const values = data.map(d => d.total).reverse();
    
    aportesChart = new Chart(canvas.getContext('2d'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ingresos Mensuales',
                data: values,
                backgroundColor: 'rgba(13, 110, 78, 0.7)',
                borderColor: '#0d6e4e',
                borderWidth: 1,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { 
                y: { beginAtZero: true, ticks: { callback: v => '$' + v.toLocaleString() } } 
            },
            plugins: { legend: { display: false } }
        }
    });
}

// --- Respaldo de Base de Datos ---
async function performBackup() {
    if (window.electronAPI && window.electronAPI.selectFolder) {
        try {
            const folderPath = await window.electronAPI.selectFolder();
            if (!folderPath) {
                return; // El usuario canceló la selección de carpeta
            }
            
            showLoading("Creando respaldo en proceso...");
            
            // Llamar al backend para hacer la copia
            const response = await fetch(`${API_BASE}/parroquia/db/backup?destination_dir=${encodeURIComponent(folderPath)}`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            
            const data = await response.json();
            hideLoading();
            
            if (response.ok) {
                showSuccessMessage("¡Respaldo exitoso! Archivo guardado en: " + folderPath);
            } else {
                showErrorMessage("Error: " + (data.detail || "No se pudo crear el respaldo"));
            }
        } catch (error) {
            console.error(error);
            hideLoading();
            showErrorMessage("Error de conexión al intentar crear el respaldo.");
        }
    } else {
        alert("Esta función solo está disponible instalando la aplicación de escritorio.");
    }
}
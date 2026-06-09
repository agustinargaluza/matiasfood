/**
 * perfil.js — compartido por index.html, matias.html y dashboard.html
 * Maneja foto de perfil y nombre en localStorage
 */

const PERFIL_KEY = 'ruta_perfil';

function getPerfil() {
  try { return JSON.parse(localStorage.getItem(PERFIL_KEY)) || null; }
  catch { return null; }
}

function setPerfil(data) {
  localStorage.setItem(PERFIL_KEY, JSON.stringify(data));
}

/** Inyecta el avatar en todos los elementos .avatar-btn de la página */
function aplicarAvatar() {
  const perfil = getPerfil();
  document.querySelectorAll('.avatar-btn').forEach(el => {
    if (perfil?.foto) {
      el.innerHTML = `<img src="${perfil.foto}" alt="Perfil"
        style="width:100%;height:100%;object-fit:cover;border-radius:50%;">`;
    } else if (perfil?.nombre) {
      const iniciales = perfil.nombre.trim().split(' ')
        .map(w => w[0]).slice(0, 2).join('').toUpperCase();
      el.innerHTML = `<span style="font-size:12px;font-weight:700;color:#fff;">${iniciales}</span>`;
      el.style.background = '#22C55E';
    }
  });
}

/** Abre el modal de perfil */
function abrirModalPerfil() {
  document.getElementById('modal-perfil')?.remove();

  const perfil = getPerfil();
  const modal = document.createElement('div');
  modal.id = 'modal-perfil';
  modal.innerHTML = `
    <div id="modal-overlay" style="
      position:fixed;inset:0;background:rgba(0,0,0,0.6);
      z-index:1000;display:flex;align-items:center;justify-content:center;
      padding:20px;">
      <div style="
        background:#fff;border-radius:20px;padding:28px 24px;
        width:100%;max-width:360px;font-family:'Inter',sans-serif;">

        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
          <h2 style="font-size:17px;font-weight:700;color:#0F172A;">Mi perfil</h2>
          <button onclick="document.getElementById('modal-perfil').remove()"
            style="border:none;background:none;font-size:20px;cursor:pointer;color:#94A3B8;">✕</button>
        </div>

        <!-- Preview foto -->
        <div style="display:flex;flex-direction:column;align-items:center;gap:12px;margin-bottom:20px;">
          <div id="preview-avatar" style="
            width:80px;height:80px;border-radius:50%;
            background:#E2E8F0;display:flex;align-items:center;
            justify-content:center;overflow:hidden;font-size:32px;
            border:3px solid #22C55E;">
            ${perfil?.foto
              ? `<img src="${perfil.foto}" style="width:100%;height:100%;object-fit:cover;">`
              : perfil?.nombre
                ? `<span style="font-size:22px;font-weight:700;color:#fff;background:#22C55E;width:100%;height:100%;display:flex;align-items:center;justify-content:center;">
                    ${perfil.nombre.trim().split(' ').map(w=>w[0]).slice(0,2).join('').toUpperCase()}
                   </span>`
                : '🧑'}
          </div>
          <label style="
            background:#F0FDF4;border:1.5px dashed #22C55E;
            border-radius:10px;padding:8px 16px;font-size:13px;
            font-weight:500;color:#16A34A;cursor:pointer;">
            📷 Subir foto
            <input type="file" accept="image/*" id="input-foto"
              style="display:none;" onchange="previsualizarFoto(this)">
          </label>
        </div>

        <!-- Nombre -->
        <div style="margin-bottom:16px;">
          <label style="font-size:12px;font-weight:500;color:#64748B;display:block;margin-bottom:6px;">
            Nombre
          </label>
          <input id="input-nombre" type="text" value="${perfil?.nombre || ''}"
            placeholder="Ej. Matías Rodríguez"
            style="width:100%;border:1.5px solid #E2E8F0;border-radius:10px;
              padding:10px 14px;font-size:14px;font-family:'Inter',sans-serif;
              outline:none;color:#0F172A;"
            onfocus="this.style.borderColor='#22C55E'"
            onblur="this.style.borderColor='#E2E8F0'">
        </div>

        <!-- Botón guardar -->
        <button onclick="guardarPerfil()" style="
          width:100%;background:#22C55E;color:#fff;border:none;
          border-radius:12px;padding:13px;font-size:14px;font-weight:600;
          font-family:'Inter',sans-serif;cursor:pointer;">
          Guardar cambios
        </button>

        ${perfil ? `
        <button onclick="eliminarPerfil()" style="
          width:100%;background:none;border:none;margin-top:10px;
          font-size:12px;color:#EF4444;cursor:pointer;font-family:'Inter',sans-serif;">
          Eliminar foto de perfil
        </button>` : ''}
      </div>
    </div>`;

  document.body.appendChild(modal);
  // Cerrar al hacer clic en overlay
  document.getElementById('modal-overlay').addEventListener('click', e => {
    if (e.target === document.getElementById('modal-overlay'))
      modal.remove();
  });
}

function previsualizarFoto(input) {
  const file = input.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = e => {
    document.getElementById('preview-avatar').innerHTML =
      `<img src="${e.target.result}" style="width:100%;height:100%;object-fit:cover;">`;
    // Guardar temporalmente
    window._fotoTemporal = e.target.result;
  };
  reader.readAsDataURL(file);
}

function guardarPerfil() {
  const nombre = document.getElementById('input-nombre').value.trim();
  const foto   = window._fotoTemporal || getPerfil()?.foto || null;
  if (!nombre && !foto) {
    alert('Ingresa al menos tu nombre.');
    return;
  }
  setPerfil({ nombre, foto });
  window._fotoTemporal = null;
  document.getElementById('modal-perfil').remove();
  aplicarAvatar();
}

function eliminarPerfil() {
  localStorage.removeItem(PERFIL_KEY);
  window._fotoTemporal = null;
  document.getElementById('modal-perfil').remove();
  aplicarAvatar();
}

/** Si es primera vez, muestra el modal automáticamente */
function iniciarPerfil(esPrimerUso = false) {
  aplicarAvatar();
  if (esPrimerUso && !getPerfil()) {
    setTimeout(abrirModalPerfil, 600);
  }
}

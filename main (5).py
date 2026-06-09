"""
Mati on the Way! — Backend
Caso 06: Rutas Enredadas
Ejecutar: uvicorn main:app --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3, os
from datetime import datetime

app = FastAPI(title="Mati on the Way! API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
DB_PATH       = os.path.join(BASE_DIR, "db", "ruta.db")
FRONTEND_PATH = BASE_DIR  # HTML files live next to main.py

# ── Base de datos ─────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    cur  = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS zonas (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre     TEXT NOT NULL,
        descripcion TEXT,
        color_hex  TEXT DEFAULT '#22C55E'
    );
    CREATE TABLE IF NOT EXISTS clientes (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo  TEXT NOT NULL,
        telefono         TEXT,
        direccion_defecto TEXT,
        zona_id          INTEGER REFERENCES zonas(id),
        creado_en        DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS menus (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre     TEXT NOT NULL,
        descripcion TEXT,
        precio     INTEGER NOT NULL,
        disponible INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS pedidos (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id       INTEGER REFERENCES clientes(id),
        menu_id          INTEGER REFERENCES menus(id),
        zona_id          INTEGER REFERENCES zonas(id),
        direccion_entrega TEXT NOT NULL,
        notas            TEXT,
        estado           TEXT DEFAULT 'pendiente',
        orden_ruta       INTEGER,
        fecha_pedido     DATETIME DEFAULT CURRENT_TIMESTAMP,
        fecha_entrega    DATETIME
    );
    """)

    if not cur.execute("SELECT 1 FROM zonas LIMIT 1").fetchone():
        cur.executemany("INSERT INTO zonas (nombre, descripcion, color_hex) VALUES (?,?,?)", [
            ('Zona A - Centro La Serena', 'Centro histórico y Av. del Mar', '#22C55E'),
            ('Zona B - Coquimbo',         'Puerto y sector costero',        '#3B82F6'),
            ('Zona C - Las Compañías',    'Sector norte La Serena',         '#8B5CF6'),
        ])
        cur.executemany("INSERT INTO menus (nombre, descripcion, precio) VALUES (?,?,?)", [
            ('Menú del día',       'Plato del día + ensalada + bebida',             5500),
            ('Hamburguesa Clásica','Carne de res, lechuga, tomate, cheddar',        8990),
            ('Hamburguesa BBQ',    'Doble carne, bacon, salsa BBQ, cebolla',        8990),
            ('Hamburguesa Vegana', 'Medallón de legumbres, palta, tomate, mostaza', 8990),
            ('Completo Italiano',  'Palta, tomate, mayonesa, mostaza',              2990),
            ('Completo Vegano',    'Sin salchicha, palta, tomate, mayo vegana',     2990),
        ])
        cur.executemany(
            "INSERT INTO clientes (nombre_completo, telefono, direccion_defecto, zona_id) VALUES (?,?,?,?)", [
            ('Alejandro Ramos', '+56912345601', 'Av. Francisco de Aguirre 485, La Serena', 1),
            ('Sofía Méndez',    '+56912345602', 'Calle Balmaceda 320, La Serena',          1),
            ('Carlos Martínez', '+56912345603', 'Av. Costanera 950, Coquimbo',             2),
            ('Marina López',    '+56912345604', 'Calle Los Aromos 234, Las Compañías',     3),
            ('Juan Torres',     '+56912345605', 'Av. del Mar 1200, La Serena',             1),
        ])
        cur.executemany(
            "INSERT INTO pedidos (cliente_id, menu_id, zona_id, direccion_entrega, notas, estado, orden_ruta) VALUES (?,?,?,?,?,?,?)", [
            (1, 1, 1, 'Av. Francisco de Aguirre 485, La Serena', '1x Menú del día',       'entregado', 1),
            (2, 2, 1, 'Calle Balmaceda 320, La Serena',          '1x Hamburguesa Clásica','entregado', 2),
            (5, 1, 1, 'Av. del Mar 1200, La Serena',             '1x Menú del día',       'en_ruta',   3),
            (3, 5, 2, 'Av. Costanera 950, Coquimbo',             '2x Completo Italiano',  'pendiente', 4),
            (4, 3, 3, 'Calle Los Aromos 234, Las Compañías',     '1x Hamburguesa BBQ',    'pendiente', 5),
        ])

    conn.commit()
    conn.close()

init_db()

# ── Modelos ───────────────────────────────────────────────────

class PedidoCreate(BaseModel):
    nombre_completo:   str
    direccion_entrega: str
    menu_id:           int
    telefono:          Optional[str] = None
    notas:             Optional[str] = None

# ── Helpers ───────────────────────────────────────────────────

def detectar_zona(direccion: str) -> int:
    addr = direccion.lower()
    if any(w in addr for w in ['coquimbo', 'costanera', 'aldunate', 'borgoño', 'puerto']):
        return 2
    if any(w in addr for w in ['compañías', 'companias', 'aromos', 'flores']):
        return 3
    return 1

def serve_html(filename: str):
    path = os.path.join(FRONTEND_PATH, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type="text/html")
    return JSONResponse({"error": f"{filename} no encontrado"}, status_code=404)

# ── Páginas frontend ──────────────────────────────────────────

@app.get("/")
def index():
    return serve_html("index.html")

@app.get("/matias")
def matias():
    return serve_html("matias.html")

@app.get("/dashboard")
def dashboard_page():
    return serve_html("dashboard.html")

# ── API ───────────────────────────────────────────────────────

@app.get("/api")
def api_status():
    return {"mensaje": "Mati on the Way! API funcionando", "version": "2.0.0"}

@app.get("/menus")
def listar_menus():
    conn  = get_db()
    menus = conn.execute("SELECT * FROM menus WHERE disponible=1").fetchall()
    conn.close()
    return [dict(m) for m in menus]

@app.post("/pedidos", status_code=201)
def crear_pedido(pedido: PedidoCreate):
    conn    = get_db()
    cur     = conn.cursor()
    zona_id = detectar_zona(pedido.direccion_entrega)

    cliente = cur.execute(
        "SELECT id FROM clientes WHERE nombre_completo=?",
        (pedido.nombre_completo,)
    ).fetchone()

    if cliente:
        cliente_id = cliente["id"]
        if pedido.telefono:
            cur.execute("UPDATE clientes SET telefono=? WHERE id=?",
                        (pedido.telefono, cliente_id))
    else:
        cur.execute(
            "INSERT INTO clientes (nombre_completo, telefono, direccion_defecto, zona_id) VALUES (?,?,?,?)",
            (pedido.nombre_completo, pedido.telefono, pedido.direccion_entrega, zona_id)
        )
        cliente_id = cur.lastrowid

    max_orden = cur.execute(
        "SELECT COALESCE(MAX(orden_ruta), 0) FROM pedidos WHERE zona_id=? AND date(fecha_pedido)=date('now')",
        (zona_id,)
    ).fetchone()[0]

    cur.execute(
        """INSERT INTO pedidos
           (cliente_id, menu_id, zona_id, direccion_entrega, notas, estado, orden_ruta)
           VALUES (?,?,?,?,?,'pendiente',?)""",
        (cliente_id, pedido.menu_id, zona_id,
         pedido.direccion_entrega, pedido.notas, max_orden + 1)
    )
    nuevo_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"id": nuevo_id, "zona_id": zona_id, "mensaje": "Pedido creado"}

@app.get("/pedidos/hoy")
def pedidos_hoy():
    """Retorna solo pedidos pendientes y en ruta del día de hoy."""
    conn    = get_db()
    pedidos = conn.execute("""
        SELECT p.id,
               c.nombre_completo AS cliente,
               p.direccion_entrega AS direccion,
               c.telefono,
               p.zona_id, p.estado, p.orden_ruta,
               m.nombre AS menu, p.notas
        FROM   pedidos p
        JOIN   clientes c ON c.id = p.cliente_id
        JOIN   menus m    ON m.id = p.menu_id
        WHERE  date(p.fecha_pedido) = date('now')
          AND  p.estado IN ('pendiente', 'en_ruta')
        ORDER  BY p.zona_id, p.orden_ruta
    """).fetchall()
    conn.close()
    return [dict(p) for p in pedidos]

@app.get("/pedidos/historial")
def pedidos_historial():
    """Retorna pedidos entregados del día para el dashboard."""
    conn    = get_db()
    pedidos = conn.execute("""
        SELECT p.id,
               c.nombre_completo AS cliente,
               p.direccion_entrega AS direccion,
               p.zona_id, p.estado,
               m.nombre AS menu, p.notas,
               p.fecha_pedido, p.fecha_entrega
        FROM   pedidos p
        JOIN   clientes c ON c.id = p.cliente_id
        JOIN   menus m    ON m.id = p.menu_id
        WHERE  date(p.fecha_pedido) = date('now')
          AND  p.estado = 'entregado'
        ORDER  BY p.fecha_entrega DESC
    """).fetchall()
    conn.close()
    return [dict(p) for p in pedidos]

@app.patch("/pedidos/{pedido_id}/entregar")
def marcar_entregado(pedido_id: int):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE pedidos SET estado='entregado', fecha_entrega=datetime('now') WHERE id=?",
        (pedido_id,)
    )
    if cur.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    conn.commit()
    conn.close()
    return {"mensaje": f"Pedido {pedido_id} entregado"}

@app.get("/dashboard/hoy")
def dashboard_hoy():
    """KPIs del día para el dashboard — nunca falla."""
    try:
        conn = get_db()
        cur  = conn.cursor()

        total      = cur.execute("SELECT COUNT(*) FROM pedidos WHERE date(fecha_pedido)=date('now')").fetchone()[0]
        entregados = cur.execute("SELECT COUNT(*) FROM pedidos WHERE date(fecha_pedido)=date('now') AND estado='entregado'").fetchone()[0]
        pendientes = total - entregados

        por_zona = cur.execute("""
            SELECT z.nombre, COUNT(p.id) AS total
            FROM   pedidos p
            JOIN   zonas z ON z.id = p.zona_id
            WHERE  date(p.fecha_pedido) = date('now')
            GROUP  BY p.zona_id
            ORDER  BY total DESC
        """).fetchall()

        por_hora = cur.execute("""
            SELECT strftime('%H', fecha_pedido) AS hora, COUNT(*) AS total
            FROM   pedidos
            WHERE  date(fecha_pedido) >= date('now', '-7 days')
            GROUP  BY hora
            ORDER  BY hora
        """).fetchall()

        por_semana = cur.execute("""
            SELECT strftime('%w', fecha_pedido) AS dia, COUNT(*) AS total
            FROM   pedidos
            WHERE  date(fecha_pedido) >= date('now', '-7 days')
            GROUP  BY dia
            ORDER  BY dia
        """).fetchall()

        ventas = cur.execute("""
            SELECT COALESCE(SUM(m.precio), 0)
            FROM   pedidos p
            JOIN   menus m ON m.id = p.menu_id
            WHERE  date(p.fecha_pedido) = date('now')
        """).fetchone()[0]

        conn.close()
        return {
            "total":      total,
            "entregados": entregados,
            "pendientes": pendientes,
            "ventas":     ventas,
            "por_zona":   [dict(r) for r in por_zona],
            "por_hora":   [dict(r) for r in por_hora],
            "por_semana": [dict(r) for r in por_semana],
        }
    except Exception as e:
        # Nunca devolver 500 — retornar datos vacíos con el error
        return {
            "total": 0, "entregados": 0, "pendientes": 0, "ventas": 0,
            "por_zona": [], "por_hora": [], "por_semana": [],
            "error": str(e)
        }

@app.get("/zonas")
def listar_zonas():
    conn  = get_db()
    zonas = conn.execute("SELECT * FROM zonas").fetchall()
    conn.close()
    return [dict(z) for z in zonas]

# Bitácora de Prompts — Mati on the Way!
**Proyecto:** Desarrollo de Soluciones Tecnológicas Asistidas por IA  
**Caso:** 06 — Rutas Enredadas  
**Herramienta IA:** Claude (Anthropic) — claude.ai  
**Asignatura:** Sistemas de Información — Ingeniería Comercial UCN 2026  

---

## ¿Qué es esta Bitácora?

Este documento registra las conversaciones clave y los prompts más efectivos utilizados durante el desarrollo de **Mati on the Way!** con Claude como asistente de pair-programming. Incluye tanto los prompts exitosos como los iterativos (los que requirieron corrección), evidenciando el proceso real de trabajo con IA generativa.

---

## Fase 1: Diseño Inicial y Estructura del Sistema

### Prompt 1 — Definición del Stack y Arquitectura
**Contexto:** Inicio del proyecto, necesitábamos decidir qué tecnologías usar.

**Prompt usado:**
```
Tenemos el Caso 06 "Rutas Enredadas" de Sistemas de Información UCN.
Matías reparte almuerzos en bicicleta, 30-50 pedidos diarios, 
organiza todo con papelitos. Necesitamos una app web completa.
¿Qué stack nos recomiendas y por qué?
```

**Respuesta clave de Claude:**
> Recomiendo HTML + CSS + JS vanilla para el frontend (sin compiladores, deploy instantáneo en GitHub Pages), Python + FastAPI para el backend (desarrollo rápido de APIs REST), y SQLite como base de datos (sin configuración adicional, ideal para negocio unipersonal). Deploy en Render para el backend y GitHub Pages para el frontend.

**Por qué fue efectivo:** El prompt incluyó el contexto del negocio (volumen de pedidos, tipo de operación), lo que permitió a Claude justificar cada tecnología según las necesidades reales del caso.

---

### Prompt 2 — Creación del Schema de Base de Datos
**Contexto:** Necesitábamos definir las tablas antes de desarrollar el backend.

**Prompt usado:**
```
Basado en el Caso 06, diseña el schema SQL para la base de datos.
Necesitamos manejar: clientes, pedidos, zonas de entrega y menús.
Usa SQLite. Incluye datos de prueba (DML).
```

**Resultado:** Claude generó las 4 tablas principales (zonas, clientes, menus, pedidos) con sus relaciones y datos semilla, incluyendo el campo `orden_ruta` para optimización de entregas y el campo `estado` con el flujo pendiente → en_ruta → entregado.

---

## Fase 2: Desarrollo del Frontend

### Prompt 3 — Portal de Pedidos (index.html)
**Contexto:** Primera versión del portal para clientes.

**Prompt usado:**
```
Crea index.html para la app "Mati on the Way!". 
Stack: HTML + CSS + JS vanilla. Necesita:
- Formulario de pedido (nombre, teléfono, dirección)
- Menú con hamburguesas ($8.990), completos ($2.990) y bebidas ($1.990)
- Sistema de puntos llamado "Matipuntos" (1 punto por $1.000)
- Diseño mobile-first, máx 420px de ancho
- Conectar con backend en matiasfood.onrender.com
```

**Por qué fue efectivo:** El prompt especificó precios exactos, nombre del sistema de puntos y URL del backend. Los detalles específicos evitan que Claude invente valores que luego hay que corregir.

---

### Prompt 4 — Corrección de Fotos Incorrectas (Iteración)
**Contexto:** Las fotos de Pexels no correspondían a los productos. El Sprite mostraba una Pepsi, el Agua mostraba un batido verde, el Red Bull mostraba un toro emoji.

**Evidencia del problema (captura enviada):**
> Completo Italiano → sushi/mariscos ❌  
> Agua mineral → batido verde ❌  
> Sprite → botella Coca-Cola ❌  
> Red Bull → lata Pepsi ❌

**Prompt inicial (no efectivo):**
```
Las fotos están mal, corrígelas
```

**Prompt mejorado (efectivo):**
```
Las fotos de los productos están incorrectas. Te mando captura.
Completo Italiano muestra sushi, Agua muestra batido verde,
Sprite muestra Coca-Cola, Red Bull muestra Pepsi.
Necesito IDs de Pexels que correspondan a cada producto real.
```

**Lección aprendida:** Describir el problema específico con evidencia visual acelera la solución. "No funciona" es mucho menos efectivo que "muestra X cuando debería mostrar Y".

**Solución final:** Las fotos fueron subidas directamente al repositorio GitHub (carpeta `/img`) para evitar bloqueos de CORS de CDNs externos.

---

### Prompt 5 — App del Repartidor con Mapa (matias.html)
**Prompt usado:**
```
Crea matias.html para el repartidor. Necesita:
- Mapa con Leaflet + OpenStreetMap (sin API key)
- Pedidos agrupados por zona (Zona A La Serena, Zona B Coquimbo, Zona C Las Compañías)
- Geocodificación automática con Nominatim
- Botón llamar al cliente (href tel:)
- Botón "Entregado" que actualiza el backend
- PATCH /pedidos/{id}/entregar
- Diseño mobile-first
```

**Por qué fue efectivo:** Se especificó el proveedor de mapas (evitar API keys de pago), las zonas geográficas reales del caso y el endpoint exacto del backend.

---

### Prompt 6 — Corrección Bug del Mapa (Iteración)
**Contexto:** El mapa no se veía en producción, aparecía cortado.

**Prompt inicial (no efectivo):**
```
El mapa no se ve
```

**Prompt mejorado (efectivo):**
```
El mapa Leaflet aparece cortado en la mitad en Render.
El problema parece ser el overflow:hidden del div .card padre.
El mapa necesita invalidateSize() después de renderizarse.
```

**Solución:** Claude agregó `mapa.invalidateSize()` con `setTimeout` de 400ms y removió `overflow:hidden` del contenedor padre.

**Lección:** Incluir la causa probable del error en el prompt evita que Claude busque soluciones en la dirección equivocada.

---

## Fase 3: Dashboard y Analíticas

### Prompt 7 — Dashboard con Datos Reales (dashboard.html)
**Contexto:** El dashboard mostraba datos hardcodeados (Alejandro Ramos, Sofía Méndez, etc.) en lugar de los datos reales del backend.

**Prompt usado:**
```
El dashboard muestra datos demo hardcodeados:
pedidosDemoHoy con nombres falsos como "Alejandro Ramos".
Necesito que use datos reales del backend.
Endpoints disponibles:
- GET /pedidos/hoy (pendientes y en_ruta)
- GET /pedidos/historial (entregados del día)
- GET /dashboard/hoy (KPIs)
Eliminar COMPLETAMENTE pedidosDemoHoy del código.
Si el backend no responde, mostrar "⏳ Conectando..." no datos falsos.
```

**Por qué fue efectivo:** Se especificó exactamente qué eliminar, los endpoints disponibles y el comportamiento esperado cuando el backend falla. La instrucción "COMPLETAMENTE" fue clave para que Claude no dejara referencias residuales.

---

### Prompt 8 — Excel con Formato de Tabla (Iteración x3)
**Contexto:** El Excel exportado mostraba todo en columna A sin separación.

**Iteración 1 (no efectiva):**
```
El Excel no queda bien, arréglalo
```

**Iteración 2 (parcialmente efectiva):**
```
El Excel usa \t como separador pero Excel Chile usa ;
Cambia a punto y coma
```
*Resultado: Las columnas se separaron pero sin formato visual*

**Iteración 3 (efectiva):**
```
El Excel necesita formato de tabla real, no CSV.
Usa HTML table con estilos inline que Excel pueda interpretar.
Columnas: N°, Cliente, Pedido, Precio Venta, Costo Est., 
Ganancia Neta, Estado. Cabeceras en negro (#0F172A) texto blanco.
Filas alternadas. Al final tabla de resumen con ventas totales,
costos, ganancia neta y margen %.
Tipo MIME: application/vnd.ms-excel
```

**Lección:** Algunos problemas requieren cambiar el enfoque completo (de CSV a HTML table), no solo ajustar parámetros.

---

### Prompt 9 — Analíticas Mensuales
**Prompt usado:**
```
Agregar al dashboard:
1. Resumen mensual bajo el calendario con 4 KPIs:
   pedidos del mes, ventas totales, eficiencia promedio, días trabajados
2. Botón "Exportar mes completo a Excel" con tabla por día:
   Fecha, Pedidos, Ventas, Promedio/pedido, Costos Est., Ganancia Neta, Eficiencia
3. El resumen debe actualizarse al navegar entre meses con las flechas
```

**Por qué fue efectivo:** Se especificaron los 4 KPIs exactos, las columnas del Excel mensual y el comportamiento de actualización. Sin esa especificidad, Claude habría inventado métricas diferentes.

---

## Fase 4: Funcionalidades Avanzadas

### Prompt 10 — GPS en Tiempo Real
**Prompt usado:**
```
Agregar GPS en tiempo real a matias.html:
- Botón toggle "📍 GPS" arriba del mapa
- Al activar: marcador 🚲 con posición real de Matías usando watchPosition()
- Badge que cambia a "GPS activo" en verde cuando está on
- Al desactivar: remover marcador del mapa
- BUG CRÍTICO a evitar: guardar referencia const ref = markerGPS
  ANTES de hacer markerGPS = null, para que el filter funcione correctamente
```

**Por qué fue efectivo:** Se anticipó el bug conocido de la referencia nula y se incluyó en el prompt. Esto evitó que Claude repitiera el mismo error.

---

### Prompt 11 — Notificaciones de Pedidos Nuevos
**Prompt usado:**
```
Agregar a matias.html notificaciones cuando llegan pedidos nuevos:
- Polling cada 30 segundos a GET /pedidos/hoy
- Si hay más pedidos que antes: mostrar banner "🔔 X pedidos nuevos"
- Vibración del teléfono: navigator.vibrate([200,100,200])
- Notificación nativa del sistema operativo si el usuario dio permiso
- Pedir permiso al cargar la página con Notification.requestPermission()
- Recargar lista de pedidos automáticamente
```

---

### Prompt 12 — Verificación Automática de Código
**Contexto:** Después de varios bugs que pasaron desapercibidos, se implementó verificación sistemática.

**Prompt usado:**
```
Antes de entregarme el archivo, ejecuta un script Python que verifique:
- Que no exista pedidosDemoHoy en el código
- Que no haya nombres hardcodeados como "Alejandro Ramos"
- Que cada función crítica aparezca exactamente 1 vez (no duplicada)
- Que existan todos los endpoints del backend
- Que la sintaxis Python sea válida
Muéstrame el resultado antes de darme el archivo.
```

**Por qué fue efectivo:** Esta estrategia de verificación automática detectó funciones duplicadas, datos demo residuales y bugs de lógica que habrían sido difíciles de encontrar manualmente. Se convirtió en práctica estándar para cada entrega.

---

## Estrategias de Prompting Identificadas

| Estrategia | Descripción | Efectividad |
|---|---|---|
| **Contexto completo** | Siempre incluir nombre de la app, stack y URL de producción | ⭐⭐⭐⭐⭐ |
| **Evidencia visual** | Enviar capturas de pantalla de los problemas | ⭐⭐⭐⭐⭐ |
| **Especificar qué eliminar** | "Elimina COMPLETAMENTE X" en vez de "arréglalo" | ⭐⭐⭐⭐⭐ |
| **Verificación automática** | Pedir script de check antes de recibir el archivo | ⭐⭐⭐⭐⭐ |
| **Anticipar bugs conocidos** | Incluir en el prompt los bugs a evitar | ⭐⭐⭐⭐ |
| **Iteración incremental** | Funcionalidad básica → estilo → backend → bugs | ⭐⭐⭐⭐ |
| **Comportamiento en falla** | Especificar qué mostrar si el backend no responde | ⭐⭐⭐⭐ |
| **Cambiar enfoque** | Si una solución no funciona tras 2 intentos, cambiar estrategia completa | ⭐⭐⭐ |

---

## Estadísticas del Proceso

- **Herramienta utilizada:** Claude (Anthropic) — claude.ai
- **Total de iteraciones estimadas:** +60 intercambios
- **Archivos desarrollados:** 4 (index.html, matias.html, dashboard.html, main.py)
- **Bugs detectados y corregidos:** 12+ (mapa cortado, fotos incorrectas, datos demo, Excel mal formateado, GPS referencia nula, función duplicada, CORS, etc.)
- **Funcionalidades implementadas:** 14 requerimientos funcionales cumplidos al 100%

---

## Conclusión del Proceso

El uso de Claude como asistente de pair-programming demostró que la calidad del prompt determina directamente la calidad del resultado. Los prompts vagos ("no funciona", "arréglalo") generaron respuestas incompletas que requirieron más iteraciones. Los prompts específicos con contexto, evidencia y comportamiento esperado resolvieron los problemas en el primer o segundo intento.

La estrategia más valiosa fue la **verificación automática mediante scripts**: en lugar de confiar en la revisión visual del código, se usaron scripts Python para comprobar sistemáticamente que el código cumplía todos los requisitos antes de aceptarlo como válido.

---

*Bitácora generada como parte del entregable del proyecto — Sistemas de Información, UCN 2026*

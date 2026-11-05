# Plan de Implementación — Triage Queue

## 📋 Visión General

Sistema de gestión de cola de prioridad para triaje hospitalario en Python. El programa operará en terminal y modelará una cola de prioridad con 3 niveles de triaje, respetando orden FIFO dentro de cada nivel.

---

## 🏗️ Arquitectura del Proyecto

```
triage-queue/
├── triage_queue.py          # Punto de entrada (CLI interactiva)
├── queue/
│   ├── __init__.py
│   ├── patient.py           # Clase Patient (datos del paciente)
│   ├── triage_queue.py      # Clase TriageQueue (lógica de la cola)
│   └── priority_queue.py    # Clase PriorityQueue (estructura interna)
└── tests/
    ├── __init__.py
    ├── test_patient.py
    ├── test_triage_queue.py
    └── test_priority_queue.py
```

---

## 🧱 Fase 1 — Modelo de Datos

### 1.1 Clase `Patient`

- **Atributos:**
  - `name: str` — nombre del paciente
  - `triage_level: int` — nivel (1, 2 o 3)
  - `arrival_time: datetime` — timestamp de llegada
  - `id: int` — identificador único auto-incremental (para desempate FIFO)
- **Métodos:**
  - `__init__(self, name, triage_level)`
  - `__repr__(self)` / `__str__(self)` — representación legible

### 1.2 Clase `PriorityQueue`

Estructura interna que gestiona las colas por nivel.

- **Estructura interna:** 3 listas/colas internas (`self._queues = {1: deque(), 2: deque(), 3: deque()}`)
  - Usamos `collections.deque` para operaciones eficientes O(1) en inserción por la derecha y extracción por la izquierda.
- **Métodos:**
  - `enqueue(patient)` — inserta en la cola correspondiente según `triage_level`
  - `dequeue()` — extrae de la cola de nivel más prioritario no vacía
  - `peek()` — consulta el siguiente paciente sin extraerlo
  - `is_empty()` — ¿cola vacía?
  - `list_all()` — devuelve lista plana ordenada [nivel 1 → nivel 2 → nivel 3], y dentro de cada nivel FIFO
  - `stats()` — dict con conteo por nivel y total
  - `size()` — número total de pacientes

---

## 🧠 Fase 2 — Lógica de Negocio (TriageQueue)

### 2.1 Clase `TriageQueue`

Capa de servicio que orquesta las operaciones.

- **Atributos:**
  - `_priority_queue: PriorityQueue`
  - `_counter: int` — contador auto-incremental para IDs
- **Métodos (operaciones requeridas):**
  - `add_patient(name, triage_level) -> Patient` — encolar nuevo paciente
  - `call_next() -> Patient | None` — desencolar (llamar al siguiente)
  - `next_patient() -> Patient | None` — peek
  - `list_queue() -> list[Patient]` — listar cola ordenada
  - `get_stats() -> dict` — estadísticas

### 2.2 Validaciones

- `triage_level` debe ser 1, 2 o 3 (lanzar `ValueError` si no)
- `name` no puede ser vacío
- No se puede desencolar si la cola está vacía (manejar con `IndexError` o retornar `None`)

---

## 💻 Fase 3 — Interfaz de Terminal (CLI)

### 3.1 Menú interactivo

Bucle principal con las siguientes opciones:

```
===== TRIAGE QUEUE - Urgencias =====
1. Encolar paciente
2. Llamar siguiente paciente
3. Ver siguiente paciente
4. Listar cola
5. Ver estadísticas
6. Salir
======================================
Selecciona una opción:
```

### 3.2 Flujos de cada opción

| Opción | Acción | Input | Output |
|--------|--------|-------|--------|
| 1 | Encolar | nombre, nivel (1-3) | Confirmación con datos del paciente |
| 2 | Desencolar | — | "Paciente llamado: {nombre}" o "No hay pacientes" |
| 3 | Peek | — | "Siguiente: {nombre}" o "No hay pacientes" |
| 4 | Listar | — | Tabla ordenada de pacientes |
| 5 | Stats | — | Resumen por nivel |
| 6 | Salir | — | Mensaje de despedida |

### 3.3 Manejo de errores en CLI

- Capturar `KeyboardInterrupt` (Ctrl+C) para salir limpio
- Validar entrada numérica en nivel (1-3) y en selección de menú
- Re-preguntar si la entrada es inválida

---

## 🧪 Fase 4 — Tests

### 4.1 Tests unitarios (pytest)

| Archivo | Tests |
|---------|-------|
| `test_patient.py` | Creación de paciente, validación de nivel, representación string |
| `test_priority_queue.py` | Enqueue/dequeue, orden de prioridad, FIFO dentro del mismo nivel, stats, list_all, edge cases (cola vacía) |
| `test_triage_queue.py` | Integración básica, flujo completo |

### 4.2 Escenarios clave a testear

1. **Prioridad estricta:** Encolar niveles [3, 2, 1] → desencolar debe dar [1, 2, 3]
2. **FIFO dentro del mismo nivel:** Encolar 3 pacientes nivel 2 → desencolar debe respetar orden de llegada
3. **Prioridad con llegada tardía:** Encolar nivel 3, nivel 2, nivel 3, nivel 1 → orden esperado: 1, 2, 3 (el primero), 3 (el segundo)
4. **Cola vacía:** Desencolar/peek en cola vacía debe retornar None
5. **Stats después de operaciones:** Verificar conteos después de varias inserciones y extracciones
6. **Validación:** Nivel inválido (0, 4, -1, "abc") debe lanzar ValueError

---

## 📦 Fase 5 — Empaquetado (opcional pero recomendado)

### 5.1 Archivos de configuración

- `requirements.txt` — (opcional, solo `pytest` para tests)
- `setup.py` o `pyproject.toml` — para instalación del paquete
- `.gitignore` — Python estándar

---

## ✅ Criterios de aceptación

- [ ] Programa funcional en terminal con menú interactivo
- [ ] PriorityQueue implementa enqueue/dequeue/peek/list_all/stats correctamente
- [ ] Pacientes de nivel 1 siempre se atienden antes que nivel 2 y 3
- [ ] Dentro del mismo nivel se respeta orden FIFO
- [ ] Validación de datos de entrada
- [ ] Tests unitarios pasan (pytest)
- [ ] Código limpio, comentado y con type hints

---

## � Secuencia de implementación sugerida

```
Paso 1: Crear estructura de directorios y archivos vacíos
Paso 2: Implementar Patient
Paso 3: Implementar PriorityQueue
Paso 4: Implementar TriageQueue
Paso 5: Implementar CLI (menú interactivo)
Paso 6: Escribir tests
Paso 7: Ejecutar tests y corregir errores
Paso 8: Refinar y documentar
```
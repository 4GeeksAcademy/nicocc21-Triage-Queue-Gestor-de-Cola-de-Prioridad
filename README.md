# Triage Queue — Gestor de Cola de Prioridad

Sistema de gestión de cola de prioridad para triaje hospitalario en **Python** (solo biblioteca estándar). El programa corre en terminal y modela una cola de prioridad con 3 niveles de triaje, respetando el orden FIFO dentro de cada nivel.

## 🏥 Descripción

El departamento de informática de un hospital público moderniza el proceso de triaje en su unidad de urgencias. Actualmente una enfermera apunta a mano los nombres en una pizarra y llama por orden de llegada — esto genera caos cuando llega un caso crítico y hay que saltarse la cola.

Este sistema modela la cola correctamente en Python, listo para integrarse más adelante en una aplicación mayor.

## 🚑 Niveles de triaje

| Nivel | Nombre | Prioridad |
|-------|--------|-----------|
| 1 | Crítico | Alta |
| 2 | Urgente | Media |
| 3 | Estándar | Baja |

Los pacientes de nivel 1 siempre se atienden antes que los de nivel 2, y estos antes que los de nivel 3. Dentro del mismo nivel se respeta el **orden de llegada (FIFO)**.

## ⚙️ API

### `Patient` (dataclass)
- `name: str`
- `triage_level: int` (1–3)
- `arrived_at: datetime` (timestamp de llegada)
- `patient_id: int`

### `TriageQueue`

| Método | Descripción |
|--------|-------------|
| `enqueue(patient)` | Añade un paciente; la posición respeta nivel y orden de llegada |
| `dequeue()` | Extrae y devuelve el siguiente paciente; **lanza `QueueEmptyError` si la cola está vacía** |
| `peek()` | Devuelve el siguiente paciente sin extraerlo (`None` si vacía) |
| `list_queue()` | Devuelve todos los pacientes en espera, en orden de atención |
| `stats()` | Devuelve dict con pacientes en espera por nivel (`level_1`, `level_2`, `level_3`, `total`) |

## 📂 Estructura del proyecto

```
triage-queue/
├── triage_queue.py          # CLI interactiva (punto de entrada)
├── queue/
│   ├── __init__.py
│   ├── patient.py           # Dataclass Patient
│   └── triage_queue.py      # TriageQueue (3 colas FIFO internas + QueueEmptyError)
├── tests/
│   ├── __init__.py
│   ├── test_patient.py
│   └── test_triage_queue.py
├── DESIGN.md                # Notas de diseño (estructura de datos + concurrencia)
├── PLAN.md                  # Plan de implementación
└── requirements.txt         # Solo pytest (para tests)
```

## 🧠 Decisión técnica

Se usan **3 colas FIFO internas** (`collections.deque`), una por nivel de triaje. Esto permite:

- **Inserción O(1)** — siempre al final de la deque correspondiente.
- **Extracción O(1)** — siempre del frente de la deque de mayor prioridad no vacía.
- **FIFO estricto sin desempates** — cada deque es FIFO por construcción.
- **Sin reordenamiento** — un paciente crítico que llega tarde simplemente se agrega a la deque de nivel 1.

Un `deque` simple o un `heapq` (no estable) no son suficientes. Justificación completa en [`DESIGN.md`](DESIGN.md), incluyendo el escenario de concurrencia entre workers (dequeue) y enfermeras (enqueue).

## 🚀 Cómo ejecutar

```bash
# Asegurarse de ejecutar desde la raíz del proyecto (para los imports de queue/...)
cd triage-queue

# Ejecutar la CLI
python triage_queue.py
```

> Nota: los imports usan `queue/...`, por lo que debes ejecutar desde la raíz del proyecto.

## 🧪 Tests

```bash
# Instalar pytest (solo para el entorno de desarrollo)
pip install pytest

# Ejecutar tests
python -m pytest tests/ -v
```

## 📥 Menú de la CLI

```
================================================
        TRIAGE QUEUE — Gestor de Urgencias
================================================

--- MENÚ PRINCIPAL ---

  1. Añadir paciente
  2. Llamar siguiente paciente
  3. Ver siguiente paciente
  4. Ver cola actual
  5. Ver estadísticas
  6. Salir
```

## ✅ Criterios de aceptación

- [x] `TriageQueue` modela cola de prioridad: nivel 1 siempre antes que nivel 2, nivel 2 antes que nivel 3
- [x] Dentro del mismo nivel de triaje, el orden FIFO se preserva estrictamente
- [x] Las cinco operaciones (`enqueue`, `dequeue`, `peek`, `list_queue`, `stats`) implementadas
- [x] Casos borde gestionados: `dequeue()`/`peek()` sobre cola vacía no rompen el programa (error descriptivo + manejo con gracia)
- [x] Lógica organizada en clases con responsabilidades claras (sin lógica en `main()`)
- [x] Nota de diseño explica la elección de estructura con razón concreta (`DESIGN.md`)
- [x] Nota de diseño aborda la mutación concurrente (`DESIGN.md`)
- [x] Bucle de CLI funciona y no rompe ante entradas inválidas
- [x] Solo biblioteca estándar (`collections.deque`, `datetime`); sin paquetes externos en runtime

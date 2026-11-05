# Notas de Diseño — Triage Queue

## 1. Estructura de datos interna: tres colas FIFO separadas

Para modelar la cola de prioridad de triaje se eligió usar **tres colas `collections.deque` independientes**, una por nivel de triaje (1, 2 y 3), en lugar de las alternativas más comunes:

### Alternativa A — Una sola `deque` FIFO

- **Problema:** no modela prioridad en absoluto. Un paciente crítico llegando tarde tendría que esperar detrás de todos los estándar, o habría que retirarlo y reinsertarlo en la posición correcta (O(n)). Reordenar la pizarra manualmente es exactamente el caos que el hospital quiere eliminar.

### Alternativa B — Lista ordenada por prioridad

- **Problema:** la inserción en una lista ordenada es **O(n)** en el peor caso (desplazar todos los elementos), porque una lista Python almacena elementos contiguos en memoria. Con miles de pacientes en un hospital grande, cada inserción de un paciente crítico implicaría mover cientos de referencias.

### Alternativa C — `heapq` (heap binario)

- **Ventaja:** inserción y extracción O(log n).
- **Problemas:**
  - `heapq` de Python **no es estable**: dos pacientes del mismo nivel con la misma prioridad pueden salir en cualquier orden, rompiendo el requisito FIFO. Habría que añadir un campo de desempate (p. ej., el timestamp o un contador) como tercer elemento de la tupla `(nivel, orden_llegada, paciente)`.
  - Requiere **paquetear y desempaquetar** tuplas en cada operación, más indirección, más generación de objetos temporales.

### Alternativa elegida — Tres `deque` (una por nivel)

- **Inserción (enqueue):** `deque.append` → **O(1)**. El paciente se añade siempre al final de su deque correspondiente.
- **Extracción (dequeue):** `deque.popleft` → **O(1)**. Se mira 1 → 2 → 3 y se extrae de la primera deque no vacía.
- **Peek:** O(1) (acceder a `deque[0]`).
- **FIFO estricto:** sin desempates. Cada deque es FIFO por construcción; `append` por el final y `popleft` por el frente garantizan el orden de llegada sin ningún campo extra.
- **Escalado a más niveles:** si mañana el hospital añade un nivel 0 (trauma activo), el diseño solo necesita añadir otra deque. No hay reescritura de algoritmos.

Esta es la solución clásica a una *cola de prioridad con prioridades discretas y estables* (al estilo de "buckets", como en el *bucket queue* / *Radix heap*), que es exactamente nuestro caso: solo 3 prioridades bien definidas.

---

## 2. Concurrencia: controlador (worker) extrayendo vs. enfermera encolando

### Escenario

Un *worker* médica está llamando a la vez que llega un paciente crítico:

- Worker A: `dequeue()` — extrae al siguiente paciente.
- Worker B: `enqueue(crítico)` — añade un nivel 1.

Si no se controla, podría ocurrir que **dos workers extraigan el mismo paciente a la vez** (doble procesamiento), o que un paciente se "pierda" entre la comprobación de `is_empty()` y el `popleft()`.

### Cómo garantizar que no haya doble procesamiento

La regla de oro, tanto en Python (GIL) como en cualquier sistema concurrente, es **tratar las operaciones de mutación como una única unidad atómica**:

1. **Hacer del enqueue y del dequeue operaciones atómicas.** En Python, las operaciones sobre `deque` (`append`, `popleft`) ya son atómicas a nivel de intérprete gracias al GIL, pero eso no basta para programas multi-hilo donde una operación compuesta (p. ej. "comprobar vacío + extraer") podría intercalarse.

2. **Proteger toda mutación con un `threading.Lock`** (o usar `queue.Queue`, que ya es thread-safe internamente con su propio lock y condición):

   ```python
   import threading

   class TriageQueue:
       def __init__(self):
           self._queues = {1: deque(), 2: deque(), 3: deque()}
           self._lock = threading.Lock()

       def enqueue(self, patient):
           with self._lock:            # <-- todo en una sección crítica
               self._queues[patient.triage_level].append(patient)

       def dequeue(self):
           with self._lock:            # <-- todo en una sección crítica
               return self._pop_next() # comprueba y extrae sin salir del lock
   ```

3. **Nunca separar "comprobar" de "extraer".** El error clásico es:

   ```python
   if not q.is_empty():   # ← comprobación fuera del lock
       return q._pop_next()  # ← otro worker puede extraer aquí → DOBLE PROCESAMIENTO
   ```

   La solución es que `dequeue()` **compruebe y extraiga dentro del mismo bloqueo**, de forma que ningún otro hilo pueda intercalarse entre ambas instrucciones. Como la comprobación y la extracción comparten el lock, la operación es indivisible.

4. **El orden de mutación correcto:**

   - **En `enqueue`:** añadir primero al deque y **después** notificar/liberar. El paciente solo es visible para otros workers una vez que está completament insertado.
   - **En `dequeue`:** comprobar vacío y extraer bajo el mismo lock; si vacío, esperar (con una `Condition`/`Event`) en vez de devolver un error, cuando queremos bloqueo en lugar de excepción.

5. **Por qué el diseño interno facilita esto:** al tener un diseño donde `dequeue()` se delega a `_pop_next()` (que ya itera 1→2→3 y extrae de la primera no vacía), el bloqueo envuelve una única llamada. La estructura de "tres deques" no introduce operaciones multi-paso sobre múltiples estructuras que rompan la atomicidad — solo tocamos UNA deque por operación.

### Concurrencia y el `QueueEmptyError`

En el programa actual (CLI de un solo hilo) `dequeue()` sobre cola vacía lanza `QueueEmptyError` y la CLI lo muestra con gracia. En una versión multi-hilo de producción, la política típica sería **bloquear al worker hasta que haya un paciente** (`condition.wait()`), o `dequeue(timeout=...)`, en lugar de lanzar excepción. Ese cambio de política es ortogonal a la estructura de datos elegida.

---

## 3. Sobre la elección de `Patient` como `@dataclass`

- `@dataclass` (biblioteca estándar) nos da `__init__`, `__repr__`, `__eq__` gratis, con **inmutabilidad suficiente** y sin lógica volcada en métodos manuales.
- Los datos se validan en `__post_init__` (nombre no vacío, nivel en {1,2,3}).
- El campo `arrived_at` se fija en el momento de creación y el `patient_id` proporciona una identidad legible para los humanos; **el orden de atención NO depende de la hora del reloj** (que puede tener colisiones), sino de la posición física en la deque — más robusto.

## 4. Responsabilidad de cada módulo

- `queue/patient.py` → modelo de datos (qué es un paciente).
- `queue/triage_queue.py` → comportamiento de la cola (cómo se ordenan y atendernos los pacientes). Toda la lógica vive aquí, no en `main()`.
- `triage_queue.py` (raíz) → interfaz de usuario CLI. Solo recoge entrada y formatea salida; no contiene reglas de negocio.
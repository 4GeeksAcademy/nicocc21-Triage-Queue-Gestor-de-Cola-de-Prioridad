#!/usr/bin/env python3
"""
Triage Queue — Gestor de Cola de Prioridad para Urgencias Hospitalarias.

CLI interactiva para gestionar pacientes por nivel de triaje.

Uso:
    python triage_queue.py
"""

import sys
from datetime import datetime

from queue.patient import Patient
from queue.triage_queue import QueueEmptyError, TriageQueue


class PatientId:
    """Small mutable counter to assign unique human-readable patient IDs."""

    def __init__(self) -> None:
        self.value = 0

    def next(self) -> int:
        """Return the next ID and increment the counter."""
        self.value += 1
        return self.value


def clear_screen() -> None:
    """Clear the terminal screen."""
    import os
    os.system("cls" if os.name == "nt" else "clear")


def print_header() -> None:
    """Print the application header."""
    print("=" * 48)
    print("        TRIAGE QUEUE — Gestor de Urgencias")
    print("=" * 48)
    print()


def print_menu() -> None:
    """Print the main menu options."""
    print("--- MENÚ PRINCIPAL ---")
    print()
    print("  1. Añadir paciente")
    print("  2. Llamar siguiente paciente")
    print("  3. Ver siguiente paciente")
    print("  4. Ver cola actual")
    print("  5. Ver estadísticas")
    print("  6. Salir")
    print()
    print("-" * 48)


def get_menu_option() -> int:
    """
    Prompt the user for a menu option and validate it.

    Returns:
        A valid menu option (1-6).
    """
    while True:
        try:
            choice = input("Selecciona una opción (1-6): ").strip()
            option = int(choice)
            if 1 <= option <= 6:
                return option
            print("  ❌ Opción inválida. Debe ser un número entre 1 y 6.")
        except ValueError:
            print("  ❌ Entrada inválida. Debes introducir un número.")


def get_triage_level() -> int:
    """
    Prompt the user for a triage level and validate it.

    Returns:
        A valid triage level (1, 2, or 3).
    """
    while True:
        print()
        print("  Niveles de triaje:")
        print("    1 — Crítico")
        print("    2 — Urgente")
        print("    3 — Estándar")
        print()
        try:
            choice = input("Nivel de triaje (1-3): ").strip()
            level = int(choice)
            if level in (1, 2, 3):
                return level
            print("  ❌ Nivel inválido. Debe ser 1, 2 o 3.")
        except ValueError:
            print("  ❌ Entrada inválida. Debes introducir un número.")


def get_patient_name() -> str:
    """
    Prompt the user for a patient name and validate it.

    Returns:
        A non-empty patient name.
    """
    while True:
        name = input("Nombre del paciente: ").strip()
        if name:
            return name
        print("  ❌ El nombre no puede estar vacío.")


# --- Command handlers ---


def handle_enqueue(queue: TriageQueue, ids: PatientId) -> None:
    """
    Handle adding a new patient to the queue.

    Args:
        queue: The triage queue.
        ids: Counter used to assign unique patient IDs.
    """
    print()
    print("--- NUEVO PACIENTE ---")
    name = get_patient_name()
    level = get_triage_level()
    try:
        patient = Patient(
            name=name,
            triage_level=level,
            arrived_at=datetime.now(),
            patient_id=ids.next(),
        )
        queue.enqueue(patient)
        print()
        print(f"  ✅ Paciente añadido correctamente:")
        print(f"     {patient}")
    except ValueError as e:
        print(f"  ❌ Error: {e}")
    print()


def handle_call_next(queue: TriageQueue) -> None:
    """Handle calling the next patient."""
    print()
    print("--- LLAMAR SIGUIENTE PACIENTE ---")
    try:
        patient = queue.dequeue()
        print(f"  🏥 Llamando a: {patient}")
    except QueueEmptyError as e:
        print(f"  ℹ️  {e}")
    print()


def handle_peek(queue: TriageQueue) -> None:
    """Handle viewing the next patient without dequeuing."""
    print()
    print("--- SIGUIENTE PACIENTE ---")
    patient = queue.peek()
    if patient is None:
        print("  ℹ️  No hay pacientes en espera.")
    else:
        print(f"  👤 Siguiente: {patient}")
    print()


def handle_list_queue(queue: TriageQueue) -> None:
    """Handle listing all waiting patients."""
    print()
    print("--- COLA DE ESPERA ---")
    patients = queue.list_queue()
    if not patients:
        print("  ℹ️  No hay pacientes en espera.")
    else:
        print(f"  Total: {len(patients)} paciente(s)")
        print()
        for i, patient in enumerate(patients, start=1):
            print(f"  {i}. {patient}")
    print()


def handle_stats(queue: TriageQueue) -> None:
    """Handle displaying queue statistics."""
    print()
    print("--- ESTADÍSTICAS ---")
    stats = queue.stats()
    print(f"  🔴  Nivel 1 (Crítico):  {stats['level_1']} paciente(s)")
    print(f"  🟡  Nivel 2 (Urgente):  {stats['level_2']} paciente(s)")
    print(f"  🟢  Nivel 3 (Estándar): {stats['level_3']} paciente(s)")
    print()
    print(f"  📊  Total en espera:    {stats['total']} paciente(s)")
    print()


def main() -> None:
    """Main loop for the Triage Queue CLI."""
    queue = TriageQueue()
    ids = PatientId()

    while True:
        try:
            clear_screen()
            print_header()
            print_menu()

            option = get_menu_option()

            if option == 1:
                handle_enqueue(queue, ids)
            elif option == 2:
                handle_call_next(queue)
            elif option == 3:
                handle_peek(queue)
            elif option == 4:
                handle_list_queue(queue)
            elif option == 5:
                handle_stats(queue)
            elif option == 6:
                print()
                print("🙏  Gracias por usar Triage Queue. ¡Hasta luego!")
                print()
                sys.exit(0)

            input("\nPresiona ENTER para continuar...")

        except KeyboardInterrupt:
            print()
            print("\n🙏  Interrupción del usuario. Saliendo...")
            sys.exit(0)


if __name__ == "__main__":
    main()
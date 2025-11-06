"""
Ejemplo de uso del simulador de panel solar sin interfaz gráfica.
Demuestra cómo usar las clases principales para realizar optimizaciones.
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from solar_panel_model import SolarPanelModel
from numerical_methods import NumericalOptimizer


def example_daily_optimization():
    """Ejemplo de optimización para un día específico."""
    print("=== OPTIMIZACIÓN DIARIA ===")
    
    # Crear modelo para Madrid (latitud 40.4°)
    madrid_model = SolarPanelModel(latitude=40.4, panel_area=2.0, efficiency=0.22)
    optimizer = NumericalOptimizer(madrid_model)
    
    # Día del solsticio de verano (día 172)
    day = 172
    min_angle, max_angle = 0, 90
    
    print(f"Optimizando para el día {day} del año (solsticio de verano)")
    print(f"Latitud: 40.4° (Madrid)")
    print(f"Área del panel: 2.0 m²")
    print(f"Eficiencia: 22%")
    print()
    
    # Comparar todos los métodos
    results = optimizer.compare_methods(min_angle, max_angle, 'daily', day)
    
    print("Resultados de comparación de métodos:")
    for method, data in results.items():
        if 'error' not in data:
            print(f"{method:20}: {data['angle']:6.2f}° -> {data['energy']:8.2f} Wh ({data['evaluations']:3d} evaluaciones)")
        else:
            print(f"{method:20}: ERROR - {data['error']}")
    
    return results


def example_annual_optimization():
    """Ejemplo de optimización anual."""
    print("\n=== OPTIMIZACIÓN ANUAL ===")
    
    # Crear modelo para diferentes latitudes
    latitudes = [20, 30, 40, 50, 60]  # Diferentes ubicaciones
    results_by_latitude = {}
    
    for lat in latitudes:
        print(f"\nOptimizando para latitud {lat}°")
        model = SolarPanelModel(latitude=lat, panel_area=1.0, efficiency=0.20)
        optimizer = NumericalOptimizer(model)
        
        # Usar búsqueda ternaria para rapidez
        optimal_angle, max_energy, history = optimizer.ternary_search(
            0, 90, tolerance=0.1, optimization_type='annual')
        
        results_by_latitude[lat] = {
            'angle': optimal_angle,
            'energy': max_energy,
            'evaluations': len(history)
        }
        
        print(f"  Ángulo óptimo: {optimal_angle:.1f}°")
        print(f"  Energía anual: {max_energy:.1f} kWh")
        print(f"  Evaluaciones: {len(history)}")
    
    return results_by_latitude


def example_sensitivity_analysis():
    """Ejemplo de análisis de sensibilidad."""
    print("\n=== ANÁLISIS DE SENSIBILIDAD ===")
    
    # Modelo para Barcelona (latitud 41.4°)
    barcelona_model = SolarPanelModel(latitude=41.4, panel_area=1.5, efficiency=0.21)
    optimizer = NumericalOptimizer(barcelona_model)
    
    # Encontrar ángulo óptimo anual
    optimal_angle, max_energy, _ = optimizer.golden_section_search(
        10, 60, tolerance=0.1, optimization_type='annual')
    
    print(f"Ángulo óptimo para Barcelona: {optimal_angle:.1f}°")
    print(f"Energía máxima anual: {max_energy:.1f} kWh")
    
    # Análisis de sensibilidad
    sensitivity_data = optimizer.sensitivity_analysis(
        optimal_angle, range_percent=15, optimization_type='annual')
    
    print("\nAnálisis de sensibilidad (±15% del ángulo óptimo):")
    print("Ángulo (°)  | Energía (kWh) | Pérdida (%)")
    print("-" * 40)
    
    for angle, energy, loss in sensitivity_data[::2]:  # Mostrar cada 2 puntos
        print(f"{angle:8.1f}    | {energy:9.1f}     | {loss:7.2f}")
    
    return sensitivity_data


def plot_comparison_example():
    """Crear gráficas de ejemplo."""
    print("\n=== CREANDO GRÁFICAS DE EJEMPLO ===")
    
    # Modelo para análisis
    model = SolarPanelModel(latitude=35.0, panel_area=1.0, efficiency=0.20)
    
    # Calcular energía para diferentes ángulos
    angles = np.arange(0, 91, 2)
    daily_energies = []
    annual_energies = []
    
    print("Calculando energías para diferentes ángulos...")
    for angle in angles:
        daily_energy = model.daily_energy(angle, 172)  # Solsticio
        annual_energy = model.annual_energy(angle)
        daily_energies.append(daily_energy)
        annual_energies.append(annual_energy)
    
    # Crear gráficas
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Gráfica diaria
    ax1.plot(angles, daily_energies, 'b-', linewidth=2, marker='o', markersize=4)
    ax1.set_xlabel('Ángulo de inclinación (°)')
    ax1.set_ylabel('Energía diaria (Wh)')
    ax1.set_title('Energía vs Ángulo - Solsticio de Verano')
    ax1.grid(True, alpha=0.3)
    
    # Encontrar y marcar el óptimo diario
    max_daily_idx = np.argmax(daily_energies)
    ax1.scatter(angles[max_daily_idx], daily_energies[max_daily_idx], 
               color='red', s=100, marker='*', zorder=5,
               label=f'Óptimo: {angles[max_daily_idx]}°')
    ax1.legend()
    
    # Gráfica anual
    ax2.plot(angles, annual_energies, 'g-', linewidth=2, marker='s', markersize=4)
    ax2.set_xlabel('Ángulo de inclinación (°)')
    ax2.set_ylabel('Energía anual (kWh)')
    ax2.set_title('Energía vs Ángulo - Anual')
    ax2.grid(True, alpha=0.3)
    
    # Encontrar y marcar el óptimo anual
    max_annual_idx = np.argmax(annual_energies)
    ax2.scatter(angles[max_annual_idx], annual_energies[max_annual_idx], 
               color='red', s=100, marker='*', zorder=5,
               label=f'Óptimo: {angles[max_annual_idx]}°')
    ax2.legend()
    
    plt.tight_layout()
    
    # Guardar gráfica
    try:
        plt.savefig('../docs/energy_vs_angle_example.png', dpi=300, bbox_inches='tight')
        print("Gráfica guardada como 'energy_vs_angle_example.png'")
    except:
        print("No se pudo guardar la gráfica")
    
    plt.show()


def main():
    """Función principal del ejemplo."""
    print("SIMULADOR DE PANEL SOLAR - EJEMPLOS DE USO")
    print("=" * 50)
    
    try:
        # Ejecutar ejemplos
        daily_results = example_daily_optimization()
        annual_results = example_annual_optimization()
        sensitivity_data = example_sensitivity_analysis()
        
        # Crear gráficas si matplotlib está disponible
        try:
            plot_comparison_example()
        except ImportError:
            print("Matplotlib no disponible para gráficas")
        
        print("\n" + "=" * 50)
        print("RESUMEN DE EJEMPLOS COMPLETADO")
        print("Para usar la interfaz gráfica, ejecute: python src/main.py")
        
    except Exception as e:
        print(f"Error durante la ejecución de ejemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

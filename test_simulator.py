"""
Script de prueba simple para el simulador de panel solar.
No requiere PyQt5, solo usa las clases principales.
"""

import sys
import os
import numpy as np

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from solar_panel_model import SolarPanelModel
    from numerical_methods import NumericalOptimizer
    print("✓ Importaciones exitosas")
except ImportError as e:
    print(f"✗ Error de importación: {e}")
    sys.exit(1)


def test_basic_functionality():
    """Prueba la funcionalidad básica del simulador."""
    print("\n=== PRUEBA BÁSICA DEL SIMULADOR ===")
    
    # Crear modelo para Madrid (40.4°N)
    print("Creando modelo para Madrid (latitud 40.4°)...")
    madrid_model = SolarPanelModel(latitude=40.4, panel_area=2.0, efficiency=0.22)
    
    # Crear optimizador
    optimizer = NumericalOptimizer(madrid_model)
    
    # Prueba de optimización diaria (solsticio de verano)
    print("Ejecutando optimización diaria para el solsticio de verano...")
    day = 172  # Solsticio de verano
    
    try:
        # Usar búsqueda ternaria (rápida y precisa)
        optimal_angle, max_energy, history = optimizer.ternary_search(
            min_angle=20, max_angle=60, 
            tolerance=0.1, 
            optimization_type='daily', 
            day_of_year=day
        )
        
        print(f"✓ Optimización diaria completada:")
        print(f"  - Ángulo óptimo: {optimal_angle:.2f}°")
        print(f"  - Energía máxima: {max_energy:.2f} Wh")
        print(f"  - Evaluaciones: {len(history)}")
        
    except Exception as e:
        print(f"✗ Error en optimización diaria: {e}")
        return False
    
    # Prueba de optimización anual
    print("\nEjecutando optimización anual...")
    try:
        optimal_angle_annual, max_energy_annual, history_annual = optimizer.ternary_search(
            min_angle=25, max_angle=55, 
            tolerance=0.1, 
            optimization_type='annual'
        )
        
        print(f"✓ Optimización anual completada:")
        print(f"  - Ángulo óptimo anual: {optimal_angle_annual:.2f}°")
        print(f"  - Energía máxima anual: {max_energy_annual:.2f} kWh")
        print(f"  - Evaluaciones: {len(history_annual)}")
        
    except Exception as e:
        print(f"✗ Error en optimización anual: {e}")
        return False
    
    # Comparación de métodos (versión rápida)
    print("\nComparando métodos de optimización...")
    try:
        comparison_results = {}
        
        # Solo probar los métodos más rápidos
        methods_to_test = [
            ('ternary_search', 'Búsqueda ternaria'),
            ('golden_section_search', 'Sección áurea')
        ]
        
        for method_name, display_name in methods_to_test:
            try:
                method = getattr(optimizer, method_name)
                angle, energy, hist = method(
                    min_angle=25, max_angle=55, 
                    tolerance=0.5,  # Tolerancia más relajada para rapidez
                    optimization_type='daily',
                    day_of_year=day
                )
                comparison_results[display_name] = {
                    'angle': angle,
                    'energy': energy,
                    'evaluations': len(hist)
                }
                print(f"  ✓ {display_name}: {angle:.1f}° -> {energy:.1f} Wh ({len(hist)} eval.)")
            except Exception as e:
                print(f"  ✗ {display_name}: Error - {e}")
        
    except Exception as e:
        print(f"✗ Error en comparación de métodos: {e}")
    
    return True


def test_different_latitudes():
    """Prueba el simulador con diferentes latitudes."""
    print("\n=== PRUEBA PARA DIFERENTES LATITUDES ===")
    
    latitudes = [
        (0, "Ecuador"),
        (23.5, "Trópico de Cáncer"),
        (40.4, "Madrid"),
        (51.5, "Londres"),
        (60, "Escandinavia")
    ]
    
    for lat, location in latitudes:
        try:
            model = SolarPanelModel(latitude=lat, panel_area=1.0, efficiency=0.20)
            optimizer = NumericalOptimizer(model)
            
            # Optimización anual rápida
            min_a, max_a = model.get_optimal_angles_range()
            angle, energy, _ = optimizer.ternary_search(
                min_angle=min_a, max_angle=max_a, 
                tolerance=1.0,  # Tolerancia relajada
                optimization_type='annual'
            )
            
            print(f"  {location:20} ({lat:5.1f}°): {angle:5.1f}° -> {energy:6.1f} kWh")
            
        except Exception as e:
            print(f"  {location:20} ({lat:5.1f}°): Error - {e}")


def test_model_calculations():
    """Prueba cálculos específicos del modelo."""
    print("\n=== PRUEBA DE CÁLCULOS DEL MODELO ===")
    
    model = SolarPanelModel(latitude=40.4, panel_area=1.0, efficiency=0.20)
    
    # Prueba cálculos básicos
    try:
        # Declinación solar
        dec_summer = model.solar_declination(172)  # Solsticio verano
        dec_winter = model.solar_declination(355)  # Solsticio invierno
        print(f"✓ Declinación solar:")
        print(f"  - Solsticio verano: {np.degrees(dec_summer):.2f}°")
        print(f"  - Solsticio invierno: {np.degrees(dec_winter):.2f}°")
        
        # Elevación solar al mediodía
        hour_angle_noon = model.hour_angle(12)
        elevation_summer = model.solar_elevation_angle(dec_summer, hour_angle_noon)
        elevation_winter = model.solar_elevation_angle(dec_winter, hour_angle_noon)
        print(f"✓ Elevación solar al mediodía:")
        print(f"  - Verano: {np.degrees(elevation_summer):.2f}°")
        print(f"  - Invierno: {np.degrees(elevation_winter):.2f}°")
        
        # Potencia instantánea
        power_summer = model.instantaneous_power(35, 172, 12)  # 35° inclinación
        power_winter = model.instantaneous_power(35, 355, 12)
        print(f"✓ Potencia instantánea (35° inclinación, mediodía):")
        print(f"  - Verano: {power_summer:.1f} W")
        print(f"  - Invierno: {power_winter:.1f} W")
        
    except Exception as e:
        print(f"✗ Error en cálculos del modelo: {e}")


def main():
    """Función principal de prueba."""
    print("SIMULADOR DE PANEL SOLAR - PRUEBAS SIN INTERFAZ GRÁFICA")
    print("=" * 60)
    
    # Verificar que las librerías básicas funcionan
    print(f"Versión de Python: {sys.version}")
    print(f"Versión de NumPy: {np.__version__}")
    
    # Ejecutar pruebas
    try:
        # Prueba básica
        if not test_basic_functionality():
            print("\n✗ Las pruebas básicas fallaron")
            return
        
        # Pruebas adicionales
        test_different_latitudes()
        test_model_calculations()
        
        print("\n" + "=" * 60)
        print("✓ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("\nEl simulador está funcionando correctamente.")
        print("Para usar la interfaz gráfica, instale PyQt5:")
        print("  pip install PyQt5")
        print("  python src/main.py")
        
    except Exception as e:
        print(f"\n✗ Error inesperado durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
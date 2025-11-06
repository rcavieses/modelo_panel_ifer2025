"""
Métodos numéricos para encontrar el ángulo óptimo de inclinación del panel solar.
Implementa algoritmos de optimización como búsqueda ternaria, método de Newton-Raphson,
y búsqueda de fuerza bruta para maximizar la energía captada.
"""

import numpy as np
import math
from typing import Callable, Tuple, List
from solar_panel_model import SolarPanelModel


class NumericalOptimizer:
    """
    Clase que implementa diferentes métodos numéricos para encontrar
    el ángulo óptimo de inclinación del panel solar.
    """
    
    def __init__(self, solar_model: SolarPanelModel):
        """
        Inicializa el optimizador con un modelo de panel solar.
        
        Args:
            solar_model (SolarPanelModel): Instancia del modelo de panel solar
        """
        self.solar_model = solar_model
        self.optimization_history = []
    
    def clear_history(self):
        """Limpia el historial de optimización."""
        self.optimization_history = []
    
    def brute_force_search(self, min_angle: float, max_angle: float, 
                          step: float = 0.5, optimization_type: str = 'daily',
                          day_of_year: int = 172) -> Tuple[float, float, List[Tuple[float, float]]]:
        """
        Búsqueda por fuerza bruta para encontrar el ángulo óptimo.
        
        Args:
            min_angle (float): Ángulo mínimo en grados
            max_angle (float): Ángulo máximo en grados
            step (float): Paso de búsqueda en grados
            optimization_type (str): 'daily' o 'annual'
            day_of_year (int): Día del año para optimización diaria
            
        Returns:
            tuple: (ángulo_óptimo, energía_máxima, historial_puntos)
        """
        self.clear_history()
        angles = np.arange(min_angle, max_angle + step, step)
        energies = []
        
        for angle in angles:
            if optimization_type == 'daily':
                energy = self.solar_model.daily_energy(angle, day_of_year)
            else:  # annual
                energy = self.solar_model.annual_energy(angle)
            
            energies.append(energy)
            self.optimization_history.append((angle, energy))
        
        max_idx = np.argmax(energies)
        optimal_angle = angles[max_idx]
        max_energy = energies[max_idx]
        
        return optimal_angle, max_energy, self.optimization_history.copy()
    
    def ternary_search(self, min_angle: float, max_angle: float, 
                      tolerance: float = 1e-3, optimization_type: str = 'daily',
                      day_of_year: int = 172) -> Tuple[float, float, List[Tuple[float, float]]]:
        """
        Búsqueda ternaria para encontrar el ángulo óptimo.
        
        Args:
            min_angle (float): Ángulo mínimo en grados
            max_angle (float): Ángulo máximo en grados
            tolerance (float): Tolerancia para la convergencia
            optimization_type (str): 'daily' o 'annual'
            day_of_year (int): Día del año para optimización diaria
            
        Returns:
            tuple: (ángulo_óptimo, energía_máxima, historial_puntos)
        """
        self.clear_history()
        left = min_angle
        right = max_angle
        
        def energy_function(angle):
            if optimization_type == 'daily':
                return self.solar_model.daily_energy(angle, day_of_year)
            else:
                return self.solar_model.annual_energy(angle)
        
        iteration = 0
        max_iterations = 100
        
        while (right - left) > tolerance and iteration < max_iterations:
            # Dividir el intervalo en tres partes
            m1 = left + (right - left) / 3
            m2 = right - (right - left) / 3
            
            # Evaluar la función en los puntos medios
            f1 = energy_function(m1)
            f2 = energy_function(m2)
            
            # Agregar puntos al historial
            self.optimization_history.append((m1, f1))
            self.optimization_history.append((m2, f2))
            
            # Reducir el intervalo de búsqueda
            if f1 < f2:
                left = m1
            else:
                right = m2
            
            iteration += 1
        
        # Punto óptimo
        optimal_angle = (left + right) / 2
        max_energy = energy_function(optimal_angle)
        self.optimization_history.append((optimal_angle, max_energy))
        
        return optimal_angle, max_energy, self.optimization_history.copy()
    
    def golden_section_search(self, min_angle: float, max_angle: float,
                             tolerance: float = 1e-3, optimization_type: str = 'daily',
                             day_of_year: int = 172) -> Tuple[float, float, List[Tuple[float, float]]]:
        """
        Búsqueda de sección áurea para encontrar el ángulo óptimo.
        
        Args:
            min_angle (float): Ángulo mínimo en grados
            max_angle (float): Ángulo máximo en grados
            tolerance (float): Tolerancia para la convergencia
            optimization_type (str): 'daily' o 'annual'
            day_of_year (int): Día del año para optimización diaria
            
        Returns:
            tuple: (ángulo_óptimo, energía_máxima, historial_puntos)
        """
        self.clear_history()
        
        def energy_function(angle):
            if optimization_type == 'daily':
                return self.solar_model.daily_energy(angle, day_of_year)
            else:
                return self.solar_model.annual_energy(angle)
        
        # Razón áurea
        phi = (1 + math.sqrt(5)) / 2
        resphi = 2 - phi
        
        # Inicializar puntos
        a = min_angle
        b = max_angle
        tol = tolerance
        
        # Puntos iniciales
        x1 = a + resphi * (b - a)
        x2 = b - resphi * (b - a)
        f1 = energy_function(x1)
        f2 = energy_function(x2)
        
        self.optimization_history.append((x1, f1))
        self.optimization_history.append((x2, f2))
        
        iteration = 0
        max_iterations = 100
        
        while abs(b - a) > tol and iteration < max_iterations:
            if f1 > f2:
                b = x2
                x2 = x1
                f2 = f1
                x1 = a + resphi * (b - a)
                f1 = energy_function(x1)
                self.optimization_history.append((x1, f1))
            else:
                a = x1
                x1 = x2
                f1 = f2
                x2 = b - resphi * (b - a)
                f2 = energy_function(x2)
                self.optimization_history.append((x2, f2))
            
            iteration += 1
        
        # Punto óptimo
        optimal_angle = (a + b) / 2
        max_energy = energy_function(optimal_angle)
        
        return optimal_angle, max_energy, self.optimization_history.copy()
    
    def gradient_ascent(self, initial_angle: float, learning_rate: float = 0.1,
                       tolerance: float = 1e-3, optimization_type: str = 'daily',
                       day_of_year: int = 172) -> Tuple[float, float, List[Tuple[float, float]]]:
        """
        Método de ascenso por gradiente para encontrar el ángulo óptimo.
        
        Args:
            initial_angle (float): Ángulo inicial en grados
            learning_rate (float): Tasa de aprendizaje
            tolerance (float): Tolerancia para la convergencia
            optimization_type (str): 'daily' o 'annual'
            day_of_year (int): Día del año para optimización diaria
            
        Returns:
            tuple: (ángulo_óptimo, energía_máxima, historial_puntos)
        """
        self.clear_history()
        
        def energy_function(angle):
            if optimization_type == 'daily':
                return self.solar_model.daily_energy(angle, day_of_year)
            else:
                return self.solar_model.annual_energy(angle)
        
        def numerical_gradient(angle, h=0.01):
            """Calcula la derivada numérica."""
            return (energy_function(angle + h) - energy_function(angle - h)) / (2 * h)
        
        current_angle = initial_angle
        iteration = 0
        max_iterations = 1000
        
        while iteration < max_iterations:
            current_energy = energy_function(current_angle)
            self.optimization_history.append((current_angle, current_energy))
            
            # Calcular gradiente
            gradient = numerical_gradient(current_angle)
            
            # Actualizar ángulo
            new_angle = current_angle + learning_rate * gradient
            
            # Limitar ángulo dentro de rangos válidos
            new_angle = max(0, min(90, new_angle))
            
            # Verificar convergencia
            if abs(new_angle - current_angle) < tolerance:
                break
            
            current_angle = new_angle
            iteration += 1
        
        final_energy = energy_function(current_angle)
        return current_angle, final_energy, self.optimization_history.copy()
    
    def compare_methods(self, min_angle: float, max_angle: float,
                       optimization_type: str = 'daily', day_of_year: int = 172) -> dict:
        """
        Compara diferentes métodos de optimización.
        
        Args:
            min_angle (float): Ángulo mínimo en grados
            max_angle (float): Ángulo máximo en grados
            optimization_type (str): 'daily' o 'annual'
            day_of_year (int): Día del año para optimización diaria
            
        Returns:
            dict: Resultados de todos los métodos
        """
        results = {}
        
        # Búsqueda por fuerza bruta
        try:
            angle, energy, history = self.brute_force_search(
                min_angle, max_angle, 1.0, optimization_type, day_of_year)
            results['brute_force'] = {
                'angle': angle,
                'energy': energy,
                'evaluations': len(history),
                'history': history
            }
        except Exception as e:
            results['brute_force'] = {'error': str(e)}
        
        # Búsqueda ternaria
        try:
            angle, energy, history = self.ternary_search(
                min_angle, max_angle, 1e-2, optimization_type, day_of_year)
            results['ternary_search'] = {
                'angle': angle,
                'energy': energy,
                'evaluations': len(history),
                'history': history
            }
        except Exception as e:
            results['ternary_search'] = {'error': str(e)}
        
        # Sección áurea
        try:
            angle, energy, history = self.golden_section_search(
                min_angle, max_angle, 1e-2, optimization_type, day_of_year)
            results['golden_section'] = {
                'angle': angle,
                'energy': energy,
                'evaluations': len(history),
                'history': history
            }
        except Exception as e:
            results['golden_section'] = {'error': str(e)}
        
        # Ascenso por gradiente
        try:
            initial_angle = (min_angle + max_angle) / 2
            angle, energy, history = self.gradient_ascent(
                initial_angle, 0.1, 1e-2, optimization_type, day_of_year)
            results['gradient_ascent'] = {
                'angle': angle,
                'energy': energy,
                'evaluations': len(history),
                'history': history
            }
        except Exception as e:
            results['gradient_ascent'] = {'error': str(e)}
        
        return results
    
    def sensitivity_analysis(self, optimal_angle: float, range_percent: float = 10,
                           optimization_type: str = 'daily', day_of_year: int = 172) -> List[Tuple[float, float, float]]:
        """
        Realiza un análisis de sensibilidad alrededor del ángulo óptimo.
        
        Args:
            optimal_angle (float): Ángulo óptimo en grados
            range_percent (float): Porcentaje de variación alrededor del óptimo
            optimization_type (str): 'daily' o 'annual'
            day_of_year (int): Día del año para optimización diaria
            
        Returns:
            list: Lista de tuplas (ángulo, energía, pérdida_porcentual)
        """
        def energy_function(angle):
            if optimization_type == 'daily':
                return self.solar_model.daily_energy(angle, day_of_year)
            else:
                return self.solar_model.annual_energy(angle)
        
        optimal_energy = energy_function(optimal_angle)
        range_angle = optimal_angle * range_percent / 100
        
        angles = np.linspace(optimal_angle - range_angle, 
                           optimal_angle + range_angle, 21)
        
        results = []
        for angle in angles:
            if 0 <= angle <= 90:  # Verificar que el ángulo sea válido
                energy = energy_function(angle)
                loss_percent = ((optimal_energy - energy) / optimal_energy) * 100
                results.append((angle, energy, loss_percent))
        
        return results

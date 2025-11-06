"""
Interfaz gráfica para el simulador de panel solar usando PyQt5.
Permite al usuario configurar parámetros del panel y encontrar el ángulo óptimo
usando diferentes métodos numéricos.
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                           QPushButton, QComboBox, QTextEdit, QTabWidget,
                           QGroupBox, QSpinBox, QDoubleSpinBox, QProgressBar,
                           QMessageBox, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

from solar_panel_model import SolarPanelModel
from numerical_methods import NumericalOptimizer


class OptimizationWorker(QThread):
    """Worker thread para realizar optimizaciones sin bloquear la UI."""
    
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int)
    
    def __init__(self, optimizer, method, params):
        super().__init__()
        self.optimizer = optimizer
        self.method = method
        self.params = params
    
    def run(self):
        try:
            if self.method == 'brute_force':
                result = self.optimizer.brute_force_search(**self.params)
            elif self.method == 'ternary_search':
                result = self.optimizer.ternary_search(**self.params)
            elif self.method == 'golden_section':
                result = self.optimizer.golden_section_search(**self.params)
            elif self.method == 'gradient_ascent':
                result = self.optimizer.gradient_ascent(**self.params)
            elif self.method == 'compare_all':
                result = self.optimizer.compare_methods(**self.params)
            
            self.finished.emit({'success': True, 'result': result})
        except Exception as e:
            self.finished.emit({'success': False, 'error': str(e)})


class MplCanvas(FigureCanvas):
    """Canvas personalizado para matplotlib."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)


class SolarPanelGUI(QMainWindow):
    """Interfaz gráfica principal para el simulador de panel solar."""
    
    def __init__(self):
        super().__init__()
        self.solar_model = None
        self.optimizer = None
        self.optimization_results = {}
        self.current_worker = None
        
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """Inicializar la interfaz de usuario."""
        self.setWindowTitle("Simulador de Panel Solar - Optimización de Ángulo")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter para dividir controles y gráficas
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel de controles (izquierda)
        control_panel = self.create_control_panel()
        splitter.addWidget(control_panel)
        
        # Panel de visualización (derecha)
        visualization_panel = self.create_visualization_panel()
        splitter.addWidget(visualization_panel)
        
        # Configurar proporciones del splitter
        splitter.setSizes([400, 1000])
        
        # Barra de estado
        self.statusBar().showMessage("Listo para optimizar")
        
        # Configurar valores por defecto
        self.load_default_values()
    
    def create_control_panel(self):
        """Crear el panel de controles."""
        panel = QFrame()
        panel.setMaximumWidth(450)
        layout = QVBoxLayout(panel)
        
        # Parámetros del sistema
        system_group = QGroupBox("Parámetros del Sistema")
        system_layout = QGridLayout(system_group)
        
        # Latitud
        system_layout.addWidget(QLabel("Latitud (°):"), 0, 0)
        self.latitude_input = QDoubleSpinBox()
        self.latitude_input.setRange(-90, 90)
        self.latitude_input.setValue(40.0)
        self.latitude_input.setDecimals(2)
        system_layout.addWidget(self.latitude_input, 0, 1)
        
        # Área del panel
        system_layout.addWidget(QLabel("Área del panel (m²):"), 1, 0)
        self.area_input = QDoubleSpinBox()
        self.area_input.setRange(0.1, 100)
        self.area_input.setValue(1.0)
        self.area_input.setDecimals(2)
        system_layout.addWidget(self.area_input, 1, 1)
        
        # Eficiencia
        system_layout.addWidget(QLabel("Eficiencia (%):"), 2, 0)
        self.efficiency_input = QDoubleSpinBox()
        self.efficiency_input.setRange(1, 50)
        self.efficiency_input.setValue(20)
        self.efficiency_input.setDecimals(1)
        system_layout.addWidget(self.efficiency_input, 2, 1)
        
        layout.addWidget(system_group)
        
        # Parámetros de optimización
        optim_group = QGroupBox("Parámetros de Optimización")
        optim_layout = QGridLayout(optim_group)
        
        # Tipo de optimización
        optim_layout.addWidget(QLabel("Tipo de optimización:"), 0, 0)
        self.optimization_type = QComboBox()
        self.optimization_type.addItems(["Diaria", "Anual"])
        optim_layout.addWidget(self.optimization_type, 0, 1)
        
        # Día del año (para optimización diaria)
        optim_layout.addWidget(QLabel("Día del año:"), 1, 0)
        self.day_of_year = QSpinBox()
        self.day_of_year.setRange(1, 365)
        self.day_of_year.setValue(172)  # Solsticio de verano
        optim_layout.addWidget(self.day_of_year, 1, 1)
        
        # Ángulo mínimo
        optim_layout.addWidget(QLabel("Ángulo mínimo (°):"), 2, 0)
        self.min_angle = QDoubleSpinBox()
        self.min_angle.setRange(0, 90)
        self.min_angle.setValue(0)
        optim_layout.addWidget(self.min_angle, 2, 1)
        
        # Ángulo máximo
        optim_layout.addWidget(QLabel("Ángulo máximo (°):"), 3, 0)
        self.max_angle = QDoubleSpinBox()
        self.max_angle.setRange(0, 90)
        self.max_angle.setValue(90)
        optim_layout.addWidget(self.max_angle, 3, 1)
        
        layout.addWidget(optim_group)
        
        # Métodos de optimización
        method_group = QGroupBox("Método de Optimización")
        method_layout = QVBoxLayout(method_group)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Búsqueda por fuerza bruta",
            "Búsqueda ternaria",
            "Sección áurea",
            "Ascenso por gradiente",
            "Comparar todos los métodos"
        ])
        method_layout.addWidget(self.method_combo)
        
        # Botón de optimización
        self.optimize_button = QPushButton("Optimizar Ángulo")
        self.optimize_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)
        method_layout.addWidget(self.optimize_button)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        method_layout.addWidget(self.progress_bar)
        
        layout.addWidget(method_group)
        
        # Resultados
        results_group = QGroupBox("Resultados")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setFont(QFont("Courier", 9))
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        # Botones adicionales
        buttons_layout = QHBoxLayout()
        
        self.analysis_button = QPushButton("Análisis de Sensibilidad")
        self.analysis_button.setEnabled(False)
        buttons_layout.addWidget(self.analysis_button)
        
        self.clear_button = QPushButton("Limpiar")
        buttons_layout.addWidget(self.clear_button)
        
        layout.addLayout(buttons_layout)
        
        # Espaciador
        layout.addStretch()
        
        return panel
    
    def create_visualization_panel(self):
        """Crear el panel de visualización."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Pestañas para diferentes visualizaciones
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Pestaña de optimización
        self.optimization_canvas = MplCanvas(width=8, height=6)
        self.tabs.addTab(self.optimization_canvas, "Optimización")
        
        # Pestaña de comparación
        self.comparison_canvas = MplCanvas(width=8, height=6)
        self.tabs.addTab(self.comparison_canvas, "Comparación de Métodos")
        
        # Pestaña de análisis diario/anual
        self.analysis_canvas = MplCanvas(width=8, height=6)
        self.tabs.addTab(self.analysis_canvas, "Análisis Temporal")
        
        return panel
    
    def connect_signals(self):
        """Conectar señales de la interfaz."""
        self.optimize_button.clicked.connect(self.run_optimization)
        self.analysis_button.clicked.connect(self.run_sensitivity_analysis)
        self.clear_button.clicked.connect(self.clear_results)
        self.optimization_type.currentTextChanged.connect(self.update_day_visibility)
        self.latitude_input.valueChanged.connect(self.update_angle_range)
    
    def load_default_values(self):
        """Cargar valores por defecto."""
        self.update_angle_range()
        self.update_day_visibility()
    
    def update_day_visibility(self):
        """Actualizar visibilidad del campo día del año."""
        is_daily = self.optimization_type.currentText() == "Diaria"
        self.day_of_year.setEnabled(is_daily)
    
    def update_angle_range(self):
        """Actualizar rango de ángulos basado en latitud."""
        latitude = self.latitude_input.value()
        min_suggested = max(0, latitude - 20)
        max_suggested = min(90, latitude + 20)
        
        self.min_angle.setValue(min_suggested)
        self.max_angle.setValue(max_suggested)
    
    def get_current_model(self):
        """Obtener el modelo actual con los parámetros de la interfaz."""
        latitude = self.latitude_input.value()
        area = self.area_input.value()
        efficiency = self.efficiency_input.value() / 100  # Convertir porcentaje
        
        return SolarPanelModel(latitude, area, efficiency)
    
    def run_optimization(self):
        """Ejecutar la optimización."""
        try:
            # Crear modelo y optimizador
            self.solar_model = self.get_current_model()
            self.optimizer = NumericalOptimizer(self.solar_model)
            
            # Parámetros de optimización
            min_angle = self.min_angle.value()
            max_angle = self.max_angle.value()
            optimization_type = 'daily' if self.optimization_type.currentText() == 'Diaria' else 'annual'
            day_of_year = self.day_of_year.value()
            
            # Verificar parámetros
            if min_angle >= max_angle:
                QMessageBox.warning(self, "Error", "El ángulo mínimo debe ser menor que el máximo")
                return
            
            # Preparar parámetros
            params = {
                'min_angle': min_angle,
                'max_angle': max_angle,
                'optimization_type': optimization_type,
                'day_of_year': day_of_year
            }
            
            # Determinar método
            method_text = self.method_combo.currentText()
            method_map = {
                "Búsqueda por fuerza bruta": "brute_force",
                "Búsqueda ternaria": "ternary_search",
                "Sección áurea": "golden_section",
                "Ascenso por gradiente": "gradient_ascent",
                "Comparar todos los métodos": "compare_all"
            }
            
            method = method_map[method_text]
            
            # Configurar UI para optimización
            self.optimize_button.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Progreso indeterminado
            self.statusBar().showMessage("Optimizando...")
            
            # Ejecutar en worker thread
            self.current_worker = OptimizationWorker(self.optimizer, method, params)
            self.current_worker.finished.connect(self.on_optimization_finished)
            self.current_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante la optimización: {str(e)}")
            self.reset_ui_after_optimization()
    
    def on_optimization_finished(self, result):
        """Manejar finalización de optimización."""
        self.reset_ui_after_optimization()
        
        if result['success']:
            self.optimization_results = result['result']
            self.display_results()
            self.plot_results()
            self.analysis_button.setEnabled(True)
            self.statusBar().showMessage("Optimización completada")
        else:
            QMessageBox.critical(self, "Error", f"Error en optimización: {result['error']}")
            self.statusBar().showMessage("Error en optimización")
    
    def reset_ui_after_optimization(self):
        """Resetear UI después de optimización."""
        self.optimize_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        if self.current_worker:
            self.current_worker.quit()
            self.current_worker = None
    
    def display_results(self):
        """Mostrar resultados en el área de texto."""
        results = self.optimization_results
        text = ""
        
        if isinstance(results, dict) and 'brute_force' in results:
            # Comparación de métodos
            text = "=== COMPARACIÓN DE MÉTODOS ===\n\n"
            
            for method, data in results.items():
                if 'error' in data:
                    text += f"{method.upper()}: ERROR - {data['error']}\n\n"
                else:
                    text += f"{method.upper()}:\n"
                    text += f"  Ángulo óptimo: {data['angle']:.2f}°\n"
                    text += f"  Energía máxima: {data['energy']:.2f} {'Wh' if self.optimization_type.currentText() == 'Diaria' else 'kWh'}\n"
                    text += f"  Evaluaciones: {data['evaluations']}\n\n"
        else:
            # Método individual
            angle, energy, history = results
            method_name = self.method_combo.currentText()
            unit = 'Wh' if self.optimization_type.currentText() == 'Diaria' else 'kWh'
            
            text = f"=== {method_name.upper()} ===\n\n"
            text += f"Ángulo óptimo: {angle:.2f}°\n"
            text += f"Energía máxima: {energy:.2f} {unit}\n"
            text += f"Evaluaciones realizadas: {len(history)}\n\n"
            
            # Información adicional del sistema
            text += f"Parámetros del sistema:\n"
            text += f"  Latitud: {self.latitude_input.value()}°\n"
            text += f"  Área del panel: {self.area_input.value()} m²\n"
            text += f"  Eficiencia: {self.efficiency_input.value()}%\n"
            
            if self.optimization_type.currentText() == 'Diaria':
                text += f"  Día del año: {self.day_of_year.value()}\n"
        
        self.results_text.setText(text)
    
    def plot_results(self):
        """Graficar resultados de optimización."""
        if not self.optimization_results:
            return
        
        # Limpiar canvas
        self.optimization_canvas.fig.clear()
        
        results = self.optimization_results
        
        if isinstance(results, dict) and 'brute_force' in results:
            # Comparación de métodos
            self.plot_method_comparison(results)
        else:
            # Método individual
            self.plot_single_method(results)
        
        self.optimization_canvas.draw()
    
    def plot_single_method(self, results):
        """Graficar resultado de un método individual."""
        angle, energy, history = results
        
        if not history:
            return
        
        angles = [point[0] for point in history]
        energies = [point[1] for point in history]
        
        ax = self.optimization_canvas.fig.add_subplot(111)
        
        # Gráfica de la función objetivo
        angle_range = np.linspace(self.min_angle.value(), self.max_angle.value(), 100)
        energy_range = []
        
        optimization_type = 'daily' if self.optimization_type.currentText() == 'Diaria' else 'annual'
        day_of_year = self.day_of_year.value()
        
        for a in angle_range:
            if optimization_type == 'daily':
                e = self.solar_model.daily_energy(a, day_of_year)
            else:
                e = self.solar_model.annual_energy(a)
            energy_range.append(e)
        
        ax.plot(angle_range, energy_range, 'b-', linewidth=2, label='Función objetivo')
        
        # Puntos de evaluación
        ax.scatter(angles, energies, c='red', s=50, alpha=0.7, label='Evaluaciones')
        
        # Punto óptimo
        ax.scatter([angle], [energy], c='green', s=100, marker='*', 
                  label=f'Óptimo: {angle:.1f}°', zorder=5)
        
        ax.set_xlabel('Ángulo de inclinación (°)')
        unit = 'Wh' if self.optimization_type.currentText() == 'Diaria' else 'kWh'
        ax.set_ylabel(f'Energía ({unit})')
        ax.set_title(f'Optimización: {self.method_combo.currentText()}')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def plot_method_comparison(self, results):
        """Graficar comparación de métodos."""
        ax = self.optimization_canvas.fig.add_subplot(111)
        
        methods = []
        angles = []
        energies = []
        evaluations = []
        
        for method, data in results.items():
            if 'error' not in data:
                methods.append(method.replace('_', ' ').title())
                angles.append(data['angle'])
                energies.append(data['energy'])
                evaluations.append(data['evaluations'])
        
        # Gráfica de barras para ángulos óptimos
        x = np.arange(len(methods))
        bars = ax.bar(x, angles, color=['#FF9999', '#66B2FF', '#99FF99', '#FFCC99'])
        
        ax.set_xlabel('Método de optimización')
        ax.set_ylabel('Ángulo óptimo (°)')
        ax.set_title('Comparación de métodos: Ángulos óptimos')
        ax.set_xticks(x)
        ax.set_xticklabels(methods, rotation=45, ha='right')
        
        # Agregar valores sobre las barras
        for i, (bar, angle, energy, evals) in enumerate(zip(bars, angles, energies, evaluations)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{angle:.1f}°\n({evals} eval.)',
                   ha='center', va='bottom', fontsize=9)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
    
    def run_sensitivity_analysis(self):
        """Ejecutar análisis de sensibilidad."""
        if not self.optimization_results:
            return
        
        try:
            results = self.optimization_results
            
            # Obtener ángulo óptimo
            if isinstance(results, dict) and 'brute_force' in results:
                # Usar mejor resultado de la comparación
                best_method = max(results.keys(), 
                                key=lambda k: results[k].get('energy', 0) if 'error' not in results[k] else 0)
                optimal_angle = results[best_method]['angle']
            else:
                optimal_angle = results[0]
            
            # Ejecutar análisis
            optimization_type = 'daily' if self.optimization_type.currentText() == 'Diaria' else 'annual'
            day_of_year = self.day_of_year.value()
            
            sensitivity_data = self.optimizer.sensitivity_analysis(
                optimal_angle, 20, optimization_type, day_of_year)
            
            # Graficar análisis de sensibilidad
            self.plot_sensitivity_analysis(sensitivity_data, optimal_angle)
            
            # Cambiar a pestaña de análisis
            self.tabs.setCurrentIndex(2)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en análisis de sensibilidad: {str(e)}")
    
    def plot_sensitivity_analysis(self, sensitivity_data, optimal_angle):
        """Graficar análisis de sensibilidad."""
        self.analysis_canvas.fig.clear()
        
        angles = [data[0] for data in sensitivity_data]
        energies = [data[1] for data in sensitivity_data]
        losses = [data[2] for data in sensitivity_data]
        
        # Crear subplots
        ax1 = self.analysis_canvas.fig.add_subplot(211)
        ax2 = self.analysis_canvas.fig.add_subplot(212)
        
        # Gráfica de energía vs ángulo
        ax1.plot(angles, energies, 'b-', linewidth=2, marker='o')
        ax1.axvline(optimal_angle, color='red', linestyle='--', label=f'Óptimo: {optimal_angle:.1f}°')
        ax1.set_xlabel('Ángulo de inclinación (°)')
        unit = 'Wh' if self.optimization_type.currentText() == 'Diaria' else 'kWh'
        ax1.set_ylabel(f'Energía ({unit})')
        ax1.set_title('Análisis de Sensibilidad')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Gráfica de pérdida porcentual
        ax2.plot(angles, losses, 'r-', linewidth=2, marker='s')
        ax2.axhline(0, color='green', linestyle='--', alpha=0.7)
        ax2.set_xlabel('Ángulo de inclinación (°)')
        ax2.set_ylabel('Pérdida de energía (%)')
        ax2.set_title('Pérdida de Energía vs Ángulo Óptimo')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self.analysis_canvas.draw()
    
    def clear_results(self):
        """Limpiar resultados y gráficas."""
        self.results_text.clear()
        self.optimization_results = {}
        self.analysis_button.setEnabled(False)
        
        # Limpiar canvas
        self.optimization_canvas.fig.clear()
        self.comparison_canvas.fig.clear()
        self.analysis_canvas.fig.clear()
        
        self.optimization_canvas.draw()
        self.comparison_canvas.draw()
        self.analysis_canvas.draw()
        
        self.statusBar().showMessage("Resultados limpiados")


def main():
    """Función principal para ejecutar la aplicación."""
    app = QApplication(sys.argv)
    
    # Configurar estilo de la aplicación
    app.setStyle('Fusion')
    
    # Crear y mostrar ventana principal
    window = SolarPanelGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

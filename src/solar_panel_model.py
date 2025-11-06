"""
Modelo matemático para panel solar y cálculo de energía captada.
Este módulo contiene las funciones para calcular la radiación solar
y la energía captada por un panel solar en función de su inclinación.
"""

import numpy as np
import math
from datetime import datetime, timedelta


class SolarPanelModel:
    """
    Clase para modelar el comportamiento de un panel solar y calcular
    la energía captada basada en parámetros geográficos y de inclinación.
    """
    
    def __init__(self, latitude, panel_area=1.0, efficiency=0.2):
        """
        Inicializa el modelo del panel solar.
        
        Args:
            latitude (float): Latitud geográfica en grados
            panel_area (float): Área del panel en m²
            efficiency (float): Eficiencia del panel (0-1)
        """
        self.latitude = math.radians(latitude)  # Convertir a radianes
        self.panel_area = panel_area
        self.efficiency = efficiency
        
        # Constantes solares
        self.solar_constant = 1367  # W/m² (constante solar)
        self.atmosphere_factor = 0.7  # Factor de atenuación atmosférica
    
    def solar_declination(self, day_of_year):
        """
        Calcula la declinación solar para un día dado del año.
        
        Args:
            day_of_year (int): Día del año (1-365)
            
        Returns:
            float: Declinación solar en radianes
        """
        return math.radians(23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365)))
    
    def hour_angle(self, hour):
        """
        Calcula el ángulo horario para una hora dada.
        
        Args:
            hour (float): Hora del día (0-24)
            
        Returns:
            float: Ángulo horario en radianes
        """
        return math.radians(15 * (hour - 12))
    
    def solar_elevation_angle(self, declination, hour_angle):
        """
        Calcula el ángulo de elevación solar.
        
        Args:
            declination (float): Declinación solar en radianes
            hour_angle (float): Ángulo horario en radianes
            
        Returns:
            float: Ángulo de elevación solar en radianes
        """
        sin_elevation = (math.sin(self.latitude) * math.sin(declination) +
                        math.cos(self.latitude) * math.cos(declination) * math.cos(hour_angle))
        return math.asin(max(0, sin_elevation))
    
    def solar_azimuth_angle(self, declination, hour_angle, elevation):
        """
        Calcula el ángulo azimutal del sol.
        
        Args:
            declination (float): Declinación solar en radianes
            hour_angle (float): Ángulo horario en radianes
            elevation (float): Ángulo de elevación solar en radianes
            
        Returns:
            float: Ángulo azimutal en radianes
        """
        if elevation <= 0:
            return 0
        
        cos_azimuth = ((math.sin(declination) * math.cos(self.latitude) -
                       math.cos(declination) * math.sin(self.latitude) * math.cos(hour_angle)) /
                      math.cos(elevation))
        
        cos_azimuth = max(-1, min(1, cos_azimuth))  # Limitar entre -1 y 1
        azimuth = math.acos(cos_azimuth)
        
        # Ajustar el signo basado en el ángulo horario
        if hour_angle > 0:
            azimuth = 2 * math.pi - azimuth
            
        return azimuth
    
    def incidence_angle(self, elevation, azimuth, panel_tilt, panel_azimuth=math.pi):
        """
        Calcula el ángulo de incidencia de la radiación solar sobre el panel.
        
        Args:
            elevation (float): Ángulo de elevación solar en radianes
            azimuth (float): Ángulo azimutal solar en radianes
            panel_tilt (float): Ángulo de inclinación del panel en radianes
            panel_azimuth (float): Ángulo azimutal del panel en radianes (por defecto sur)
            
        Returns:
            float: Ángulo de incidencia en radianes
        """
        cos_incidence = (math.sin(elevation) * math.cos(panel_tilt) +
                        math.cos(elevation) * math.sin(panel_tilt) *
                        math.cos(azimuth - panel_azimuth))
        
        return math.acos(max(0, min(1, cos_incidence)))
    
    def direct_normal_irradiance(self, elevation):
        """
        Calcula la irradiancia directa normal basada en el ángulo de elevación.
        
        Args:
            elevation (float): Ángulo de elevación solar en radianes
            
        Returns:
            float: Irradiancia directa normal en W/m²
        """
        if elevation <= 0:
            return 0
        
        # Modelo simple de irradiancia directa
        air_mass = 1 / math.sin(elevation)
        
        # Limitar la masa de aire para evitar valores extremos
        air_mass = min(air_mass, 10)
        
        dni = self.solar_constant * self.atmosphere_factor ** air_mass
        return max(0, dni)
    
    def total_irradiance_on_panel(self, dni, incidence_angle, elevation):
        """
        Calcula la irradiancia total sobre el panel inclinado.
        
        Args:
            dni (float): Irradiancia directa normal en W/m²
            incidence_angle (float): Ángulo de incidencia en radianes
            elevation (float): Ángulo de elevación solar en radianes
            
        Returns:
            float: Irradiancia total sobre el panel en W/m²
        """
        if elevation <= 0 or incidence_angle >= math.pi/2:
            return 0
        
        # Componente directa
        direct_component = dni * math.cos(incidence_angle)
        
        # Componente difusa (aproximación simple)
        diffuse_component = 0.1 * dni
        
        # Componente reflejada del suelo (albedo = 0.2)
        ground_reflected = 0.2 * dni * math.sin(elevation) * 0.5
        
        return max(0, direct_component + diffuse_component + ground_reflected)
    
    def instantaneous_power(self, panel_tilt, day_of_year, hour):
        """
        Calcula la potencia instantánea generada por el panel.
        
        Args:
            panel_tilt (float): Ángulo de inclinación del panel en grados
            day_of_year (int): Día del año (1-365)
            hour (float): Hora del día (0-24)
            
        Returns:
            float: Potencia instantánea en vatios
        """
        panel_tilt_rad = math.radians(panel_tilt)
        declination = self.solar_declination(day_of_year)
        h_angle = self.hour_angle(hour)
        elevation = self.solar_elevation_angle(declination, h_angle)
        
        if elevation <= 0:
            return 0
        
        azimuth = self.solar_azimuth_angle(declination, h_angle, elevation)
        incidence = self.incidence_angle(elevation, azimuth, panel_tilt_rad)
        dni = self.direct_normal_irradiance(elevation)
        irradiance = self.total_irradiance_on_panel(dni, incidence, elevation)
        
        return irradiance * self.panel_area * self.efficiency
    
    def daily_energy(self, panel_tilt, day_of_year, time_step=0.5):
        """
        Calcula la energía total generada en un día.
        
        Args:
            panel_tilt (float): Ángulo de inclinación del panel en grados
            day_of_year (int): Día del año (1-365)
            time_step (float): Paso de tiempo en horas para la integración
            
        Returns:
            float: Energía total en Wh
        """
        total_energy = 0
        hours = np.arange(6, 18 + time_step, time_step)  # De 6 AM a 6 PM
        
        for hour in hours:
            power = self.instantaneous_power(panel_tilt, day_of_year, hour)
            total_energy += power * time_step
        
        return total_energy
    
    def annual_energy(self, panel_tilt, time_step=0.5):
        """
        Calcula la energía total generada en un año.
        
        Args:
            panel_tilt (float): Ángulo de inclinación del panel en grados
            time_step (float): Paso de tiempo en horas para la integración diaria
            
        Returns:
            float: Energía total anual en kWh
        """
        total_energy = 0
        
        # Calcular para días representativos de cada mes
        representative_days = [17, 47, 75, 105, 135, 162, 198, 230, 266, 296, 326, 356]
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        
        for i, day in enumerate(representative_days):
            daily_energy = self.daily_energy(panel_tilt, day, time_step)
            total_energy += daily_energy * days_in_month[i]
        
        return total_energy / 1000  # Convertir a kWh
    
    def get_optimal_angles_range(self):
        """
        Retorna el rango recomendado de ángulos para la optimización.
        
        Returns:
            tuple: (ángulo_mínimo, ángulo_máximo) en grados
        """
        lat_deg = math.degrees(self.latitude)
        min_angle = max(0, lat_deg - 20)
        max_angle = min(90, lat_deg + 20)
        return min_angle, max_angle

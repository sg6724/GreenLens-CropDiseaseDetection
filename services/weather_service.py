import requests
from config import WEATHER_API_KEY, WEATHER_DISEASE_RULES

class WeatherService:
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.base_url = "http://api.weatherapi.com/v1"
    
    def get_weather_data(self, location):
        """Get current weather data for location"""
        try:
            url = f"{self.base_url}/current.json"
            params = {
                'key': self.api_key,
                'q': location,
                'aqi': 'no'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'location': data['location']['name'],
                'country': data['location']['country'],
                'temperature': data['current']['temp_c'],
                'humidity': data['current']['humidity'],
                'condition': data['current']['condition']['text'],
                'wind_speed': data['current']['wind_kph'],
                'pressure': data['current']['pressure_mb'],
                'visibility': data['current']['vis_km'],
                'uv_index': data['current']['uv'],
                'last_updated': data['current']['last_updated']
            }
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def get_forecast(self, location, days=3):
        """Get weather forecast for location"""
        try:
            url = f"{self.base_url}/forecast.json"
            params = {
                'key': self.api_key,
                'q': location,
                'days': days,
                'aqi': 'no',
                'alerts': 'no'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            forecast = []
            for day in data['forecast']['forecastday']:
                forecast.append({
                    'date': day['date'],
                    'max_temp': day['day']['maxtemp_c'],
                    'min_temp': day['day']['mintemp_c'],
                    'avg_temp': day['day']['avgtemp_c'],
                    'humidity': day['day']['avghumidity'],
                    'condition': day['day']['condition']['text'],
                    'rain_chance': day['day']['daily_chance_of_rain'],
                    'rain_mm': day['day']['totalprecip_mm']
                })
            
            return forecast
            
        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None
    
    def assess_disease_risk(self, disease_name, weather_data):
        """Assess disease risk based on weather conditions"""
        try:
            if not weather_data or disease_name not in WEATHER_DISEASE_RULES:
                return {
                    'risk_level': 'unknown',
                    'assessment': 'Unable to assess risk for this disease.',
                    'recommendations': []
                }
            
            rules = WEATHER_DISEASE_RULES[disease_name]
            current_temp = weather_data['temperature']
            current_humidity = weather_data['humidity']
            
            risk_factors = []
            recommendations = []
            
            # Temperature assessment
            temp_range = rules['favorable_temp']
            if temp_range[0] <= current_temp <= temp_range[1]:
                risk_factors.append("Temperature is favorable for disease development")
                recommendations.append("Monitor crops closely as temperature conditions favor disease spread")
            else:
                recommendations.append("Temperature conditions are not ideal for disease development")
            
            # Humidity assessment
            humidity_range = rules['favorable_humidity']
            if humidity_range[0] <= current_humidity <= humidity_range[1]:
                risk_factors.append("Humidity is favorable for disease development")
                recommendations.append("Ensure good air circulation and avoid overwatering")
            else:
                recommendations.append("Humidity levels are not conducive to disease spread")
            
            # Rain assessment
            if rules['rain_risk'] and 'rain' in weather_data['condition'].lower():
                risk_factors.append("Rainy conditions increase disease risk")
                recommendations.append("Apply preventive treatments before rain if possible")
                recommendations.append("Ensure proper drainage to prevent waterlogging")
            
            # Overall risk assessment
            if len(risk_factors) >= 2:
                risk_level = 'high'
                assessment = "Current weather conditions are highly favorable for disease development and spread."
            elif len(risk_factors) == 1:
                risk_level = 'moderate'
                assessment = "Weather conditions are somewhat favorable for disease development."
            else:
                risk_level = 'low'
                assessment = "Current weather conditions are not particularly favorable for disease development."
            
            return {
                'risk_level': risk_level,
                'assessment': assessment,
                'risk_factors': risk_factors,
                'recommendations': recommendations,
                'weather_summary': f"Temperature: {current_temp}°C, Humidity: {current_humidity}%, Condition: {weather_data['condition']}"
            }
            
        except Exception as e:
            print(f"Error assessing disease risk: {e}")
            return {
                'risk_level': 'unknown',
                'assessment': f'Error assessing risk: {str(e)}',
                'recommendations': []
            }

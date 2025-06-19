"""
Location processing service integrating Wikipedia API and OpenAI.
"""

import json
import logging
import math
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import openai
from src.config import Config
from src.wikipedia_parser import WikipediaParser

logger = logging.getLogger(__name__)


@dataclass
class LocationResult:
    """Result of location processing."""
    place_name: str
    distance: float  # in kilometers
    coordinates: Dict[str, float]
    interesting_fact: str
    wikipedia_url: Optional[str] = None


class LocationService:
    """Service for processing location and generating interesting facts."""
    
    def __init__(self) -> None:
        """Initialize location service."""
        self.config = Config()
        self.openai_client = openai.AsyncOpenAI(api_key=self.config.OPENAI_API_KEY)
        self.wikipedia_parser = WikipediaParser()
        
        # Load landmarks dataset
        self.landmarks_data = self._load_landmarks_data()
        
    def _load_landmarks_data(self) -> List[Dict[str, Any]]:
        """Load landmarks dataset from JSON file."""
        try:
            with open('data/test_landmarks.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('locations', [])
        except FileNotFoundError:
            logger.warning("Landmarks dataset not found. Using empty dataset.")
            return []
        except Exception as e:
            logger.error(f"Error loading landmarks dataset: {e}")
            return []
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula."""
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Earth radius in kilometers
        
        return c * r
    
    def _find_nearest_landmark(self, latitude: float, longitude: float, 
                             max_distance: float = 10.0) -> Optional[Dict[str, Any]]:
        """Find the nearest landmark within specified distance."""
        nearest_landmark = None
        min_distance = float('inf')
        
        for landmark in self.landmarks_data:
            landmark_lat = landmark['coordinates']['lat']
            landmark_lon = landmark['coordinates']['lon']
            
            distance = self._calculate_distance(latitude, longitude, landmark_lat, landmark_lon)
            
            if distance <= max_distance and distance < min_distance:
                min_distance = distance
                nearest_landmark = landmark.copy()
                nearest_landmark['distance'] = distance
        
        return nearest_landmark
    
    async def _generate_interesting_fact(self, landmark: Dict[str, Any], 
                                       user_coordinates: Dict[str, float]) -> str:
        """Generate interesting fact about the landmark using OpenAI."""
        place_name = landmark['name']
        description = landmark.get('description', '')
        place_type = landmark.get('type', 'достопримечательность')
        country = landmark.get('country', 'Unknown')
        city = landmark.get('city', 'Unknown')
        
        prompt = (
            f"Ты эксперт по истории и культуре. Расскажи один интересный, необычный "
            f"или малоизвестный факт о месте '{place_name}' "
            f"({'в ' + city if city != 'Unknown' else ''}"
            f"{', ' + country if country != 'Unknown' else ''}).\n\n"
            f"Тип места: {place_type}\n"
            f"Краткое описание: {description[:300]}...\n\n"
            f"Требования:\n"
            f"- Факт должен быть интересным и увлекательным\n"
            f"- Длина ответа: 2-3 предложения (максимум 200 символов)\n"
            f"- Используй простой и понятный язык\n"
            f"- Начни прямо с факта, без вводных слов\n"
            f"- Не упоминай координаты или техническую информацию"
        )
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Ты увлекательный гид, который знает интересные факты о достопримечательностях."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            fact = response.choices[0].message.content.strip()
            
            # Log for analysis
            logger.info(f"Generated fact for {place_name}: {fact[:100]}...")
            
            return fact
            
        except Exception as e:
            logger.error(f"Error generating fact with OpenAI: {e}")
            
            # Fallback to description if OpenAI fails
            if description:
                return f"Это {place_type.lower()} {description[:150]}..."
            else:
                return f"Это интересное место - {place_name}."
    
    async def process_location(self, latitude: float, longitude: float, 
                             user_id: int) -> Optional[Dict[str, Any]]:
        """Process user location and return interesting fact about nearby place."""
        logger.info(f"Processing location for user {user_id}: lat={latitude}, lon={longitude}")
        
        # Find nearest landmark
        nearest_landmark = self._find_nearest_landmark(latitude, longitude)
        
        if not nearest_landmark:
            logger.info(f"No landmarks found near {latitude}, {longitude}")
            return None
        
        # Generate interesting fact
        try:
            interesting_fact = await self._generate_interesting_fact(
                nearest_landmark, 
                {'lat': latitude, 'lon': longitude}
            )
            
            result = {
                'place_name': nearest_landmark['name'],
                'distance': nearest_landmark['distance'],
                'coordinates': nearest_landmark['coordinates'],
                'interesting_fact': interesting_fact,
                'wikipedia_url': nearest_landmark.get('wikipedia_url'),
                'place_type': nearest_landmark.get('type', 'достопримечательность')
            }
            
            # Log result for analysis
            self._log_processing_result(user_id, latitude, longitude, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing location for user {user_id}: {e}")
            return None
    
    def _log_processing_result(self, user_id: int, lat: float, lon: float, 
                             result: Dict[str, Any]) -> None:
        """Log processing result for analysis."""
        log_entry = {
            'user_id': user_id,
            'input_coordinates': {'lat': lat, 'lon': lon},
            'found_place': result['place_name'],
            'distance': result['distance'],
            'place_coordinates': result['coordinates'],
            'generated_fact': result['interesting_fact'][:100] + '...'  # Truncate for logs
        }
        
        logger.info(f"Location processing result: {json.dumps(log_entry, ensure_ascii=False)}") 
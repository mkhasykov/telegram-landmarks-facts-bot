"""
Wikipedia Parser for extracting landmark data with coordinates.
"""

import json
import logging
import argparse
from typing import List, Dict, Optional, Any
from datetime import datetime
import requests
import time


class WikipediaParser:
    """Parser for extracting landmark data from Wikipedia API."""
    
    def __init__(self) -> None:
        self.base_url = "https://ru.wikipedia.org/w/api.php"
        self.en_base_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TelegramLocationBot/1.0 (https://github.com/user/repo)'
        })
        
    def get_category_pages(self, category: str, limit: int = 50, lang: str = "ru") -> List[str]:
        """Получить список страниц из категории."""
        base_url = self.base_url if lang == "ru" else self.en_base_url
        
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': f'Category:{category}' if lang == "en" else f'Категория:{category}',
            'cmlimit': limit,
            'format': 'json',
            'cmnamespace': 0  # Only main namespace (articles)
        }
        
        try:
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = []
            if 'query' in data and 'categorymembers' in data['query']:
                pages = [page['title'] for page in data['query']['categorymembers']]
                
            logging.info(f"Found {len(pages)} pages in category '{category}'")
            return pages
            
        except requests.RequestException as e:
            logging.error(f"Error fetching category pages: {e}")
            return []
    
    def get_page_coordinates(self, page_title: str, lang: str = "ru") -> Optional[Dict[str, float]]:
        """Извлечь координаты страницы."""
        base_url = self.base_url if lang == "ru" else self.en_base_url
        
        params = {
            'action': 'query',
            'titles': page_title,
            'prop': 'coordinates',
            'format': 'json'
        }
        
        try:
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'query' in data and 'pages' in data['query']:
                for page_id, page_data in data['query']['pages'].items():
                    if 'coordinates' in page_data and page_data['coordinates']:
                        coord = page_data['coordinates'][0]
                        return {
                            'lat': coord['lat'],
                            'lon': coord['lon']
                        }
            return None
            
        except requests.RequestException as e:
            logging.error(f"Error fetching coordinates for '{page_title}': {e}")
            return None
    
    def get_page_extract(self, page_title: str, lang: str = "ru") -> str:
        """Получить краткое описание страницы."""
        base_url = self.base_url if lang == "ru" else self.en_base_url
        
        params = {
            'action': 'query',
            'titles': page_title,
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True,
            'exsectionformat': 'plain',
            'format': 'json'
        }
        
        try:
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'query' in data and 'pages' in data['query']:
                for page_id, page_data in data['query']['pages'].items():
                    if 'extract' in page_data:
                        # Limit extract to first 500 characters
                        extract = page_data['extract'][:500]
                        if len(page_data['extract']) > 500:
                            extract += "..."
                        return extract
            return ""
            
        except requests.RequestException as e:
            logging.error(f"Error fetching extract for '{page_title}': {e}")
            return ""
    
    def get_page_categories(self, page_title: str, lang: str = "ru") -> List[str]:
        """Получить категории страницы."""
        base_url = self.base_url if lang == "ru" else self.en_base_url
        
        params = {
            'action': 'query',
            'titles': page_title,
            'prop': 'categories',
            'format': 'json'
        }
        
        try:
            response = self.session.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            categories = []
            if 'query' in data and 'pages' in data['query']:
                for page_id, page_data in data['query']['pages'].items():
                    if 'categories' in page_data:
                        categories = [cat['title'].replace('Категория:', '').replace('Category:', '') 
                                    for cat in page_data['categories']]
            return categories
            
        except requests.RequestException as e:
            logging.error(f"Error fetching categories for '{page_title}': {e}")
            return []
    
    def validate_coordinates(self, coordinates: Dict[str, float]) -> bool:
        """Валидация координат."""
        lat = coordinates.get('lat')
        lon = coordinates.get('lon')
        
        if lat is None or lon is None:
            return False
            
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    def classify_place_type(self, categories: List[str], title: str) -> str:
        """Определить тип места по категориям."""
        title_lower = title.lower()
        categories_lower = [cat.lower() for cat in categories]
        
        # Mapping categories to place types
        if any(word in title_lower for word in ['музей', 'museum']):
            return 'музей'
        elif any(word in title_lower for word in ['парк', 'park', 'сад', 'garden']):
            return 'парк'
        elif any(word in title_lower for word in ['памятник', 'monument']):
            return 'памятник'
        elif any(word in title_lower for word in ['церковь', 'собор', 'храм', 'church', 'cathedral']):
            return 'религиозное строение'
        elif any(word in title_lower for word in ['площадь', 'square']):
            return 'площадь'
        elif any(word in title_lower for word in ['театр', 'theater', 'theatre']):
            return 'театр'
        elif any(word in title_lower for word in ['дворец', 'palace']):
            return 'дворец'
        else:
            return 'достопримечательность'
    
    def parse_landmark_data(self, page_title: str, lang: str = "ru") -> Optional[Dict[str, Any]]:
        """Полная информация о достопримечательности."""
        coordinates = self.get_page_coordinates(page_title, lang)
        if not coordinates or not self.validate_coordinates(coordinates):
            return None
        
        extract = self.get_page_extract(page_title, lang)
        if not extract.strip():
            return None
        
        categories = self.get_page_categories(page_title, lang)
        place_type = self.classify_place_type(categories, page_title)
        
        # Determine country and city from categories or extract
        country = "Unknown"
        city = "Unknown"
        
        for cat in categories:
            if 'москв' in cat.lower() or 'moscow' in cat.lower():
                country = "Россия"
                city = "Москва"
                break
            elif 'петербург' in cat.lower() or 'petersburg' in cat.lower():
                country = "Россия"
                city = "Санкт-Петербург"
                break
            elif 'париж' in cat.lower() or 'paris' in cat.lower():
                country = "Франция"
                city = "Париж"
                break
            elif 'нью-йорк' in cat.lower() or 'new york' in cat.lower():
                country = "США"
                city = "Нью-Йорк"
                break
            elif 'рим' in cat.lower() or 'rome' in cat.lower():
                country = "Италия"
                city = "Рим"
                break
        
        base_url = self.base_url if lang == "ru" else self.en_base_url
        wiki_url = f"{base_url.replace('/w/api.php', '/wiki/')}{page_title.replace(' ', '_')}"
        
        return {
            'name': page_title,
            'coordinates': coordinates,
            'description': extract,
            'categories': categories,
            'wikipedia_url': wiki_url,
            'country': country,
            'city': city,
            'type': place_type,
            'language': lang
        }
    
    def generate_test_dataset(self, categories: List[str], output_file: str, 
                            limit_per_category: int = 10) -> None:
        """Создать тестовый датасет и сохранить в JSON."""
        logging.info(f"Starting dataset generation for {len(categories)} categories")
        
        all_landmarks = []
        landmark_id = 1
        
        for category in categories:
            logging.info(f"Processing category: {category}")
            
            # Determine language based on category name
            lang = "en" if any(eng_word in category.lower() 
                             for eng_word in ['tourist', 'attractions', 'landmarks', 'sites']) else "ru"
            
            pages = self.get_category_pages(category, limit_per_category * 2, lang)
            
            for page_title in pages[:limit_per_category]:
                landmark_data = self.parse_landmark_data(page_title, lang)
                if landmark_data:
                    landmark_data['id'] = landmark_id
                    all_landmarks.append(landmark_data)
                    landmark_id += 1
                    logging.info(f"Added landmark: {page_title}")
                
                # Rate limiting
                time.sleep(0.1)
        
        # Remove duplicates based on coordinates
        unique_landmarks = []
        seen_coords = set()
        
        for landmark in all_landmarks:
            coord_key = (
                round(landmark['coordinates']['lat'], 4),
                round(landmark['coordinates']['lon'], 4)
            )
            if coord_key not in seen_coords:
                seen_coords.add(coord_key)
                unique_landmarks.append(landmark)
        
        # Create final dataset
        dataset = {
            'generated_at': datetime.now().isoformat(),
            'source': 'Wikipedia API',
            'total_locations': len(unique_landmarks),
            'categories_processed': categories,
            'locations': unique_landmarks
        }
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Dataset saved to {output_file} with {len(unique_landmarks)} unique landmarks")


# Configuration for different categories
CATEGORIES_CONFIG = {
    "russian": [
        "Достопримечательности Москвы",
        "Достопримечательности Санкт-Петербурга",
        "Музеи России",
        "Памятники России",
        "Театры России",
        "Дворцы России"
    ],
    "world": [
        "World Heritage Sites",
        "Tourist attractions in Paris",
        "Landmarks in New York City",
        "Tourist attractions in Rome",
        "Museums in London",
        "Palaces"
    ]
}


def main() -> None:
    """CLI interface for Wikipedia parser."""
    parser = argparse.ArgumentParser(description="Parse Wikipedia landmarks data")
    parser.add_argument(
        "--categories",
        choices=["russian", "world", "all"],
        default="russian",
        help="Categories to parse"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit per category"
    )
    parser.add_argument(
        "--output",
        default="data/landmarks_dataset.json",
        help="Output file path"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get categories to process
    if args.categories == "all":
        categories = CATEGORIES_CONFIG["russian"] + CATEGORIES_CONFIG["world"]
    else:
        categories = CATEGORIES_CONFIG[args.categories]
    
    # Initialize parser and generate dataset
    wiki_parser = WikipediaParser()
    wiki_parser.generate_test_dataset(categories, args.output, args.limit)
    
    print(f"Dataset generation completed. Output saved to: {args.output}")


if __name__ == "__main__":
    main() 
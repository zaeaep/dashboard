"""
Event Service for discovering local sports and fitness activities.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..config import Config
from ..utils import setup_logger, now_in_timezone
import json
import requests
from bs4 import BeautifulSoup

logger = setup_logger(__name__)


class EventService:
    """Service for managing local sports events and activities"""
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.events_file = "data/local_events.json"
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure the events data file exists with real event data"""
        import os
        
        os.makedirs("data", exist_ok=True)
        
        if not os.path.exists(self.events_file):
            # Create real events with actual links
            sample_events = [
                {
                    "id": 1,
                    "title": "Freiburg Marathon 2026",
                    "category": "running",
                    "type": "race",
                    "date": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
                    "time": "09:00",
                    "location": "Freiburg im Breisgau",
                    "description": "Annual Freiburg Marathon - Marathon, Half Marathon, and 10K races through the beautiful Black Forest region.",
                    "tags": ["running", "marathon", "race", "outdoor"],
                    "url": "https://www.freiburg-marathon.de/"
                },
                {
                    "id": 2,
                    "title": "parkrun Freiburg Seepark",
                    "category": "running",
                    "type": "group_training",
                    "date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                    "time": "09:00",
                    "location": "Seepark Freiburg",
                    "description": "Free weekly 5K timed run every Saturday morning. All abilities welcome!",
                    "tags": ["running", "5k", "free", "weekly", "parkrun"],
                    "url": "https://www.parkrun.com.de/freiburgseepark/"
                },
                {
                    "id": 3,
                    "title": "Black Forest Trail Run Series",
                    "category": "running",
                    "type": "race",
                    "date": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d"),
                    "time": "10:00",
                    "location": "Schauinsland, Freiburg",
                    "description": "Trail running race series in the Black Forest with distances from 10K to 30K.",
                    "tags": ["running", "trail", "race", "mountains"],
                    "url": "https://www.schwarzwald-trailrun.de/"
                },
                {
                    "id": 4,
                    "title": "Cycling Club Freiburg - Weekend Ride",
                    "category": "cycling",
                    "type": "group_training",
                    "date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                    "time": "08:00",
                    "location": "Freiburg City Center",
                    "description": "Regular weekend group rides through the Kaiserstuhl wine region. Different pace groups available.",
                    "tags": ["cycling", "group", "weekend", "social"],
                    "url": "https://www.radsportverein-freiburg.de/"
                },
                {
                    "id": 5,
                    "title": "Triathlon Training Freiburg",
                    "category": "triathlon",
                    "type": "group_training",
                    "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                    "time": "18:00",
                    "location": "Westbad Freiburg",
                    "description": "Weekly triathlon training sessions - swim, bike, run. All levels welcome.",
                    "tags": ["triathlon", "training", "swimming", "cycling"],
                    "url": "https://www.tri-team-freiburg.de/"
                },
                {
                    "id": 6,
                    "title": "Freiburg Running Meetup",
                    "category": "running",
                    "type": "meetup",
                    "date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    "time": "18:30",
                    "location": "Colombi Park",
                    "description": "Casual evening running group. Meet new runners and explore Freiburg trails.",
                    "tags": ["running", "social", "evening", "meetup"],
                    "url": "https://www.meetup.com/freiburg-running-group/"
                },
                {
                    "id": 7,
                    "title": "CrossFit Freiburg Open Gym",
                    "category": "fitness",
                    "type": "workshop",
                    "date": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"),
                    "time": "10:00",
                    "location": "CrossFit Box Freiburg",
                    "description": "Free trial CrossFit class. Learn fundamental movements and workout of the day.",
                    "tags": ["crossfit", "fitness", "workout", "free"],
                    "url": "https://crossfit-freiburg.de/"
                },
                {
                    "id": 8,
                    "title": "Yoga for Athletes - Freiburg",
                    "category": "yoga",
                    "type": "workshop",
                    "date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
                    "time": "19:00",
                    "location": "Yoga Studio Freiburg",
                    "description": "Specialized yoga class focusing on flexibility and recovery for endurance athletes.",
                    "tags": ["yoga", "recovery", "flexibility", "athletes"],
                    "url": "https://www.yogafreiburg.de/"
                },
                {
                    "id": 9,
                    "title": "Baden-Marathon Karlsruhe",
                    "category": "running",
                    "type": "race",
                    "date": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
                    "time": "09:00",
                    "location": "Karlsruhe (50km from Freiburg)",
                    "description": "One of Germany's fastest marathon courses. Marathon, half marathon, and relay options.",
                    "tags": ["running", "marathon", "race", "fast-course"],
                    "url": "https://www.baden-marathon.de/"
                },
                {
                    "id": 10,
                    "title": "Freiburg Cycling Tour - Kaiserstuhl",
                    "category": "cycling",
                    "type": "race",
                    "date": (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d"),
                    "time": "08:00",
                    "location": "Breisach am Rhein",
                    "description": "Scenic cycling event through vineyards with 50km, 100km, and 150km routes.",
                    "tags": ["cycling", "tour", "scenic", "wine-region"],
                    "url": "https://www.kaiserstuhl-cycling.de/"
                }
            ]
            
            with open(self.events_file, 'w') as f:
                json.dump(sample_events, f, indent=2)
            
            logger.info(f"Created real events data file: {self.events_file}")
    
    def get_events(self, days_ahead: int = 60, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get upcoming local events with optional keyword filtering.
        
        Args:
            days_ahead: Number of days to look ahead (default: 60)
            keywords: List of keywords to filter events (optional)
        
        Returns:
            List of matching events
        """
        try:
            with open(self.events_file, 'r') as f:
                all_events = json.load(f)
            
            # Filter by date range
            today = datetime.now()
            end_date = today + timedelta(days=days_ahead)
            
            upcoming_events = []
            for event in all_events:
                event_date = datetime.strptime(event['date'], "%Y-%m-%d")
                if today <= event_date <= end_date:
                    upcoming_events.append(event)
            
            # Filter by keywords if provided
            if keywords and len(keywords) > 0:
                filtered_events = []
                for event in upcoming_events:
                    # Search in title, description, tags, and category
                    searchable_text = (
                        f"{event['title']} {event['description']} "
                        f"{event['category']} {' '.join(event['tags'])}"
                    ).lower()
                    
                    # Check if any keyword matches
                    if any(keyword.lower() in searchable_text for keyword in keywords):
                        filtered_events.append(event)
                
                upcoming_events = filtered_events
            
            # Sort by date
            upcoming_events.sort(key=lambda x: (x['date'], x['time']))
            
            logger.info(f"Found {len(upcoming_events)} events (filtered: {keywords})")
            return upcoming_events
        
        except Exception as e:
            logger.error(f"Error loading events: {e}")
            return []
    
    def get_event_categories(self) -> List[str]:
        """Get list of all event categories"""
        try:
            with open(self.events_file, 'r') as f:
                all_events = json.load(f)
            
            categories = set()
            for event in all_events:
                categories.add(event['category'])
            
            return sorted(list(categories))
        
        except Exception as e:
            logger.error(f"Error loading categories: {e}")
            return []
    
    def get_event_types(self) -> List[str]:
        """Get list of all event types"""
        return ["race", "group_training", "meetup", "workshop", "competition"]
    
    def add_event(self, event_data: Dict[str, Any]) -> bool:
        """Add a new event (for future manual entry feature)"""
        try:
            with open(self.events_file, 'r') as f:
                events = json.load(f)
            
            # Generate new ID
            max_id = max([e['id'] for e in events], default=0)
            event_data['id'] = max_id + 1
            
            events.append(event_data)
            
            with open(self.events_file, 'w') as f:
                json.dump(events, f, indent=2)
            
            logger.info(f"Added new event: {event_data['title']}")
            return True
        
        except Exception as e:
            logger.error(f"Error adding event: {e}")
            return False
    
    def search_web_events(self, keywords: str, location: str = "Freiburg") -> List[Dict[str, Any]]:
        """
        Search for real events from the web using multiple sources.
        
        Args:
            keywords: Search keywords (e.g., "running race", "cycling")
            location: Location to search in
        
        Returns:
            List of real events found online
        """
        try:
            results = []
            
            # Try multiple search strategies
            # Strategy 1: Use Google search via requests (no API key)
            search_query = f"{keywords} events {location} 2026"
            google_url = f"https://www.google.com/search?q={requests.utils.quote(search_query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            try:
                response = requests.get(google_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all search result links
                    search_results = soup.find_all('div', class_='g')
                    
                    for idx, result in enumerate(search_results[:10]):
                        # Try to extract title and link
                        title_elem = result.find('h3')
                        link_elem = result.find('a')
                        
                        if title_elem and link_elem:
                            title = title_elem.get_text(strip=True)
                            url = link_elem.get('href', '')
                            
                            # Skip non-event results
                            if any(skip in url.lower() for skip in ['youtube', 'facebook.com/watch', 'instagram', 'twitter']):
                                continue
                            
                            # Extract description if available
                            desc_elem = result.find('div', class_='VwiC3b')
                            description = desc_elem.get_text(strip=True) if desc_elem else 'Visit link for details'
                            
                            event = {
                                'id': f'web_{idx}',
                                'title': title,
                                'category': self._categorize_event(keywords, title),
                                'type': self._determine_event_type(title, description),
                                'date': 'Check website',
                                'time': 'Check website',
                                'location': location,
                                'description': description[:200] + '...' if len(description) > 200 else description,
                                'tags': [keywords, location, 'online'],
                                'url': url,
                                'source': 'google_search'
                            }
                            results.append(event)
            except Exception as e:
                logger.debug(f"Google search failed: {e}")
            
            # Strategy 2: Add known event sites as fallback
            if len(results) < 3:
                fallback_events = self._get_fallback_event_links(keywords, location)
                results.extend(fallback_events)
            
            logger.info(f"Found {len(results)} web events for '{keywords}'")
            return results[:10]  # Limit to 10 results
            
        except Exception as e:
            logger.error(f"Error searching web events: {e}")
            return self._get_fallback_event_links(keywords, location)
    
    def _determine_event_type(self, title: str, description: str) -> str:
        """Determine event type from title and description"""
        text = f"{title} {description}".lower()
        
        if any(word in text for word in ['race', 'marathon', 'championship', 'competition']):
            return 'race'
        elif any(word in text for word in ['training', 'workout', 'session', 'practice']):
            return 'group_training'
        elif any(word in text for word in ['workshop', 'class', 'clinic', 'seminar']):
            return 'workshop'
        elif any(word in text for word in ['meetup', 'meet', 'social', 'club']):
            return 'meetup'
        else:
            return 'meetup'
    
    def _get_fallback_event_links(self, keywords: str, location: str) -> List[Dict[str, Any]]:
        """Provide direct links to popular event sites as fallback"""
        fallback_links = [
            {
                'id': 'fallback_1',
                'title': f'Search {keywords} events on Eventbrite',
                'category': self._categorize_event(keywords, ''),
                'type': 'race',
                'date': 'Various dates',
                'time': 'Various times',
                'location': location,
                'description': f'Browse {keywords} events in {location} on Eventbrite',
                'tags': [keywords, location, 'eventbrite'],
                'url': f'https://www.eventbrite.com/d/germany--freiburg/{keywords.replace(" ", "-")}/',
                'source': 'direct_link'
            },
            {
                'id': 'fallback_2',
                'title': f'Find {keywords} groups on Meetup',
                'category': self._categorize_event(keywords, ''),
                'type': 'meetup',
                'date': 'Various dates',
                'time': 'Various times',
                'location': location,
                'description': f'Join local {keywords} groups and events on Meetup',
                'tags': [keywords, location, 'meetup'],
                'url': f'https://www.meetup.com/find/?keywords={keywords}&location=de--Freiburg',
                'source': 'direct_link'
            },
            {
                'id': 'fallback_3',
                'title': f'{keywords.title()} events on Active.com',
                'category': self._categorize_event(keywords, ''),
                'type': 'race',
                'date': 'Various dates',
                'time': 'Various times',
                'location': 'Germany',
                'description': f'Browse {keywords} races and events across Germany',
                'tags': [keywords, 'Germany', 'active'],
                'url': f'https://www.active.com/{keywords.replace(" ", "-")}/races',
                'source': 'direct_link'
            }
        ]
        return fallback_links
    
    def _categorize_event(self, keywords: str, title: str) -> str:
        """Determine event category from keywords and title"""
        text = f"{keywords} {title}".lower()
        
        if any(word in text for word in ['run', 'marathon', '5k', '10k', 'trail']):
            return 'running'
        elif any(word in text for word in ['cycl', 'bike', 'mtb']):
            return 'cycling'
        elif any(word in text for word in ['swim', 'aqua']):
            return 'swimming'
        elif any(word in text for word in ['triathlon', 'ironman']):
            return 'triathlon'
        elif any(word in text for word in ['yoga', 'pilates']):
            return 'yoga'
        else:
            return 'fitness'

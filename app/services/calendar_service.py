"""
Google Calendar Service for fetching calendar events.
"""
import os
import pickle
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from ..config import Config
from ..utils import setup_logger, parse_calendar_datetime

logger = setup_logger(__name__)


class CalendarService:
    """Service for Google Calendar integration"""
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.scopes = config.GOOGLE_CALENDAR_SCOPES
        self.credentials_file = config.CREDENTIALS_FILE
        self.token_file = config.TOKEN_FILE
        self.calendar_filter = config.CALENDAR_FILTER
        self.months_ahead = config.CALENDAR_MONTHS_AHEAD
        self.timezone = config.TIMEZONE
    
    def _get_credentials(self) -> Credentials:
        """Get or refresh Google Calendar credentials"""
        creds = None
        
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                logger.warning(f"Could not load token file: {e}")
                creds = None
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes
                )
                creds = flow.run_local_server(port=0)
            
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def get_events(self) -> List[Dict[str, Any]]:
        """
        Get calendar events for the configured time period.
        
        Returns:
            List of event dictionaries
        """
        if not os.path.exists(self.credentials_file):
            logger.warning(f"{self.credentials_file} not found - Google Calendar disabled")
            logger.info("To enable Google Calendar: Visit https://console.cloud.google.com, create a project, enable Calendar API, download credentials.json")
            return []
        
        try:
            creds = self._get_credentials()
            service = build('calendar', 'v3', credentials=creds)
            
            # Get all calendars
            calendar_list = service.calendarList().list().execute()
            all_calendars = calendar_list.get('items', [])
            
            # Filter calendars if specified
            if self.calendar_filter:
                filtered_calendars = [
                    cal for cal in all_calendars
                    if cal['summary'] in self.calendar_filter or cal['id'] in self.calendar_filter
                ]
                logger.info(f"Using {len(filtered_calendars)} of {len(all_calendars)} calendars")
            else:
                filtered_calendars = all_calendars
                logger.info(f"Using all {len(filtered_calendars)} calendars")
            
            # Calculate time range
            now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            end_date = (datetime.now(timezone.utc) + timedelta(days=30 * self.months_ahead))
            end_date_str = end_date.isoformat().replace('+00:00', 'Z')
            
            all_events = []
            
            # Fetch events from each calendar
            for calendar in filtered_calendars:
                try:
                    calendar_id = calendar['id']
                    calendar_name = calendar['summary']
                    
                    events_result = service.events().list(
                        calendarId=calendar_id,
                        timeMin=now,
                        timeMax=end_date_str,
                        maxResults=100,
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                    events = events_result.get('items', [])
                    
                    # Format events
                    for event in events:
                        start = event['start'].get('dateTime', event['start'].get('date'))
                        all_events.append({
                            'summary': event.get('summary', 'No title'),
                            'start': start,
                            'end': event['end'].get('dateTime', event['end'].get('date')),
                            'description': event.get('description', ''),
                            'calendar': calendar_name,
                            'location': event.get('location', ''),
                            'is_all_day': 'T' not in start
                        })
                    
                    logger.debug(f"Fetched {len(events)} events from '{calendar_name}'")
                    
                except Exception as e:
                    logger.warning(f"Error fetching calendar '{calendar.get('summary', 'Unknown')}': {e}")
                    continue
            
            # Sort all events by start time
            all_events.sort(key=lambda x: x['start'])
            
            logger.info(f"Fetched {len(all_events)} total events")
            return all_events
        
        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return []
    
    def get_today_events(self, all_events: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Filter events for today in the configured timezone.
        
        Args:
            all_events: Optional list of events (fetches if not provided)
        
        Returns:
            List of today's events
        """
        if all_events is None:
            all_events = self.get_events()
        
        from ..utils import now_in_timezone
        today = now_in_timezone(self.timezone).date()
        
        today_events = []
        for event in all_events:
            event_dt = parse_calendar_datetime(event['start'], self.timezone)
            if event_dt and event_dt.date() == today:
                today_events.append(event)
        
        logger.info(f"Found {len(today_events)} events for today")
        return today_events

    def get_todos(self) -> List[Dict[str, Any]]:
        """Get all todos from Google Calendar"""
        try:
            service = self._get_service()
            
            # Get events with [TODO] or [DONE] prefix
            now = datetime.now(timezone.utc).isoformat()
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            todos = []
            for event in events:
                summary = event.get('summary', '')
                if summary.startswith('[TODO]') or summary.startswith('[DONE]'):
                    completed = summary.startswith('[DONE]')
                    title = summary.replace('[TODO]', '').replace('[DONE]', '').strip()
                    
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    
                    todos.append({
                        'id': event['id'],
                        'title': title,
                        'date': start_dt.strftime('%Y-%m-%d'),
                        'time': start_dt.strftime('%H:%M'),
                        'completed': completed
                    })
            
            logger.info(f"Found {len(todos)} todos")
            return todos
            
        except Exception as e:
            logger.error(f"Error getting todos: {e}")
            return []

    def create_todo(self, title: str, date: str, time: str, completed: bool = False) -> Dict[str, Any]:
        """Create a new todo in Google Calendar"""
        try:
            service = self._get_service()
            
            # Parse date and time
            start_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(hours=1)
            
            prefix = '[DONE]' if completed else '[TODO]'
            event_body = {
                'summary': f"{prefix} {title}",
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': self.timezone,
                },
                'description': 'Created from Personal Dashboard',
            }
            
            event = service.events().insert(calendarId='primary', body=event_body).execute()
            
            logger.info(f"Created todo: {title}")
            
            return {
                'id': event['id'],
                'title': title,
                'date': date,
                'time': time,
                'completed': completed
            }
            
        except Exception as e:
            logger.error(f"Error creating todo: {e}")
            raise

    def update_todo(self, todo_id: str, completed: bool) -> Dict[str, Any]:
        """Update a todo's completion status"""
        try:
            service = self._get_service()
            
            # Get the event
            event = service.events().get(calendarId='primary', eventId=todo_id).execute()
            
            # Update the summary
            summary = event['summary']
            if completed:
                summary = summary.replace('[TODO]', '[DONE]')
            else:
                summary = summary.replace('[DONE]', '[TODO]')
            
            event['summary'] = summary
            
            # Update the event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=todo_id,
                body=event
            ).execute()
            
            title = summary.replace('[TODO]', '').replace('[DONE]', '').strip()
            start = updated_event['start'].get('dateTime', updated_event['start'].get('date'))
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            
            logger.info(f"Updated todo: {title} - completed: {completed}")
            
            return {
                'id': updated_event['id'],
                'title': title,
                'date': start_dt.strftime('%Y-%m-%d'),
                'time': start_dt.strftime('%H:%M'),
                'completed': completed
            }
            
        except Exception as e:
            logger.error(f"Error updating todo: {e}")
            raise

    def delete_todo(self, todo_id: str):
        """Delete a todo from Google Calendar"""
        try:
            service = self._get_service()
            service.events().delete(calendarId='primary', eventId=todo_id).execute()
            logger.info(f"Deleted todo: {todo_id}")
            
        except Exception as e:
            logger.error(f"Error deleting todo: {e}")
            raise

    def get_todos(self) -> List[Dict[str, Any]]:
        """
        Get all todo events from Google Calendar.
        Todos are stored as all-day events with [TODO] prefix.
        
        Returns:
            List of todo items
        """
        try:
            creds = self._get_credentials()
            service = build('calendar', 'v3', credentials=creds)
            
            # Get events from now onwards
            time_min = datetime.now(timezone.utc).isoformat()
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                maxResults=100,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Filter for todos (events with [TODO] in summary)
            todos = []
            for event in events:
                summary = event.get('summary', '')
                if summary.startswith('[TODO]'):
                    # Parse todo data
                    title = summary.replace('[TODO]', '').strip()
                    completed = '[DONE]' in summary
                    
                    start = event.get('start', {})
                    date_str = start.get('date') or start.get('dateTime', '').split('T')[0]
                    time_str = start.get('dateTime', '').split('T')[1].split(':')[0:2] if start.get('dateTime') else ['12', '00']
                    time_str = ':'.join(time_str) if time_str else '12:00'
                    
                    todos.append({
                        'id': event['id'],
                        'title': title,
                        'date': date_str,
                        'time': time_str,
                        'completed': completed
                    })
            
            logger.info(f"Found {len(todos)} todos")
            return todos
        except Exception as e:
            logger.error(f"Error fetching todos: {e}")
            return []

    def create_todo(self, title: str, date: str, time: str, completed: bool = False) -> Dict[str, Any]:
        """
        Create a new todo in Google Calendar.
        
        Args:
            title: Todo title
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            completed: Whether the todo is completed
        
        Returns:
            Created todo dict
        """
        try:
            creds = self._get_credentials()
            service = build('calendar', 'v3', credentials=creds)
            
            # Create event with [TODO] prefix
            status = '[DONE]' if completed else ''
            summary = f"[TODO] {status}{title}".strip()
            
            # Combine date and time
            start_datetime = f"{date}T{time}:00"
            end_datetime = f"{date}T{time.split(':')[0]}:30:00"  # 30 min duration
            
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': str(self.timezone)
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': str(self.timezone)
                },
                'description': 'Created via Personal Dashboard'
            }
            
            created_event = service.events().insert(calendarId='primary', body=event).execute()
            
            logger.info(f"Created todo: {title}")
            
            return {
                'id': created_event['id'],
                'title': title,
                'date': date,
                'time': time,
                'completed': completed
            }
        except Exception as e:
            logger.error(f"Error creating todo: {e}")
            raise

    def update_todo(self, todo_id: str, completed: bool) -> Dict[str, Any]:
        """
        Update a todo's completion status.
        
        Args:
            todo_id: Google Calendar event ID
            completed: New completion status
        
        Returns:
            Updated todo dict
        """
        try:
            creds = self._get_credentials()
            service = build('calendar', 'v3', credentials=creds)
            
            # Get the event
            event = service.events().get(calendarId='primary', eventId=todo_id).execute()
            
            # Update summary
            summary = event.get('summary', '')
            title = summary.replace('[TODO]', '').replace('[DONE]', '').strip()
            
            if completed:
                event['summary'] = f"[TODO] [DONE]{title}"
            else:
                event['summary'] = f"[TODO] {title}"
            
            # Update the event
            updated_event = service.events().update(
                calendarId='primary',
                eventId=todo_id,
                body=event
            ).execute()
            
            start = updated_event.get('start', {})
            date_str = start.get('date') or start.get('dateTime', '').split('T')[0]
            time_str = start.get('dateTime', '').split('T')[1].split(':')[0:2] if start.get('dateTime') else ['12', '00']
            time_str = ':'.join(time_str)
            
            logger.info(f"Updated todo {todo_id}: completed={completed}")
            
            return {
                'id': updated_event['id'],
                'title': title,
                'date': date_str,
                'time': time_str,
                'completed': completed
            }
        except Exception as e:
            logger.error(f"Error updating todo: {e}")
            raise

    def delete_todo(self, todo_id: str):
        """
        Delete a todo from Google Calendar.
        
        Args:
            todo_id: Google Calendar event ID
        """
        try:
            creds = self._get_credentials()
            service = build('calendar', 'v3', credentials=creds)
            
            service.events().delete(calendarId='primary', eventId=todo_id).execute()
            
            logger.info(f"Deleted todo {todo_id}")
        except Exception as e:
            logger.error(f"Error deleting todo: {e}")
            raise

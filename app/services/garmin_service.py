"""
Garmin Service for fetching fitness and sleep data.
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..config import Config
from ..utils import setup_logger, log_error, safe_get

logger = setup_logger(__name__)


class GarminService:
    """Service for Garmin Connect integration"""
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.email = config.GARMIN_EMAIL
        self.password = config.GARMIN_PASSWORD
    
    def get_data(self, date: str = None) -> Dict[str, Any]:
        """
        Get Garmin fitness and sleep data.
        
        Args:
            date: Date string in YYYY-MM-DD format (defaults to today)
        
        Returns:
            Dictionary with Garmin data
        """
        if not self.email or not self.password:
            logger.warning("Garmin credentials not configured")
            return self._get_fallback_data("Not configured", "⚠️ Garmin not configured. Add your GARMIN_EMAIL and GARMIN_PASSWORD to .env file. This feature is optional.")
        
        try:
            from garminconnect import Garmin
            
            client = Garmin(self.email, self.password)
            client.login()
            
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            # Get sleep data
            sleep_data = client.get_sleep_data(date)
            sleep_score, sleep_hours = self._parse_sleep_data(sleep_data)
            
            # Get training data
            training_load, training_status = self._get_training_data(client, date)
            
            # Get daily stats
            stats = self._get_daily_stats(client, date)
            
            logger.info("Garmin data synced successfully")
            
            return {
                "sleep_score": sleep_score,
                "sleep_hours": sleep_hours,
                "training_load": training_load,
                "training_status": training_status,
                "steps": stats.get('steps', 'N/A'),
                "calories": stats.get('calories', 'N/A'),
                "heart_rate": stats.get('heart_rate', 'N/A'),
                "body_battery_current": stats.get('body_battery_current'),
                "body_battery_highest": stats.get('body_battery_highest'),
                "body_battery_lowest": stats.get('body_battery_lowest')
            }
        
        except ImportError:
            logger.error("garminconnect library not installed (pip install garminconnect)")
            return self._get_fallback_data("Library not installed", "⚠️ Garmin library not installed. Run: pip install garminconnect")
        
        except Exception as e:
            log_error(logger, 'Garmin', e)
            return self._get_fallback_data("Connection failed", "⚠️ Could not connect to Garmin. Check your GARMIN_EMAIL and GARMIN_PASSWORD in .env file.")
    
    def _parse_sleep_data(self, sleep_data: Dict) -> tuple:
        """Extract sleep score and hours from sleep data"""
        sleep_score = 'N/A'
        sleep_hours = 0
        
        if sleep_data and 'dailySleepDTO' in sleep_data:
            daily_sleep = sleep_data['dailySleepDTO']
            
            # Get sleep score
            sleep_score = safe_get(
                daily_sleep,
                'sleepScores', 'overall', 'value',
                default='N/A'
            )
            
            # Get sleep duration
            sleep_seconds = safe_get(daily_sleep, 'sleepTimeSeconds', default=0)
            sleep_hours = sleep_seconds / 3600
        
        return sleep_score, sleep_hours
    
    def _get_training_data(self, client, date: str) -> tuple:
        """Get training load and status"""
        training_load = 'N/A'
        training_status = 'N/A'
        
        try:
            training_response = client.get_training_status(date)
            
            if training_response and 'mostRecentTrainingStatus' in training_response:
                latest_status = safe_get(
                    training_response,
                    'mostRecentTrainingStatus',
                    'latestTrainingStatusData',
                    default={}
                )
                
                if latest_status:
                    # Get first device's data
                    device_data = next(iter(latest_status.values()), None)
                    
                    if device_data:
                        # Get acute training load
                        acute_load_dto = device_data.get('acuteTrainingLoadDTO', {})
                        training_load = safe_get(
                            acute_load_dto,
                            'dailyTrainingLoadAcute',
                            default=safe_get(acute_load_dto, 'dailyTrainingLoadChronic', default='N/A')
                        )
                        
                        # Get training status
                        training_status = safe_get(
                            device_data,
                            'trainingStatusFeedbackPhrase',
                            default=safe_get(device_data, 'trainingStatus', default='N/A')
                        )
        
        except Exception as e:
            logger.debug(f"Training status unavailable: {e}")
        
        return training_load, training_status
    
    def _get_daily_stats(self, client, date: str) -> Dict[str, Any]:
        """Get daily activity stats"""
        stats = {
            'steps': 'N/A',
            'calories': 'N/A',
            'heart_rate': 'N/A',
            'body_battery_current': None,
            'body_battery_highest': None,
            'body_battery_lowest': None
        }
        
        try:
            daily_stats = client.get_stats(date)
            
            if daily_stats:
                stats['steps'] = safe_get(daily_stats, 'totalSteps', default='N/A')
                stats['calories'] = safe_get(daily_stats, 'totalKilocalories', default='N/A')
                stats['heart_rate'] = safe_get(daily_stats, 'restingHeartRate', default='N/A')
                
                # Body battery data
                stats['body_battery_current'] = safe_get(daily_stats, 'bodyBatteryMostRecentValue')
                stats['body_battery_highest'] = safe_get(daily_stats, 'bodyBatteryHighestValue')
                stats['body_battery_lowest'] = safe_get(daily_stats, 'bodyBatteryLowestValue')
        
        except Exception as e:
            logger.debug(f"Daily stats unavailable: {e}")
        
        return stats
    
    def get_sleep_analysis(self, days: int = 7) -> Dict[str, Any]:
        """
        Get detailed sleep analysis for the last N days.
        
        Args:
            days: Number of days to analyze (default: 7 for weekly analysis)
        
        Returns:
            Dictionary with sleep analysis including stages, trends, and recommendations
        """
        if not self.email or not self.password:
            logger.warning("Garmin credentials not configured")
            return self._get_fallback_sleep_analysis("Not configured")
        
        try:
            from garminconnect import Garmin
            
            client = Garmin(self.email, self.password)
            client.login()
            
            sleep_data_list = []
            today = datetime.now()
            
            # Fetch sleep data for the last N days
            for i in range(days):
                date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                try:
                    sleep_data = client.get_sleep_data(date)
                    if sleep_data and 'dailySleepDTO' in sleep_data:
                        daily_sleep = sleep_data['dailySleepDTO']
                        
                        # Extract sleep stages
                        sleep_levels = safe_get(daily_sleep, 'sleepLevels', default=[])
                        stages = self._calculate_sleep_stages(sleep_levels)
                        
                        # Extract basic info
                        sleep_seconds = safe_get(daily_sleep, 'sleepTimeSeconds', default=0)
                        sleep_hours = sleep_seconds / 3600
                        
                        sleep_score = safe_get(
                            daily_sleep,
                            'sleepScores', 'overall', 'value',
                            default=0
                        )
                        
                        sleep_data_list.append({
                            'date': date,
                            'hours': sleep_hours,
                            'score': sleep_score,
                            'deep_minutes': stages['deep'],
                            'light_minutes': stages['light'],
                            'rem_minutes': stages['rem'],
                            'awake_minutes': stages['awake']
                        })
                except Exception as e:
                    logger.debug(f"Could not fetch sleep data for {date}: {e}")
                    continue
            
            if not sleep_data_list:
                return self._get_fallback_sleep_analysis("No data available")
            
            # Calculate analysis metrics
            analysis = self._calculate_sleep_metrics(sleep_data_list)
            
            logger.info(f"Sleep analysis complete for {len(sleep_data_list)} days")
            return analysis
        
        except ImportError:
            logger.error("garminconnect library not installed")
            return self._get_fallback_sleep_analysis("Library not installed")
        
        except Exception as e:
            log_error(logger, 'Garmin Sleep Analysis', e)
            return self._get_fallback_sleep_analysis("Connection failed")
    
    def _calculate_sleep_stages(self, sleep_levels: List) -> Dict[str, int]:
        """Calculate total minutes for each sleep stage"""
        stages = {
            'deep': 0,
            'light': 0,
            'rem': 0,
            'awake': 0
        }
        
        if not sleep_levels:
            return stages
        
        for level in sleep_levels:
            stage_type = safe_get(level, 'activityLevel', default='').lower()
            duration_seconds = safe_get(level, 'seconds', default=0)
            duration_minutes = duration_seconds / 60
            
            if 'deep' in stage_type:
                stages['deep'] += duration_minutes
            elif 'light' in stage_type:
                stages['light'] += duration_minutes
            elif 'rem' in stage_type:
                stages['rem'] += duration_minutes
            elif 'awake' in stage_type:
                stages['awake'] += duration_minutes
        
        return stages
    
    def _calculate_sleep_metrics(self, sleep_data: List[Dict]) -> Dict[str, Any]:
        """Calculate sleep consistency, trends, and recommendations"""
        if not sleep_data:
            return self._get_fallback_sleep_analysis("No data")
        
        # Sort by date (newest first)
        sleep_data.sort(key=lambda x: x['date'], reverse=True)
        
        # Calculate averages
        avg_hours = sum(d['hours'] for d in sleep_data) / len(sleep_data)
        avg_score = sum(d['score'] for d in sleep_data if d['score'] > 0) / max(len([d for d in sleep_data if d['score'] > 0]), 1)
        avg_deep = sum(d['deep_minutes'] for d in sleep_data) / len(sleep_data)
        avg_light = sum(d['light_minutes'] for d in sleep_data) / len(sleep_data)
        avg_rem = sum(d['rem_minutes'] for d in sleep_data) / len(sleep_data)
        avg_awake = sum(d['awake_minutes'] for d in sleep_data) / len(sleep_data)
        
        # Calculate consistency score (0-100)
        # Based on standard deviation of sleep duration
        if len(sleep_data) > 1:
            mean_hours = avg_hours
            variance = sum((d['hours'] - mean_hours) ** 2 for d in sleep_data) / len(sleep_data)
            std_dev = variance ** 0.5
            # Lower std_dev = higher consistency
            # Consistency score: 100 if std_dev=0, decreases as std_dev increases
            consistency_score = max(0, min(100, 100 - (std_dev * 30)))
        else:
            consistency_score = 100
        
        # Calculate sleep debt (recommended 7-9 hours)
        recommended_hours = 8
        total_debt = sum(max(0, recommended_hours - d['hours']) for d in sleep_data)
        avg_debt = total_debt / len(sleep_data)
        
        # Detect trends (last 3 days vs previous days)
        if len(sleep_data) >= 6:
            recent_avg = sum(d['hours'] for d in sleep_data[:3]) / 3
            older_avg = sum(d['hours'] for d in sleep_data[3:6]) / 3
            
            if recent_avg > older_avg + 0.5:
                trend = "improving"
            elif recent_avg < older_avg - 0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Generate recommendations
        recommendations = self._generate_sleep_recommendations(
            avg_hours, avg_score, consistency_score, avg_deep, avg_rem, avg_debt
        )
        
        # Calculate optimal bedtime (based on average wake time and recommended sleep)
        # Assuming typical wake time of 7:00 AM
        optimal_bedtime = "22:30 - 23:00"  # For 7-8 hour sleep
        
        return {
            "weekly_data": sleep_data,
            "averages": {
                "hours": round(avg_hours, 1),
                "score": round(avg_score, 0),
                "deep_minutes": round(avg_deep, 0),
                "light_minutes": round(avg_light, 0),
                "rem_minutes": round(avg_rem, 0),
                "awake_minutes": round(avg_awake, 0)
            },
            "consistency_score": round(consistency_score, 0),
            "sleep_debt": {
                "total_hours": round(total_debt, 1),
                "avg_daily": round(avg_debt, 1)
            },
            "trend": trend,
            "optimal_bedtime": optimal_bedtime,
            "recommendations": recommendations
        }
    
    def _generate_sleep_recommendations(
        self, avg_hours: float, avg_score: float, consistency: float,
        deep_minutes: float, rem_minutes: float, debt: float
    ) -> List[str]:
        """Generate personalized sleep recommendations"""
        recommendations = []
        
        # Sleep duration recommendations
        if avg_hours < 7:
            recommendations.append("⚠️ You're averaging less than 7 hours. Aim for 7-9 hours for optimal recovery.")
        elif avg_hours > 9:
            recommendations.append("💤 Sleeping over 9 hours might indicate poor sleep quality. Check for disruptions.")
        else:
            recommendations.append("✅ Great sleep duration! You're in the optimal 7-9 hour range.")
        
        # Sleep score recommendations
        if avg_score < 70:
            recommendations.append("📉 Low sleep quality detected. Consider reducing caffeine and screen time before bed.")
        elif avg_score >= 80:
            recommendations.append("🌟 Excellent sleep quality! Keep up your sleep routine.")
        
        # Consistency recommendations
        if consistency < 70:
            recommendations.append("🔄 Inconsistent sleep schedule. Try going to bed at the same time each night.")
        else:
            recommendations.append("✅ Good sleep consistency! Regular schedule helps optimize recovery.")
        
        # Deep sleep recommendations
        if deep_minutes < 60:
            recommendations.append("🔍 Low deep sleep. Avoid alcohol and exercise 3+ hours before bedtime.")
        elif deep_minutes > 120:
            recommendations.append("💪 Excellent deep sleep! Your body is recovering optimally.")
        
        # REM sleep recommendations
        if rem_minutes < 60:
            recommendations.append("🧠 Low REM sleep. Manage stress and maintain consistent sleep times.")
        elif rem_minutes > 120:
            recommendations.append("🎯 Great REM sleep! Your mind is processing and learning well.")
        
        # Sleep debt recommendations
        if debt > 1:
            recommendations.append(f"⏰ You have {round(debt, 1)} hours of daily sleep debt. Consider a weekend catch-up sleep session.")
        
        return recommendations
    
    def _get_fallback_sleep_analysis(self, reason: str) -> Dict[str, Any]:
        """Return fallback sleep analysis when Garmin is unavailable"""
        return {
            "weekly_data": [],
            "averages": {
                "hours": 0,
                "score": 0,
                "deep_minutes": 0,
                "light_minutes": 0,
                "rem_minutes": 0,
                "awake_minutes": 0
            },
            "consistency_score": 0,
            "sleep_debt": {
                "total_hours": 0,
                "avg_daily": 0
            },
            "trend": "unavailable",
            "optimal_bedtime": "N/A",
            "recommendations": [f"Sleep analysis unavailable: {reason}"]
        }
    
    def _get_fallback_data(self, reason: str, setup_message: str = None) -> Dict[str, Any]:
        """Return fallback data when Garmin is unavailable"""
        return {
            "sleep_score": reason,
            "sleep_hours": 0,
            "training_load": "N/A",
            "training_status": reason,
            "steps": "N/A",
            "calories": "N/A",
            "heart_rate": "N/A",
            "setup_required": reason if reason != "N/A" else None,
            "setup_message": setup_message
        }

"""
Scheduler service for automated web scraping
Manages background jobs and scheduling configuration
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

SCHEDULES_CONFIG_FILE = Path(__file__).parent.parent.parent / "data" / "schedules.json"


class SchedulerService:
    """Manages scheduled scraping tasks"""
    
    def __init__(self):
        """Initialize the scheduler service"""
        self.scheduler = BackgroundScheduler()
        self.schedules: Dict[str, Dict[str, Any]] = {}
        self.scraper_service = None  # Will be set after initialization
        self._load_schedules()
    
    def set_scraper_service(self, scraper_service):
        """Set the scraper service reference"""
        self.scraper_service = scraper_service
    
    def _load_schedules(self):
        """Load schedule configuration from file"""
        if SCHEDULES_CONFIG_FILE.exists():
            try:
                with open(SCHEDULES_CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.schedules = data.get('schedules', {})
                    logger.info(f"Loaded {len(self.schedules)} schedules from config")
            except Exception as e:
                logger.error(f"Error loading schedules: {e}")
                self.schedules = {}
        else:
            self.schedules = {}
    
    def _save_schedules(self):
        """Save schedule configuration to file"""
        try:
            SCHEDULES_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(SCHEDULES_CONFIG_FILE, 'w') as f:
                json.dump({'schedules': self.schedules}, f, indent=2)
            logger.info("Schedules saved to config")
        except Exception as e:
            logger.error(f"Error saving schedules: {e}")
    
    def _scrape_job(self, sources: Optional[List[str]] = None):
        """Job function to execute scraping"""
        try:
            logger.info(f"Running scheduled scrape job (sources: {sources or 'all'})")
            
            if sources and len(sources) == 1:
                # Scrape single source
                from src.models.opportunity import SourcePlatform
                for sp in SourcePlatform:
                    if sp.value == sources[0]:
                        result = self.scraper_service.scrape_source(sp)
                        logger.info(f"Scheduled scrape completed: {result}")
                        return result
            else:
                # Scrape all sources
                result = self.scraper_service.scrape_all()
                logger.info(f"Scheduled scrape completed: {result['summary']}")
                return result
                
        except Exception as e:
            logger.error(f"Error in scheduled scrape job: {e}")
    
    def start(self):
        """Start the scheduler and load existing jobs"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Scheduler started")
            
            # Register existing schedules
            for name, config in self.schedules.items():
                if config.get('enabled', True):
                    self._register_job(name, config)
                    
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def _register_job(self, name: str, config: Dict[str, Any]):
        """Register a job with the scheduler"""
        try:
            if self.scheduler.get_job(name):
                self.scheduler.remove_job(name)
            
            schedule_type = config.get('type', 'daily')
            time_str = config.get('time', '10:00')  # HH:MM format
            sources = config.get('sources')
            
            if schedule_type == 'daily':
                hour, minute = map(int, time_str.split(':'))
                trigger = CronTrigger(hour=hour, minute=minute)
                
            elif schedule_type == 'weekly':
                day_of_week = config.get('day_of_week', 0)  # 0-6, Monday-Sunday
                hour, minute = map(int, time_str.split(':'))
                trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)
                
            elif schedule_type == 'interval':
                interval_hours = config.get('interval_hours', 24)
                trigger = IntervalTrigger(hours=interval_hours)
                
            else:
                logger.warning(f"Unknown schedule type: {schedule_type}")
                return
            
            self.scheduler.add_job(
                self._scrape_job,
                trigger=trigger,
                id=name,
                name=name,
                kwargs={'sources': sources},
                replace_existing=True
            )
            logger.info(f"Registered job '{name}' with trigger {schedule_type}")
            
        except Exception as e:
            logger.error(f"Error registering job '{name}': {e}")
    
    def create_schedule(self, name: str, config: Dict[str, Any]) -> Dict[str, str]:
        """Create a new schedule"""
        try:
            # Validate config
            if 'type' not in config:
                config['type'] = 'daily'
            
            if config['type'] in ['daily', 'weekly']:
                if 'time' not in config:
                    config['time'] = '10:00'
            
            if config['type'] == 'interval':
                if 'interval_hours' not in config:
                    config['interval_hours'] = 24
            
            config['enabled'] = config.get('enabled', True)
            config['created_at'] = datetime.now().isoformat()
            
            self.schedules[name] = config
            self._save_schedules()
            
            # If scheduler is running, register the job immediately
            if self.scheduler.running and config.get('enabled', True):
                self._register_job(name, config)
            
            return {
                'status': 'success',
                'message': f'Schedule "{name}" created',
                'schedule': name
            }
            
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def update_schedule(self, name: str, config: Dict[str, Any]) -> Dict[str, str]:
        """Update an existing schedule"""
        try:
            if name not in self.schedules:
                return {
                    'status': 'error',
                    'message': f'Schedule "{name}" not found'
                }
            
            # Merge configs
            self.schedules[name].update(config)
            self.schedules[name]['updated_at'] = datetime.now().isoformat()
            
            self._save_schedules()
            
            # Re-register job if scheduler is running
            if self.scheduler.running:
                self._register_job(name, self.schedules[name])
            
            return {
                'status': 'success',
                'message': f'Schedule "{name}" updated',
                'schedule': name
            }
            
        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def delete_schedule(self, name: str) -> Dict[str, str]:
        """Delete a schedule"""
        try:
            if name not in self.schedules:
                return {
                    'status': 'error',
                    'message': f'Schedule "{name}" not found'
                }
            
            del self.schedules[name]
            self._save_schedules()
            
            # Remove job from scheduler if running
            if self.scheduler.running:
                job = self.scheduler.get_job(name)
                if job:
                    self.scheduler.remove_job(name)
            
            return {
                'status': 'success',
                'message': f'Schedule "{name}" deleted'
            }
            
        except Exception as e:
            logger.error(f"Error deleting schedule: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_schedules(self) -> Dict[str, Any]:
        """Get all schedules with job status"""
        result = {}
        
        for name, config in self.schedules.items():
            job = self.scheduler.get_job(name) if self.scheduler.running else None
            next_run = job.next_run_time.isoformat() if job and job.next_run_time else None
            
            result[name] = {
                **config,
                'next_run': next_run,
                'active': job is not None if self.scheduler.running else False
            }
        
        return result
    
    def get_schedule(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific schedule"""
        if name not in self.schedules:
            return None
        
        config = self.schedules[name].copy()
        job = self.scheduler.get_job(name) if self.scheduler.running else None
        
        if job:
            config['next_run'] = job.next_run_time.isoformat() if job.next_run_time else None
            config['active'] = True
        else:
            config['next_run'] = None
            config['active'] = False
        
        return config
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status"""
        return {
            'running': self.scheduler.running,
            'job_count': len(self.scheduler.get_jobs()),
            'total_schedules': len(self.schedules),
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
                for job in self.scheduler.get_jobs()
            ]
        }


# Global instance
scheduler_service: Optional[SchedulerService] = None


def get_scheduler_service() -> SchedulerService:
    """Get or create the global scheduler service instance"""
    global scheduler_service
    if scheduler_service is None:
        scheduler_service = SchedulerService()
    return scheduler_service

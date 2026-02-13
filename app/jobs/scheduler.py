from apscheduler.schedulers.background import BackgroundScheduler
from app.config import settings
from app.db import SessionLocal
from app.services.ranking import RankingService
from app.providers.data import FixtureImporter, APIProvider, ManualProvider
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def update_matches_job():
    """Job to update match results from provider"""
    try:
        logger.info("Starting match update job...")
        
        db = SessionLocal()
        
        # Get provider based on config
        if settings.SPORTS_API_PROVIDER == "api-football" and settings.SPORTS_API_KEY:
            provider = APIProvider(
                api_key=settings.SPORTS_API_KEY,
                api_url=settings.SPORTS_API_URL or "https://v3.football.api-sports.io"
            )
        else:
            # Manual provider - for dev/demo
            provider = ManualProvider()
        
        importer = FixtureImporter(provider)
        count = importer.update_results(db)
        
        logger.info(f"Match update job completed. Updated {count} results.")
        
        db.close()
    except Exception as e:
        logger.error(f"Error in match update job: {e}")

def recalculate_rankings_job():
    """Job to recalculate rankings after match updates"""
    try:
        logger.info("Starting ranking recalculation job...")
        
        db = SessionLocal()
        
        # Global ranking
        RankingService.recalculate_global_ranking(db)
        
        # Group rankings
        from app.models import Group
        groups = db.query(Group).filter(Group.is_active == True).all()
        for group in groups:
            RankingService.recalculate_group_ranking(db, group.id)
        
        logger.info(f"Ranking recalculation job completed. {len(groups)} groups updated.")
        
        db.close()
    except Exception as e:
        logger.error(f"Error in ranking recalculation job: {e}")

def cleanup_expired_sessions_job():
    """Job to cleanup expired sessions and tokens"""
    try:
        logger.info("Starting cleanup job...")
        
        db = SessionLocal()
        
        # TODO: Cleanup expired password reset tokens, etc.
        # This would be done via database cleanup
        
        logger.info("Cleanup job completed.")
        
        db.close()
    except Exception as e:
        logger.error(f"Error in cleanup job: {e}")

def start_scheduler():
    """Start background scheduler"""
    if scheduler.running:
        return
    
    # Update matches every 5 minutes during Copa, less often otherwise
    scheduler.add_job(
        update_matches_job,
        'interval',
        seconds=settings.UPDATE_MATCHES_INTERVAL_SECONDS,
        id='update_matches',
        name='Update Matches',
        replace_existing=True
    )
    
    # Recalculate rankings every hour
    scheduler.add_job(
        recalculate_rankings_job,
        'interval',
        seconds=settings.RECALC_RANKINGS_INTERVAL_SECONDS,
        id='recalc_rankings',
        name='Recalculate Rankings',
        replace_existing=True
    )
    
    # Cleanup every day at 3 AM UTC
    scheduler.add_job(
        cleanup_expired_sessions_job,
        'cron',
        hour=3,
        minute=0,
        id='cleanup',
        name='Cleanup Expired Sessions',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Background scheduler started")

def stop_scheduler():
    """Stop background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Background scheduler stopped")

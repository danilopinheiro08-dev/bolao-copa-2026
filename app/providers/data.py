from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import json
import logging
from datetime import datetime, timezone
from app.models import Match, MatchStage, MatchStatus

logger = logging.getLogger(__name__)

class SportsDataProvider(ABC):
    """Abstract base class for sports data providers"""
    
    @abstractmethod
    def get_fixtures(self) -> List[Dict]:
        """Get all fixtures for tournament"""
        pass
    
    @abstractmethod
    def get_results_updates(self, since: Optional[datetime] = None) -> List[Dict]:
        """Get result updates since last check"""
        pass

class ManualProvider(SportsDataProvider):
    """Manual provider - admin uploads CSV/JSON"""
    
    def __init__(self):
        self.fixtures = []
    
    def load_from_file(self, filepath: str):
        """Load fixtures from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.fixtures = data.get('matches', [])
                logger.info(f"Loaded {len(self.fixtures)} fixtures from {filepath}")
        except Exception as e:
            logger.error(f"Error loading fixtures: {e}")
    
    def get_fixtures(self) -> List[Dict]:
        """Get fixtures"""
        return self.fixtures
    
    def get_results_updates(self, since: Optional[datetime] = None) -> List[Dict]:
        """Get result updates"""
        updates = []
        for match in self.fixtures:
            if match.get('status') == 'FT' and match.get('home_score') is not None:
                updates.append(match)
        return updates

class APIProvider(SportsDataProvider):
    """API-based provider (API-Football, Sportradar, etc.)"""
    
    def __init__(self, api_key: str, api_url: str = None):
        self.api_key = api_key
        self.api_url = api_url or "https://v3.football.api-sports.io"
    
    def get_fixtures(self) -> List[Dict]:
        """Get fixtures from API"""
        try:
            import requests
            
            # Example for api-football.com
            # Copa 2026 league ID: 16 (example, verify actual ID)
            headers = {"x-apisports-key": self.api_key}
            response = requests.get(
                f"{self.api_url}/fixtures",
                params={
                    "league": 16,  # Copa do Mundo
                    "season": 2026,
                },
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', [])
            else:
                logger.error(f"API error: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching fixtures from API: {e}")
            return []
    
    def get_results_updates(self, since: Optional[datetime] = None) -> List[Dict]:
        """Get result updates from API"""
        try:
            import requests
            
            headers = {"x-apisports-key": self.api_key}
            
            params = {
                "league": 16,
                "season": 2026,
                "status": "FT"  # Finished matches only
            }
            
            if since:
                params["from"] = since.date().isoformat()
            
            response = requests.get(
                f"{self.api_url}/fixtures",
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', [])
            else:
                logger.error(f"API error: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching results from API: {e}")
            return []

class FixtureImporter:
    """Import fixtures and update results"""
    
    def __init__(self, provider: SportsDataProvider):
        self.provider = provider
    
    def import_fixtures(self, db) -> int:
        """Import fixtures into database"""
        from sqlalchemy.orm import Session
        
        fixtures = self.provider.get_fixtures()
        count = 0
        
        for fixture in fixtures:
            try:
                match = self._parse_fixture(fixture)
                if match:
                    # Check if already exists
                    existing = db.query(Match).filter(
                        Match.fifa_match_code == match.fifa_match_code
                    ).first() if match.fifa_match_code else None
                    
                    if not existing:
                        db.add(match)
                        count += 1
            except Exception as e:
                logger.error(f"Error importing fixture: {e}")
        
        db.commit()
        logger.info(f"Imported {count} new fixtures")
        return count
    
    def update_results(self, db) -> int:
        """Update match results"""
        from sqlalchemy.orm import Session
        
        updates = self.provider.get_results_updates()
        count = 0
        
        for update in updates:
            try:
                fifa_code = update.get('fixture', {}).get('id')
                
                match = db.query(Match).filter(
                    Match.fifa_match_code == fifa_code
                ).first() if fifa_code else None
                
                if not match:
                    continue
                
                # Update score
                goals = update.get('goals', {})
                match.home_score = goals.get('home')
                match.away_score = goals.get('away')
                
                # Update status
                status = update.get('fixture', {}).get('status', {}).get('short', 'NS')
                if status == 'FT':
                    match.status = MatchStatus.FINISHED
                elif status == 'LIVE':
                    match.status = MatchStatus.LIVE
                
                match.updated_at = datetime.now(timezone.utc)
                count += 1
            except Exception as e:
                logger.error(f"Error updating result: {e}")
        
        db.commit()
        logger.info(f"Updated {count} match results")
        return count
    
    @staticmethod
    def _parse_fixture(fixture: Dict) -> Optional[Match]:
        """Parse fixture data into Match model"""
        try:
            fixture_info = fixture.get('fixture', {})
            teams = fixture.get('teams', {})
            goals = fixture.get('goals', {})
            league = fixture.get('league', {})
            
            # Extract basic info
            fifa_code = fixture_info.get('id')
            kickoff = fixture_info.get('date')
            
            if not kickoff:
                return None
            
            # Parse datetime
            kickoff_dt = datetime.fromisoformat(kickoff.replace('Z', '+00:00'))
            
            # Determine stage and group
            stage_name = league.get('round', 'GROUP STAGE').upper()
            stage = FixtureImporter._map_stage(stage_name)
            group_name = FixtureImporter._extract_group(stage_name)
            
            match = Match(
                fifa_match_code=str(fifa_code),
                stage=stage,
                group_name=group_name,
                match_order=fixture_info.get('id', 0),
                home_team=teams.get('home', {}).get('name', ''),
                away_team=teams.get('away', {}).get('name', ''),
                home_team_code=teams.get('home', {}).get('code'),
                away_team_code=teams.get('away', {}).get('code'),
                kickoff_at_utc=kickoff_dt,
                venue=fixture_info.get('venue', {}).get('name'),
                city=fixture_info.get('venue', {}).get('city'),
                status=MatchStatus.SCHEDULED,
                home_score=goals.get('home'),
                away_score=goals.get('away'),
            )
            
            return match
        
        except Exception as e:
            logger.error(f"Error parsing fixture: {e}")
            return None
    
    @staticmethod
    def _map_stage(stage_name: str) -> MatchStage:
        """Map stage name to MatchStage enum"""
        stage_name = stage_name.lower()
        
        if "group" in stage_name:
            return MatchStage.GROUP
        elif "round of 32" in stage_name or "r32" in stage_name:
            return MatchStage.ROUND_32
        elif "round of 16" in stage_name or "r16" in stage_name:
            return MatchStage.ROUND_16
        elif "quarter" in stage_name:
            return MatchStage.QUARTER_FINAL
        elif "semi" in stage_name:
            return MatchStage.SEMI_FINAL
        elif "third" in stage_name:
            return MatchStage.THIRD_PLACE
        elif "final" in stage_name:
            return MatchStage.FINAL
        
        return MatchStage.GROUP
    
    @staticmethod
    def _extract_group(stage_name: str) -> Optional[str]:
        """Extract group letter (A-L) from stage name"""
        import re
        
        match = re.search(r'[A-L](?:\s|$)', stage_name)
        if match:
            return match.group(0).strip()
        
        return None

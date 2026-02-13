import click
from app.db import SessionLocal, engine, Base
from app.models import User
from app.security.crypto import hash_password
from app.providers.data import FixtureImporter, ManualProvider
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Bolão Copa 2026 CLI"""
    pass

@click.command()
def init_db():
    """Initialize database - create all tables"""
    click.echo("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    click.echo("✓ Database initialized")

@click.command()
@click.option("--email", prompt="Admin email", type=str)
@click.option("--name", prompt="Admin name", type=str)
@click.option("--password", prompt="Admin password", hide_input=True, confirmation_prompt=True, type=str)
def create_admin(email, name, password):
    """Create admin user"""
    db = SessionLocal()
    
    # Check if exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        click.echo(f"✗ User {email} already exists")
        db.close()
        return
    
    # Create admin
    admin = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        is_admin=True,
        email_verified=True,
        provider="email"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    click.echo(f"✓ Admin user created: {email} (ID: {admin.id})")
    db.close()

@click.command()
@click.option("--file", prompt="Fixtures JSON file", type=click.Path(exists=True), default="fixtures_2026.json")
def seed_fixtures(file):
    """Import fixtures from JSON file"""
    db = SessionLocal()
    
    try:
        provider = ManualProvider()
        provider.load_from_file(file)
        
        importer = FixtureImporter(provider)
        count = importer.import_fixtures(db)
        
        click.echo(f"✓ Imported {count} fixtures from {file}")
    except Exception as e:
        click.echo(f"✗ Error importing fixtures: {e}")
    finally:
        db.close()

@click.command()
def check_db():
    """Check database connection"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        click.echo("✓ Database connection OK")
    except Exception as e:
        click.echo(f"✗ Database connection failed: {e}")

@click.command()
def list_users():
    """List all users"""
    db = SessionLocal()
    
    users = db.query(User).all()
    
    if not users:
        click.echo("No users found")
        return
    
    click.echo(f"\nFound {len(users)} users:\n")
    click.echo(f"{'ID':<5} {'Email':<30} {'Name':<20} {'Admin':<10}")
    click.echo("-" * 65)
    
    for user in users:
        click.echo(f"{user.id:<5} {user.email:<30} {user.name:<20} {'Yes' if user.is_admin else 'No':<10}")
    
    db.close()

@click.command()
def list_fixtures():
    """List all fixtures"""
    db = SessionLocal()
    
    from app.models import Match
    
    matches = db.query(Match).order_by(Match.kickoff_at_utc).all()
    
    if not matches:
        click.echo("No matches found")
        return
    
    click.echo(f"\nFound {len(matches)} matches:\n")
    click.echo(f"{'ID':<5} {'Stage':<8} {'Home':<20} {'Away':<20} {'Status':<10} {'Score':<10}")
    click.echo("-" * 80)
    
    for match in matches:
        score = f"{match.home_score}-{match.away_score}" if match.home_score is not None else "TBD"
        click.echo(f"{match.id:<5} {match.stage.value:<8} {match.home_team:<20} {match.away_team:<20} {match.status.value:<10} {score:<10}")
    
    db.close()

@click.command()
def check_fixtures():
    """Check if fixtures are loaded"""
    db = SessionLocal()
    
    from app.models import Match
    
    count = db.query(Match).count()
    click.echo(f"Total matches in database: {count}")
    
    if count == 0:
        click.echo("\n✗ No fixtures loaded. Run: python -m app.cli seed-fixtures")
    else:
        click.echo("✓ Fixtures loaded successfully")
    
    db.close()

# Add commands to CLI
cli.add_command(init_db, name="init-db")
cli.add_command(create_admin, name="create-admin")
cli.add_command(seed_fixtures, name="seed-fixtures")
cli.add_command(check_db, name="check-db")
cli.add_command(list_users, name="list-users")
cli.add_command(list_fixtures, name="list-fixtures")
cli.add_command(check_fixtures, name="check-fixtures")

if __name__ == "__main__":
    cli()

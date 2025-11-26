# Database

The bot uses a SQLite database with [Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/) as the ORM.

The database must be initialized before the bot is started.

## Initialization

### Development Container

If you are using a Development Container, the database will be automatically set up when the container starts. Otherwise, you must set up the database manually.

### Manual

1. First, you need to install the Tortoise CLI tool `aerich`. Run `python3 -m pip install aerich` to do so.

2. Now you need a database. Create an empty file named `db.sqlite3` in the `data/` folder.

3. Run `aerich upgrade` in the project root to bring the database up to the latest version.

## Database Models

All database models are located in `models/database/` and inherit from `BaseModel`:

- `aiData.py`: AI service usage data
- `memeData.py`: Meme collection data
- `quoteData.py`: Quote data
- `userData.py`: User data

## Changes to the Data Model

If you make changes to the data stored in the database, you must update the database migrations.

1. Run `aerich migrate --name=<migration name>` to create a new migration.
2. Run `aerich upgrade` to bring the database up to date.

### Best Practices

- Use descriptive names for migrations (e.g., `add_user_role_field`)
- Test migrations locally before committing
- Document breaking changes in the commit message
- Use `aerich downgrade` carefully during development

## Configuration

The database configuration is located in `tortoiseConfig.py`.

## Migrations

All migrations are located in the `src/migrations/` folder.

## Troubleshooting

### Database is corrupt

1. Back up the current database: `cp data/db.sqlite3 data/db.sqlite3.backup`
2. Delete the database: `rm data/db.sqlite3`
3. Reinitialize: `aerich upgrade`

### Migration fails

1. Check the database integrity
2. Verify that all models are correctly imported in `tortoiseConfig.py`
3. Try `aerich downgrade` to the previous version
4. Consult the Tortoise ORM [documentation](https://tortoise-orm.readthedocs.io/en/latest/)

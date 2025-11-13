# Datenbank

Der Bot benutzt eine SQLite Datenbank mit [Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/) als ORM.

Die Datenbank muss initialisiert werden, bevor der Bot gestartet wird.

## Initialisierung

### Development Container

Wenn du Development Container benutzt, wird die Datenbank beim Start des Containers automatisch eingerichtet. Andernfalls musst du die Datenbank manuell einrichten.

### Manuell

1. Zunächst musst du das Tortoise-CLI tool `aerich` installieren. Führe dazu `python3 -m pip install aerich` aus.

2. Nun benötigst du eine Datenbank. Erstelle dafür eine leere Datei namens `db.sqlite3` im Ordner `data/`.

3. Führe im Projekt-Root `aerich upgrade` aus, um die Datenbank auf die neueste Version zu bringen.

## Datenbankmodelle

Alle Datenbankmodelle befinden sich in `models/database/` und erben von `BaseModel`:

- `aiData.py`: AI-Service Nutzungsdaten
- `memeData.py`: Meme-Sammlung Daten
- `quoteData.py`: Quote-Daten
- `userData.py`: Benutzer-Daten

## Änderungen am Datenmodel

Solltest du Änderungen an den Daten vornehmen, die in der Datenbank gespeichert werden, musst du die Datenbankmigrationen aktualisieren.

1. Führe `aerich migrate --name=<name der migration>` aus, um eine neue Migration zu erstellen.
2. Führe `aerich upgrade` aus, um die Datenbank auf den neuesten Stand zu bringen.

### Best Practices

- Verwende beschreibende Namen für Migrationen (z.B. `add_user_role_field`)
- Teste Migrationen lokal vor dem Commit
- Dokumentiere Breaking Changes in der Commit-Message
- Verwende `aerich downgrade` vorsichtig in der Entwicklung

## Konfiguration

Die Datenbank-Konfiguration befindet sich in `tortoiseConfig.py`:

```python
TORTOISE_ORM = {
    "connections": {
        "default": "sqlite://data/db.sqlite3"
    },
    "apps": {
        "models": {
            "models": ["models.database", "aerich.models"],
            "default_connection": "default",
        },
    },
}
```

## Migrationen

Alle Migrationen befinden sich im `migrations/` Ordner.

## Troubleshooting

### Datenbank ist korrupt

1. Sichere die aktuelle Datenbank: `cp data/db.sqlite3 data/db.sqlite3.backup`
2. Lösche die Datenbank: `rm data/db.sqlite3`
3. Initialisiere neu: `aerich upgrade`

### Migration schlägt fehl

1. Überprüfe die Datenbank-Integrität
2. Prüfe, ob alle Modelle korrekt importiert sind in `tortoiseConfig.py`
3. Versuche ein `aerich downgrade` zur vorherigen Version
4. Konsultiere die Tortoise ORM [Dokumentation](https://tortoise-orm.readthedocs.io/en/latest/)

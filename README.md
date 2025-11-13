*Ein wilder Bot der Seminargruppe CS24-1 erscheint…*

# Development Setup

Es gibt zwei Wege, den Bot lokal auszuführen: Manuell oder über Development Containers (empfohlen).

## Development Container (empfohlen)

1. Stelle sicher, dass du [Docker](https://www.docker.com/get-started/) oder [Podman](https://podman.io/getting-started/installation) installiert hast.
2. Klone das Repo und öffne das Projekt in [Visual Studio Code](https://code.visualstudio.com/) (oder einem anderen Editor, der [Dev Containers](https://code.visualstudio.com/docs/remote/containers) unterstützt).
3. Kopiere die `EXAMPLE.env` Datei und nenne sie in `.env` um. Fülle die Werte aus.
4. Beim öffnen des Projekts sollte VS Code dich fragen, ob du den Ordner in einem Container öffnen möchtest. Bestätige dies. (Sollte die Abfrage nicht erscheinen, öffne die Kommando-Palette mit `Strg+Shift+P` und suche nach `Dev Containers: Reopen in Container`).
5. Warte, bis der Container gebaut und gestartet ist. Dies kann einige Minuten dauern.
6. Öffne ein neues Terminal in VS Code und führe `python3 main.py` aus, um den Bot zu starten.

## Manuell

Diese Schritte sind umständlicher und nicht empfohlen.

1. Clone das Repo
2. Erstelle eine venv mit `python3 -m venv venv` oder dem Tool, dass deine IDE mitbringt.
3. Installiere alle Pakete aus `requirements.txt` und `torch.requirements.txt` mit `python3 -m pip install -r requirements.txt` (bzw. `python3 -m pip install -r requirements.txt`).
4. Erstelle einen Testbot auf der [Discord Developers Seite](https://discord.com/developers)
5. Kopiere die `EXAMPLE.env` Datei und nenne sie in `.env` um. Fülle die Werte aus.
6. Richte die Datenbank ein. Befolge [diese Anleitung](#Datenbank-Einrichtung).
7. Starte den Bot, indem du die `main.py` Datei mittels `python3 main.py` ausführst.

# Datenbank

Der Bot benutzt eine SQLite Datenbank mit [Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/) als ORM.

Dafür muss die Datenbank initialisiert werden, bevor der Bot gestartet wird.

## Initialisierung

### Development Container

Wenn du Development Container benutzt, wird die Datenbank beim Start des Containers automatisch eingerichtet. Andernfalls musst du die Datenbank manuell einrichten.

### Manuell

1. Zunächst musst du das Tortoise-CLI tool `aerich` installieren. Führe dazu `python3 -m pip install aerich` aus.

2. Nun benötigst du eine Datenbank. Erstelle dafür eine leere Datei namens `db.sqlite3` im Ordner `data/`.

3. Führe im Projekt-Root `aerich upgrade` aus, um die Datenbank auf die neueste Version zu bringen.

## Änderungen am Datenmodel

Solltest du Änderungen an den Daten vornehmen, die in der Datenbank gespeichert werden, musst du die Datenbankmigrationen aktualisieren.

1. Führe `aerich migrate --name=<name der migration>` aus, um eine neue Migration zu erstellen.
2. Führe `aerich upgrade` aus, um die Datenbank auf den neuesten Stand zu bringen.

# Testing

The project includes a pytest-based test suite. To run tests locally:

## Running Tests

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run all tests:
```bash
pytest
```

3. Run tests with coverage:
```bash
pytest --cov
```

4. Run specific test files:
```bash
pytest tests/test_example.py
```

## Pre-commit Hooks

The project uses pre-commit hooks for code quality. To set up:

```bash
pre-commit install
```

To run manually on all files:
```bash
pre-commit run --all-files
```

## Continuous Integration

Tests run automatically on GitHub Actions for Python 3.10, 3.11, and 3.12 on pushes and pull requests to the main branch.

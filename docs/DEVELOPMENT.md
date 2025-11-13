# Development Setup

Es gibt zwei Wege, den Bot lokal auszuführen: Manuell oder über Development Containers (empfohlen).

## Development Container (empfohlen)

1. Stelle sicher, dass du [Docker](https://www.docker.com/get-started/) oder [Podman](https://podman.io/getting-started/installation) installiert hast.
2. Klone das Repo und öffne das Projekt in [Visual Studio Code](https://code.visualstudio.com/) (oder einem anderen Editor, der [Dev Containers](https://code.visualstudio.com/docs/remote/containers) unterstützt).
3. Erstelle einen Testbot auf der [Discord Developers Seite](https://discord.com/developers)
4. Kopiere die `EXAMPLE.env` Datei und nenne sie in `.env` um. Fülle die Werte aus.
5. Beim öffnen des Projekts sollte VS Code dich fragen, ob du den Ordner in einem Container öffnen möchtest. Bestätige dies. (Sollte die Abfrage nicht erscheinen, öffne die Kommando-Palette mit `Strg+Shift+P` und suche nach `Dev Containers: Reopen in Container`).
6. Warte, bis der Container gebaut und gestartet ist. Dies kann einige Minuten dauern.
7. Öffne ein neues Terminal in VS Code und führe `python3 main.py` aus, um den Bot zu starten.

## Manuell

Diese Schritte sind umständlicher und nicht empfohlen.

1. Clone das Repo
2. Erstelle eine venv mit `python3 -m venv venv` oder dem Tool, dass deine IDE mitbringt.
3. Installiere alle Pakete aus `requirements.txt` und `requirements-torch.txt` mit `python3 -m pip install -r requirements.txt` (bzw. `python3 -m pip install -r requirements-torch.txt`).
4. Erstelle einen Testbot auf der [Discord Developers Seite](https://discord.com/developers)
5. Kopiere die `EXAMPLE.env` Datei und nenne sie in `.env` um. Fülle die Werte aus.
6. Richte die Datenbank ein. Befolge [diese Anleitung](DATABASE.md#manuell).
7. Starte den Bot, indem du die `main.py` Datei mittels `python3 main.py` ausführst.

## Development Tools

Das Projekt benutzt verschiedene Tools zur Sicherstellung der Code-Qualität:

### Pre-commit Hooks

Das Projekt nutzt pre-commit hooks für Code-Qualität. In Development Containers sind diese bereits installiert.

Andernfalls richte sie manuell mit [dieser Anleitung](TESTING.md#pre-commit-hooks) ein.

### Code-Formatierung

- **YAPF**: Code-Formatierung nach PEP 8 mit 80 Zeichen Zeilenlänge
- **isort**: Import-Sortierung
- **mypy**: Type Checking

### VS Code Extensions

Bei Nutzung des Development Containers werden folgende Extensions automatisch installiert:

- `ms-python.python`: Python language support
- `ms-python.mypy-type-checker`: Type checking
- `eeyore.yapf`: Code formatting
- `ms-python.isort`: Import sorting
- `ChristianDein.python-radon`: Code complexity analysis
- `njpwerner.autodocstring`: Docstring generation
- `github.vscode-github-actions`: GitHub Actions support

## Lokale Tests

Siehe [TESTING.md](TESTING.md) für Informationen zum Ausführen von Tests.

# CS24-1 Discord Bot

*Ein wilder Bot der Seminargruppe CS24-1 erscheint…*

Ein Discord-Bot für die Seminargruppe CS24-1 mit Features wie KI-basierter Code-Übersetzung, Meme-Sammlung und Mensa-Speiseplan-Updates.

## Technologie-Stack

- **Python 3.10+** mit py-cord (discord.py fork)
- **Tortoise ORM** mit SQLite für Datenbank-Management
- **OpenAI API** für Code-Übersetzungsfunktionen
- **PIL & EasyOCR** für Meme-Verarbeitung
- **Docker** für Development und Deployment

## Features

- 🤖 **AI Service**: Code-Übersetzung mit OpenAI API und täglichen Nutzungslimits
- 🎨 **Meme Service**: Automatische Meme-Sammlung und Bot-Banner-Rotation
- 🍽️ **Mensa Service**: Tägliche Mensa-Speiseplan-Updates
- 💬 **Quote Service**: Zitat-Sammlung und -Verwaltung

## Quick Start

### Development Container (empfohlen)

1. Installiere [Docker](https://www.docker.com/get-started/) oder [Podman](https://podman.io/getting-started/installation)
2. Klone das Repository
3. Öffne das Projekt in [Visual Studio Code](https://code.visualstudio.com/)
4. Kopiere `EXAMPLE.env` zu `.env` und fülle die Werte aus
5. Öffne in Dev Container (VS Code fragt automatisch)
6. Führe `python3 main.py` aus

Siehe [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) für detaillierte Anweisungen.

## Dokumentation

### Für Entwickler

- **[Development Setup](docs/DEVELOPMENT.md)** - Lokales Setup und Tools
- **[Code Structure](docs/CODE_STRUCTURE.md)** - Code-Organisation, Stil-Konventionen und Patterns
- **[Database](docs/DATABASE.md)** - Datenbank-Initialisierung, Migrationen, und Best Practices
- **[Testing](docs/TESTING.md)** - Test-Ausführung, Coverage, Linting, und CI

### Infrastruktur

- **[Docker Images](docs/DOCKER_IMAGES.md)** - Multi-Layer Docker-Strategie und Image-Übersicht
- **[Workflow Dependencies](docs/WORKFLOW_DEPENDENCIES.md)** - GitHub Actions Workflow-Abhängigkeiten

## Projektstruktur

```
.
├── src/              # Quellcode
│   ├── cogs/        # Discord Command-Module (Cogs)
│   ├── models/      # Datenmodelle
│   │   ├── ai/     # AI-bezogene Modelle
│   │   ├── database/ # Datenbank-Modelle (Tortoise ORM)
│   │   └── mensa/  # Mensa-bezogene Modelle
│   ├── utils/       # Hilfsfunktionen
│   ├── migrations/  # Datenbank-Migrationen (aerich)
│   └── main.py      # Bot-Einstiegspunkt
├── tests/           # Pytest Test Suite
├── docs/            # Dokumentation
├── docker/          # Docker-Konfiguration
└── data/            # Laufzeitdaten (gitignored)
```

## Lizenz

Siehe [LICENSE](LICENSE) Datei für Details.

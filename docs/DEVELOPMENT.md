# Development Setup

There are two ways to run the bot locally: Manually or using Development Containers (recommended).

## Development Container (recommended)

1. Make sure you have [Docker](https://www.docker.com/get-started/) or [Podman](https://podman.io/getting-started/installation) installed.
2. Clone the repo and open the project in [Visual Studio Code](https://code.visualstudio.com/) (or another editor that supports [Dev Containers](https://code.visualstudio.com/docs/remote/containers)).
3. Create a test bot on the [Discord Developers page](https://discord.com/developers)
4. Copy the `EXAMPLE.env` file and rename it to `.env`. Fill in the values.
5. When opening the project, VS Code should ask if you want to open the folder in a container. Confirm this. (If the prompt doesn't appear, open the command palette with `Ctrl+Shift+P` and search for `Dev Containers: Reopen in Container`).
6. Wait for the container to build and start. This may take a few minutes.
7. Open a new terminal in VS Code and run `python3 main.py` to start the bot.

## Manual

These steps are more cumbersome and not recommended.

1. Clone the repo
2. Create a venv with `python3 -m venv venv` or the tool that your IDE provides.
3. Install all packages from `requirements.txt` and `requirements-torch.txt` with `python3 -m pip install -r requirements.txt` (and `python3 -m pip install -r requirements-torch.txt`).
4. Create a test bot on the [Discord Developers page](https://discord.com/developers)
5. Copy the `EXAMPLE.env` file and rename it to `.env`. Fill in the values.
6. Set up the database. Follow [these instructions](DATABASE.md#manual).
7. Start the bot by running the `main.py` file with `python3 main.py`.

## Development Tools

The project uses various tools to ensure code quality:

### Code Formatting

- **YAPF**: Code formatting according to PEP 8 with 80 character line length
- **isort**: Import sorting
- **mypy**: Type checking

### VS Code Extensions

When using the Development Container, the following extensions are automatically installed:

- `ms-python.python`: Python language support
- `ms-python.mypy-type-checker`: Type checking
- `eeyore.yapf`: Code formatting
- `ms-python.isort`: Import sorting
- `ChristianDein.python-radon`: Code complexity analysis
- `njpwerner.autodocstring`: Docstring generation
- `github.vscode-github-actions`: GitHub Actions support

## Code Structure

For detailed information on code organization, style conventions, and patterns used in this project, see [CODE_STRUCTURE.md](CODE_STRUCTURE.md).

## Local Testing

See [TESTING.md](TESTING.md) for information on running tests.

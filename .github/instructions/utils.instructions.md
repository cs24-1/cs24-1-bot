---
applyTo: "**/utils/**/*.py"
---

## Utility Function Requirements

When creating or modifying utility functions:

1. **Pure functions** - Prefer pure functions without side effects where possible
2. **Type hints** - Complete type annotations for all parameters and return values
3. **Docstrings** - Document purpose, parameters, return value, and any exceptions raised
4. **Error handling** - Handle edge cases and invalid inputs gracefully
5. **Logging** - Use module-level logger for important operations
6. **Constants** - Use values from `utils/constants.py`, don't hardcode
7. **Testability** - Design functions to be easily testable
8. **Single responsibility** - Each function should do one thing well
9. **Async considerations** - If the function does I/O, make it async
10. **Line length** - Keep lines under 80 characters (see CODE_STRUCTURE.md)
11. **Imports** - Organize imports in three groups: stdlib, third-party, local

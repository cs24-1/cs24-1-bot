---
applyTo: "**/models/database/**/*.py"
---

## Database Model Requirements

When creating or modifying database models:

1. **Inherit from BaseModel** - All models must inherit from `models.database.baseModel.BaseModel`
2. **Add descriptions** - Every field must have a `description` parameter
3. **Use appropriate field types** - Follow Tortoise ORM conventions
4. **Create migrations** - After model changes, run `aerich migrate --name=descriptive_name`
5. **Document relationships** - Use clear ForeignKey and ManyToMany field names
6. **Add docstrings** - Document what the model represents and any business logic
7. **Type hints** - Include proper type hints for all methods
8. **Keep models simple** - Business logic should be in utility functions or Cogs, not models
9. **Primary keys** - Use `fields.IntField(pk=True, description="...")` for primary keys
10. **Unique constraints** - Use `unique=True` parameter where appropriate (e.g., discord_id)

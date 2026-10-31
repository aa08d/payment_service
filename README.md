# app

Service skeleton (clean architecture): common domain and application code, mediator, Dishka DI.

```
src/app/
  domain/common/        Entity, AggregateRoot, ValueObject, Event, DomainError
  application/common/   Command/Query/Event handlers, Mediator + MediatorRegistry, UnitOfWork, DTO, pagination, exceptions
  bootstrap/di/         DishkaMediator, MediatorProvider, mediator registry
```

```bash
make install   # uv sync + pre-commit install (run `git init` first)
make check     # ruff + mypy strict + import-linter + pytest
```

## How to add a feature

1. `domain/<feature>/` - entities, value objects, events (no frameworks).
2. `application/<feature>/` - commands/queries/handlers, interfaces.
3. Register handlers in `bootstrap/di/registry.py` and provide them in `bootstrap/di/providers.py`.

To rename the package: rename `src/app`, then replace `app` in `pyproject.toml`, `mypy.ini`, `.importlinter`, `ruff.toml` and imports.

import ast
import importlib.resources
from pathlib import Path
from typing import Final

import pytest

import shazamio

# What the package promises to keep working. Removing a name from here is a
#  breaking change for anyone importing it, so it takes two deliberate edits.
_EXPORTS: Final[tuple[str, ...]] = (
    "AiohttpTransport",
    "BadPayload",
    "BadResponse",
    "ChartTrack",
    "Device",
    "GenreMusic",
    "NotFound",
    "RateLimited",
    "Request",
    "Response",
    "ResponseTrack",
    "Retry",
    "SearchParams",
    "Shazam",
    "ShazamError",
    "SignatureError",
    "TrackInfo",
    "Transport",
    "TransportError",
    "YoutubeData",
)


_PACKAGE_ROOT: Final[Path] = Path(shazamio.__file__).parent
# A module's `logging.getLogger(name=__name__)` is configured by name, never imported.
_LOGGER: Final[str] = "logger"

# The root `__init__.py` only re-exports, and `_EXPORTS` above pins it.
_MODULES: Final[tuple[Path, ...]] = tuple(
    path for path in sorted(_PACKAGE_ROOT.rglob("*.py")) if path != _PACKAGE_ROOT / "__init__.py"
)


def test_the_installed_package_carries_the_typing_marker() -> None:
    assert importlib.resources.files("shazamio").joinpath("py.typed").is_file()


def test_the_package_exports_exactly_the_documented_surface() -> None:
    assert shazamio.__all__ == list(_EXPORTS)


def test_every_exported_name_resolves() -> None:
    unresolvable = [name for name in shazamio.__all__ if not hasattr(shazamio, name)]

    assert unresolvable == []


# A traceback, a `repr` and `pickle` name a class by its `__module__`, which
#  for a class defined in a private module would be a path nobody may import.
def test_no_export_names_a_private_module() -> None:
    private = [
        name
        for name in shazamio.__all__
        if getattr(shazamio, name).__module__.startswith("shazamio._")
    ]

    assert private == []


def _top_level_names(tree: ast.Module) -> tuple[list[str], list[str] | None]:
    defined: list[str] = []
    declared: list[str] | None = None

    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.append(node.name)
            continue

        targets = node.targets if isinstance(node, ast.Assign) else []

        if isinstance(node, ast.AnnAssign):
            targets = [node.target]

        for target in targets:
            if not isinstance(target, ast.Name):
                continue

            if target.id == "__all__":
                declared = ast.literal_eval(node.value)
                continue

            defined.append(target.id)

    return defined, declared


@pytest.mark.parametrize(
    "path",
    [pytest.param(path, id=str(path.relative_to(_PACKAGE_ROOT))) for path in _MODULES],
)
def test_every_module_declares_exactly_its_public_names(path: Path) -> None:
    defined, declared = _top_level_names(ast.parse(path.read_text(encoding="utf-8")))

    assert isinstance(declared, list)
    assert set(declared) == {
        name for name in defined if not name.startswith("_") and name != _LOGGER
    }

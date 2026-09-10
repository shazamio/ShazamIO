# The one home of every command this project runs. A CI job and a local check are
#  the same string here rather than two copies that drift apart.

# `bash` on the CI runners and on a developer machine, so a recipe behaves the
#  same everywhere. The default is `sh`, which on Windows is whatever Git happens
#  to have put on `PATH`.
set shell := ["bash", "-uc"]

[doc("Show the recipes")]
default:
    @just --list

[doc("Install the dependencies, exactly as locked")]
install:
    uv sync --locked

[doc("Check the formatting")]
lint:
    uv run black --check .

[doc("Reformat the tree")]
format:
    uv run black .

[doc("Run the test suite")]
test:
    uv run pytest

[doc("Run everything CI runs")]
ci: lint test

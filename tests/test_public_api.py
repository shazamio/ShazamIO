import importlib.resources


def test_the_installed_package_carries_the_typing_marker() -> None:
    assert importlib.resources.files("shazamio").joinpath("py.typed").is_file()

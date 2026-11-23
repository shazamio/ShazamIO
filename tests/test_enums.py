from shazamio import GenreMusic


# The README promises the value in an f-string, which a `(str, Enum)` mixin
#  renders as `GenreMusic.ROCK`.
def test_a_genre_formats_as_its_value() -> None:
    assert f"{GenreMusic.ROCK}" == "rock"

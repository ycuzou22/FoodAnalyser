import inference
import training


def test_packages_import() -> None:
    assert training.__doc__
    assert inference.__doc__

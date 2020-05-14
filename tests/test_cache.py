import random

import pytest

import ophyd
import typhos.cache


@pytest.fixture(scope='function')
def describe_cache():
    cache = typhos.cache.get_global_describe_cache()
    cache.clear()
    yield cache
    cache.clear()


@pytest.fixture(scope='function')
def type_cache(describe_cache):
    cache = typhos.cache.get_global_widget_type_cache()
    cache.clear()
    yield cache
    cache.clear()


@pytest.fixture(scope='function')
def sig():
    name = 'test{}'.format(random.randint(0, 10000))
    sig = ophyd.Signal(name=name)
    yield sig
    sig.destroy()


@pytest.mark.skip(reason='Race condition in test')
def test_describe_cache_signal(qtbot, describe_cache, sig):
    # Check that `new_description` is emitted with the correct args:
    with qtbot.wait_signal(describe_cache.new_description) as block:
        assert describe_cache.get(sig) is None

    assert block.args == [sig, sig.describe()[sig.name]]

    # And the description is now readily available:
    assert describe_cache.get(sig) == sig.describe()[sig.name]

    # And that clearing the cache works:
    describe_cache.clear()
    assert describe_cache.get(sig) is None


@pytest.mark.skip(reason='Race condition in test')
def test_widget_type_signal(qtbot, type_cache, sig):
    with qtbot.wait_signal(type_cache.widgets_determined) as block:
        assert type_cache.get(sig) is None

    assert block.args[0] is sig
    assert type_cache.get(sig) is block.args[1]
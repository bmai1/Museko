import os
import pytest
import discogs_client

pytestmark = pytest.mark.integration

def test_discogs_client_can_fetch_a_known_release():
    d = discogs_client.Client(
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
    )
    # https://www.discogs.com/release/249504
    release = d.release(249504)
    assert release.title is not None
import pytest
import yt_dlp

pytestmark = pytest.mark.integration

def test_yt_dlp_can_extract_info_without_downloading():
    ydl_opts = {"quiet": True, "skip_download": True}
    url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    assert info is not None
    assert "title" in info
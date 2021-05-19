from databroker.tutorial_utils import _fetch_into_memory_and_unzip_to_disk


def fetch_example(version=1):
    if version != 1:
        raise ValueError("Only version 1 is known.")
    name = "boost_beamtime_productivity_example"
    url = "https://nsls2datasamples.blob.core.windows.net/bluesky-tutorial-example-data/boost_beamtime_productivity_example.zip"
    return _fetch_into_memory_and_unzip_to_disk(name, url).v1

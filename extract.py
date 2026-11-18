import io

import pandas as pd
import requests

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


API_URL = 'https://storage.googleapis.com/uber-data-engineering-project-darshil/uber_data.csv'
REQUEST_TIMEOUT = (5, 60)  # connect timeout, read timeout


@data_loader
def load_data_from_api(*args, **kwargs):
    """Load the source CSV, failing fast on network and HTTP errors."""
    response = requests.get(API_URL, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    return pd.read_csv(io.StringIO(response.text), sep=',')


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'

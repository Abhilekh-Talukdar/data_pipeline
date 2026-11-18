import importlib
import sys
import types
import unittest
from unittest.mock import Mock


def _identity_decorator(function=None, **_kwargs):
    if function is None:
        return lambda decorated: decorated
    return function


# The pipeline runs inside Mage. Stub its decorators and external data libraries
# so these unit tests can exercise the loader without installing Mage or pandas.
pandas_stub = types.ModuleType('pandas')
pandas_stub.read_csv = Mock(name='read_csv')
requests_stub = types.ModuleType('requests')
requests_stub.get = Mock(name='get')
mage_stub = types.ModuleType('mage_ai')
mage_stub.__path__ = []
data_preparation_stub = types.ModuleType('mage_ai.data_preparation')
data_preparation_stub.__path__ = []
decorators_stub = types.ModuleType('mage_ai.data_preparation.decorators')
decorators_stub.data_loader = _identity_decorator
decorators_stub.test = _identity_decorator

sys.modules.update({
    'pandas': pandas_stub,
    'requests': requests_stub,
    'mage_ai': mage_stub,
    'mage_ai.data_preparation': data_preparation_stub,
    'mage_ai.data_preparation.decorators': decorators_stub,
})

extract = importlib.import_module('extract')


class LoadDataFromApiTests(unittest.TestCase):
    def setUp(self):
        extract.requests.get.reset_mock()
        extract.requests.get.side_effect = None
        extract.pd.read_csv.reset_mock()
        extract.pd.read_csv.return_value = object()
        self.response = Mock()
        self.response.text = 'id,value\\n1,example\\n'
        extract.requests.get.return_value = self.response

    def test_uses_bounded_timeout_checks_status_and_parses_csv(self):
        result = extract.load_data_from_api()

        extract.requests.get.assert_called_once_with(
            extract.API_URL,
            timeout=(5, 60),
        )
        self.response.raise_for_status.assert_called_once_with()
        extract.pd.read_csv.assert_called_once()
        csv_buffer = extract.pd.read_csv.call_args.args[0]
        self.assertEqual(csv_buffer.getvalue(), self.response.text)
        self.assertEqual(extract.pd.read_csv.call_args.kwargs, {'sep': ','})
        self.assertIs(result, extract.pd.read_csv.return_value)

    def test_http_error_stops_before_csv_parsing(self):
        self.response.raise_for_status.side_effect = RuntimeError('HTTP 503')

        with self.assertRaisesRegex(RuntimeError, 'HTTP 503'):
            extract.load_data_from_api()

        extract.pd.read_csv.assert_not_called()

    def test_request_timeout_or_connection_error_is_propagated(self):
        extract.requests.get.side_effect = TimeoutError('request timed out')

        with self.assertRaisesRegex(TimeoutError, 'request timed out'):
            extract.load_data_from_api()

        extract.pd.read_csv.assert_not_called()


if __name__ == '__main__':
    unittest.main()

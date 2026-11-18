# data_pipeline

A Mage-based pipeline that extracts the source Uber trips CSV, transforms it into dimension and fact tables, and exports the results to BigQuery.

## API loader reliability

The source CSV loader uses a 5-second connection timeout and a 60-second read timeout. It checks the HTTP response status before parsing the body, so network failures and non-success HTTP responses fail the Mage block instead of being passed to the CSV parser.

## Run the loader regression tests

The focused tests use mocks for Mage, pandas, and requests, so they do not require cloud credentials or external services:

```bash
python -m unittest discover -s tests -v
```

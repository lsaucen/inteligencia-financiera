from src.ingest.fred import parse_fred_csv

SAMPLE = "DATE,CPIAUCSL\n2020-01-01,258.687\n2020-02-01,.\n"


def test_parse_fred_csv_handles_missing_dot():
    df = parse_fred_csv(SAMPLE, "CPIAUCSL")
    assert list(df.columns) == ["series_id", "date", "value"]
    assert len(df) == 1  # the "." row (FRED missing marker) is dropped
    assert df.iloc[0]["value"] == 258.687

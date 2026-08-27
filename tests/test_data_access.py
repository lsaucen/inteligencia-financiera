from app.data_access import DataAccess
from src.export_snapshot import export_snapshot


def test_snapshot_and_db_return_same_shape():
    export_snapshot()
    db = DataAccess(use_snapshot=False).prices()
    snap = DataAccess(use_snapshot=True).prices()
    assert list(db.columns) == list(snap.columns)
    assert len(db) == len(snap)

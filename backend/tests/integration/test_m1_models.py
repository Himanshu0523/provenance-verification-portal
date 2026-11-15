import uuid
import pytest
from app.modules.creators.repository import CreatorRepository
from app.modules.media_assets.repository import MediaAssetRepository

pytestmark = pytest.mark.asyncio

async def test_create_and_fetch_creator(db):
    repo = CreatorRepository(db)
    c = await repo.create(display_name="Alice", email="alice@example.com")
    await db.commit()
    fetched = await repo.get(c.id)
    assert fetched is not None and fetched.display_name == "Alice"

async def test_media_asset_persists_with_creator(db):
    c = await CreatorRepository(db).create(display_name="Bob")
    a = await MediaAssetRepository(db).create(
        creator_id=c.id,
        original_filename="cat.png",
        mime_type="image/png",
        file_size=1234,
        sha256_hash="a" * 64,
        storage_key="r2://bucket/cat.png",
    )
    await db.commit()
    found = await MediaAssetRepository(db).find_by_sha256("a" * 64)
    assert len(found) == 1 and found[0].id == a.id

async def test_duplicate_sha256_per_creator_rejected(db):
    from sqlalchemy.exc import IntegrityError
    c = await CreatorRepository(db).create(display_name="Carol")
    repo = MediaAssetRepository(db)
    await repo.create(
        creator_id=c.id, original_filename="x.png", mime_type="image/png",
        file_size=1, sha256_hash="b" * 64, storage_key="r2://b/x.png",
    )
    await db.commit()
    with pytest.raises(IntegrityError):
        await repo.create(
            creator_id=c.id, original_filename="x2.png", mime_type="image/png",
            file_size=1, sha256_hash="b" * 64, storage_key="r2://b/x2.png",
        )
        await db.commit()
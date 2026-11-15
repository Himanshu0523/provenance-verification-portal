import uuid
from datetime import datetime , timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError , NotFoundError , ValidationError
from app.core.security import verify_ed25519
from app.modules.creators.models import Creator , CreatorKey
from app.modules.creators.repository import CreatorRepository
from app.modules.creators.validators import validate_and_fingerprint


class CreatorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CreatorRepository(db)
        
    async def register(self , display_name: str , email: str | None) -> Creator:
        try :
            creator == await self.repo.create(display_name = display_name , email = email)
        except ValueError as exc:
            raise ConflictError(str(exc)) from exc
        await self.db.commit()
        return creator
    
    async def get(self, creator_id: uuid.UUID) -> Creator:
        creator = await self.repo.get(creator_id)
        if creator is None:
            raise NotFoundError("creator not found")
        return creator
    
    async def register_key(self, creator_id: uuid.UUID, public_key: str, algorithm: str , label: str | None ) -> CreatorKey:
        await self.get(creator_id)
        try :
            _, key_id = validate_and_fingerprint(public_key)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        
        existing = await self.repo.get_key(key_id)
        if existing is not None:
            raise ConflictError("this public key is already registered")
        
        try :
            key = await self.repo.add_key(
                creator_id= creator_id,
                key_id=key_id,
                public_key= public_key,
                algorithm=algorithm,
                label=label,
            )
        except ValueError as exc:
            raise ConflictError(str(exc)) from exc
        await self.db.commit()
        return key
    
    
    async def list_keys(self , creator_id: uuid.UUID) ->list[CreatorKey]:
        await self.get(creator_id)
        return await self.repo.list_keys(creator_id)
    
    
    async def revoke_key(self, creator_id: uuid.UUID, key_id: str) -> CreatorKey:
        await self.get(creator_id)
        key = await self.repo.get_key(key_id)
        if key is None or key.creator_id != creator_id:
            raise NotFoundError("key not found for this creator")
        if key.status != "revoked":
            key.status = "revoked"
            key.revoked_at = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(key)
        return key
    
    
    async def verify_signature(self, creator_id: uuid.UUID, payload: str, signature: str,
        key_id: str | None,) -> tuple[bool, str, str | None]:
        """Return (valid, key_id, reason)."""
        await self.get(creator_id)

        if key_id:
            key = await self.repo.get_key(key_id)
            if key is None or key.creator_id != creator_id:
                raise NotFoundError("key not found for this creator")
            keys = [key]
        else:
            keys = await self.repo.list_keys(creator_id)
            if not keys:
                raise ValidationError("creator has no registered keys")

        for key in keys:
            if key.status == "revoked":
                if key_id:
                    return False, key.key_id, "key_revoked"
                continue
            if verify_ed25519(key.public_key, payload.encode("utf-8"), signature):
                return True, key.key_id, None
        return False, (key_id or keys[0].key_id), "signature_invalid"
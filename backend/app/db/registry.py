# Import all models so that Base.metadata is populated before Alembic runs.
from app.modules.creators import models as _creators  # noqa: F401
from app.modules.media_assets import models as _assets  # noqa: F401
from app.modules.embeddings import models as _emb  # noqa: F401
from app.modules.lineage import models as _lin  # noqa: F401
from app.modules.audit import models as _audit  # noqa: F401
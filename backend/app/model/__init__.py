"""app.model package initializer.

Import model modules here so that a top-level import like
`from app.model import *` will load all model classes and register their
tables with the shared metadata (Base.metadata). This prevents issues where
an association table is declared before the target table has been imported,
which can cause SQLAlchemy to raise NoReferencedTableError during
Base.metadata.create_all(...).
"""

# Import model modules to ensure their tables are registered on Base.metadata
from .users import *
from .features import *
from .packages import *
from .user_features import *
from .transactions import *

__all__ = [
	"User",
	"Feature",
	"Package",
	"UserFeature",
	"Transaction",
]

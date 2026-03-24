"""Python 3.9 compatibility helpers."""

from __future__ import annotations

import sys

if sys.version_info >= (3, 10):
    pass
else:
    pass

# For 3.9 compat, we use Union[X, None] instead of X | None in runtime annotations.
# With `from __future__ import annotations`, X | None works in type hints everywhere.

from typing import TYPE_CHECKING
from models import Row

if TYPE_CHECKING:
    Shape = Row
else:
    import models

if enabled:
    from models import Other

if TYPE_CHECKING:
    pass
elif enabled:
    import models

if not TYPE_CHECKING:
    import models

if TYPE_CHECKING or enabled:
    import models

if (TYPE_CHECKING or enabled) and other:
    import models

if enabled and (typing.TYPE_CHECKING or other):
    from models import Row

if not (TYPE_CHECKING and enabled):
    import models

if not TYPE_CHECKING and enabled:
    pass
else:
    import models

if TYPE_CHECKING and enabled:
    pass
else:
    import models

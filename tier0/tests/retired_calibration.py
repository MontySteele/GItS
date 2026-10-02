"""THE CALIBRATION IS RETIRED (legacy cleanup pick 5, ruled 2026-10-01).

"tier0 calibration is retired until a kit reaches Balance, then re-measured
on the current kits." The frozen bands and scorecards were measured on the
shipped kits, which are deleted (stage 6); they skip, they are not re-banded.
"""

import pytest

RETIRED_CALIBRATION = pytest.mark.skip(
    reason="calibration retired until a kit reaches Balance, 2026-10-01 "
           "(review/active/legacy-cleanup-2026-10-01.md, pick 5)")

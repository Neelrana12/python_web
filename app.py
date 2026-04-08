"""WELLTRADE SURGIPHARMA - ANALYTICS DASHBOARD (SIMPLIFIED).

- `gunicorn app:app` imports this module and uses the `app` variable.
- All routes and helpers are in the `welltrade_app/` package.
"""

from __future__ import annotations

import os

from welltrade_app import create_app


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = create_app(base_dir=BASE_DIR)


if __name__ == "__main__":
    debug = (os.environ.get("WELLTRADE_DEBUG") or "").strip() in {"1", "true", "True", "yes", "YES"}
    app.run(debug=debug, port=5000)

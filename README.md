# ShopPilot

A starter Flask storefront with product browsing, search, category filtering, a session-based cart, and a demo admin page for adding products.

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Start the app:

```bash
python app.py
```

6. Open http://127.0.0.1:5000

## Important

- This is a reconstructed starter version, not a recovered copy of the previous ShopPilot folder.
- The admin page is intentionally a demo and has no login protection. Do not deploy publicly until authentication, CSRF protection, validation, and production configuration are added.
- Product data is stored in `data/inventory.json`.
- Replace the demo image URLs with your own licensed product images as needed.

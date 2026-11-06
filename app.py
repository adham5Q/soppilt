from flask import Flask, render_template, request, redirect, url_for, session, flash
from pathlib import Path
import json

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-production"
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "inventory.json"

def load_products():
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_products(products):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

@app.context_processor
def cart_context():
    cart = session.get("cart", {})
    return {"cart_count": sum(cart.values())}

@app.route("/")
def home():
    products = load_products()
    featured = products[:4]
    return render_template("index.html", products=featured)

@app.route("/products")
def products():
    all_products = load_products()
    category = request.args.get("category", "").strip()
    query = request.args.get("q", "").strip().lower()
    filtered = all_products
    if category:
        filtered = [p for p in filtered if p["category"] == category]
    if query:
        filtered = [p for p in filtered if query in p["name"].lower() or query in p["description"].lower()]
    categories = sorted({p["category"] for p in all_products})
    return render_template("products.html", products=filtered, categories=categories, selected_category=category, query=query)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = next((p for p in load_products() if p["id"] == product_id), None)
    if not product:
        return "Product not found", 404
    return render_template("product_details.html", product=product)

@app.post("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    product = next((p for p in load_products() if p["id"] == product_id), None)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("products"))
    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = min(cart.get(key, 0) + 1, product["stock"])
    session["cart"] = cart
    flash(f'{product["name"]} added to your cart.', "success")
    return redirect(request.referrer or url_for("products"))

@app.route("/cart")
def cart():
    products_by_id = {str(p["id"]): p for p in load_products()}
    items, total = [], 0
    for pid, qty in session.get("cart", {}).items():
        product = products_by_id.get(pid)
        if product:
            line_total = product["price"] * qty
            items.append({"product": product, "qty": qty, "line_total": line_total})
            total += line_total
    return render_template("cart.html", items=items, total=total)

@app.post("/cart/update")
def update_cart():
    cart = session.get("cart", {})
    products_by_id = {str(p["id"]): p for p in load_products()}
    for pid in list(cart):
        try:
            qty = int(request.form.get(f"qty_{pid}", cart[pid]))
        except ValueError:
            qty = cart[pid]
        if pid not in products_by_id or qty <= 0:
            cart.pop(pid, None)
        else:
            cart[pid] = min(qty, products_by_id[pid]["stock"])
    session["cart"] = cart
    flash("Cart updated.", "success")
    return redirect(url_for("cart"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    products = load_products()
    if request.method == "POST":
        # Demo-only admin screen. Add authentication before public deployment.
        try:
            new_product = {
                "id": max([p["id"] for p in products], default=0) + 1,
                "name": request.form["name"].strip(),
                "category": request.form["category"].strip(),
                "price": float(request.form["price"]),
                "stock": max(0, int(request.form["stock"])),
                "description": request.form["description"].strip(),
                "image": request.form.get("image", "").strip() or "https://placehold.co/600x420?text=ShopPilot"
            }
            if not new_product["name"] or not new_product["category"] or new_product["price"] < 0:
                raise ValueError("Please enter valid product details.")
            products.append(new_product)
            save_products(products)
            flash("Product added.", "success")
        except (KeyError, ValueError):
            flash("Please check the product details and try again.", "error")
        return redirect(url_for("admin"))
    return render_template("admin.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)

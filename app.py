from flask import Flask, render_template, request, redirect, url_for, flash
import paypalrestsdk

app = Flask(__name__)
app.secret_key = 'your_secret_key'
paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": "your_paypal_client_id",
    "client_secret": "your_paypal_client_secret"
})

# Mock database for products
products = [
    {"id": 1, "name": "Product 1", "price": 10.0},
    {"id": 2, "name": "Product 2", "price": 15.0},
    {"id": 3, "name": "Product 3", "price": 20.0}
]

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        selected_product_ids = request.form.getlist('product')
        selected_products = [p for p in products if str(p["id"]) in selected_product_ids]
        return render_template('cart.html', products=selected_products)
    return redirect(url_for('index'))

@app.route('/checkout', methods=['POST'])
def checkout():
    selected_product_ids = request.form.getlist('product_id')
    total_amount = sum([p["price"] for p in products if str(p["id"]) in selected_product_ids])

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": url_for('index', _external=True),
            "cancel_url": url_for('cart', _external=True)
        },
        "transactions": [{
            "amount": {
                "total": f"{total_amount:.2f}",
                "currency": "USD"
            },
            "description": "eCommerce Purchase"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.method == "REDIRECT":
                redirect_url = link.href
                return redirect(redirect_url)
    else:
        flash(f'Error: {payment.error["message"]}', 'danger')
        return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)

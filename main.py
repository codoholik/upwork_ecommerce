from flask import Flask, render_template

app = Flask(__name__)

@app.route('/admin')
def admin():
    return render_template('admin_dashboard.html')

@app.route('/list_orders')
def list_orders():
    return render_template('list_orders.html')


if __name__ == '__main__':
    app.run(debug=True)

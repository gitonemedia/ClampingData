from flask import Flask, render_template, request, redirect, url_for
from models import db, Clamp

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/clamp', methods=['GET', 'POST'])
def clamp_form():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        clamp_type = request.form['clamp_type']
        quantity = request.form['quantity']
        
        new_clamp = Clamp(customer_name=customer_name, clamp_type=clamp_type, quantity=quantity)
        db.session.add(new_clamp)
        db.session.commit()
        
        return redirect(url_for('clamp_list'))
    
    return render_template('clamp_form.html')

@app.route('/clamps')
def clamp_list():
    clamps = Clamp.query.all()
    return render_template('clamp_list.html', clamps=clamps)

if __name__ == '__main__':
    app.run(debug=True)
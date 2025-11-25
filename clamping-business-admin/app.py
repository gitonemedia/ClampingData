from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clamping_business.db'
app.config['SECRET_KEY'] = '091043239123abc'

db = SQLAlchemy(app)

# Database Model
class ClampData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(200), nullable=False)
    registration = db.Column(db.String(100))
    clamp_date = db.Column(db.Date, nullable=False)
    time_in = db.Column(db.Time, nullable=False)
    time_released = db.Column(db.Time)
    offense = db.Column(db.String(300), nullable=False)
    payment_status = db.Column(db.String(50), default='Processing')  # Paid, Not Paid, Processing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ClampData {self.id}>'

# Appeals Model
class Appeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clamp_id = db.Column(db.Integer, db.ForeignKey('clamp_data.id'), nullable=False)
    clamp = db.relationship('ClampData', backref='appeals')
    appeal_date = db.Column(db.Date, nullable=False, default=datetime.today)
    appeal_reason = db.Column(db.Text, nullable=False)
    appeal_status = db.Column(db.String(50), default='Pending')  # Pending, Approved, Rejected
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Appeal {self.id}>'

# Routes
@app.route('/')
def index():
    clamps = ClampData.query.all()
    return render_template('index.html', clamps=clamps)

@app.route('/add-clamp', methods=['POST'])
def add_clamp():
    try:
        new_clamp = ClampData(
            location=request.form['location'],
            registration=request.form.get('registration',''),
            clamp_date=datetime.strptime(request.form['clamp_date'], '%Y-%m-%d').date(),
            time_in=datetime.strptime(request.form['time_in'], '%H:%M').time(),
            time_released=datetime.strptime(request.form['time_released'], '%H:%M').time() if request.form['time_released'] else None,
            offense=request.form['offense'],
            payment_status=request.form['payment_status']
        )
        db.session.add(new_clamp)
        db.session.commit()
        flash('Clamp data added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete-clamp/<int:id>')
def delete_clamp(id):
    try:
        clamp = ClampData.query.get_or_404(id)
        db.session.delete(clamp)
        db.session.commit()
        flash('Clamp data deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/edit-clamp/<int:id>', methods=['POST'])
def edit_clamp(id):
    try:
        clamp = ClampData.query.get_or_404(id)
        clamp.location = request.form['location']
        clamp.registration = request.form.get('registration','')
        clamp.clamp_date = datetime.strptime(request.form['clamp_date'], '%Y-%m-%d').date()
        clamp.time_in = datetime.strptime(request.form['time_in'], '%H:%M').time()
        clamp.time_released = datetime.strptime(request.form['time_released'], '%H:%M').time() if request.form['time_released'] else None
        clamp.offense = request.form['offense']
        clamp.payment_status = request.form['payment_status']
        db.session.commit()
        flash('Clamp data updated successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/invoicing')
def invoicing():
    paid_clamps = ClampData.query.filter_by(payment_status='Paid').all()
    return render_template('invoicing.html', paid_clamps=paid_clamps, now=datetime.now())


@app.route('/presentation/invoice/<int:id>')
def presentation_invoice(id):
    clamp = ClampData.query.get_or_404(id)
    return render_template('presentation_invoice.html', clamp=clamp, now=datetime.now())


@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

@app.route('/appeals')
def appeals():
    all_appeals = Appeal.query.all()
    return render_template('appeals.html', appeals=all_appeals)

@app.route('/add-appeal', methods=['POST'])
def add_appeal():
    try:
        new_appeal = Appeal(
            clamp_id=request.form['clamp_id'],
            appeal_reason=request.form['appeal_reason'],
            appeal_status=request.form['appeal_status']
        )
        db.session.add(new_appeal)
        db.session.commit()
        flash('Appeal added successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('appeals'))

@app.route('/delete-appeal/<int:id>')
def delete_appeal(id):
    try:
        appeal = Appeal.query.get_or_404(id)
        db.session.delete(appeal)
        db.session.commit()
        flash('Appeal deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('appeals'))

@app.route('/edit-appeal/<int:id>', methods=['POST'])
def edit_appeal(id):
    try:
        appeal = Appeal.query.get_or_404(id)
        appeal.appeal_reason = request.form['appeal_reason']
        appeal.appeal_status = request.form['appeal_status']
        appeal.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Appeal updated successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('appeals'))

@app.route('/api/clamp/<int:id>')
def get_clamp_details(id):
    """Return clamp location and registration as JSON for AJAX calls"""
    clamp = ClampData.query.get(id)
    if not clamp:
        return {'error': 'Clamp not found'}, 404
    return {
        'id': clamp.id,
        'location': clamp.location,
        'registration': clamp.registration or ''
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
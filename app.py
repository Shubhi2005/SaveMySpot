from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///savemyspot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model for queue reports
class QueueReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    queue_length = db.Column(db.Integer, nullable=False)
    report_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    votes = db.Column(db.Integer, default=0)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        try:
            location_name = request.form['location_name'].strip()
            latitude = float(request.form['latitude'])
            longitude = float(request.form['longitude'])
            queue_length = int(request.form['queue_length'])
            
            if not location_name or len(location_name) > 100:
                raise ValueError("Invalid location name")
            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                raise ValueError("Invalid coordinates")
            if queue_length < 0 or queue_length > 1000:
                raise ValueError("Unreasonable queue length")
        except (ValueError, KeyError) as e:
            return render_template('report.html', error=str(e))
    
        return render_template('report.html')
    

        # Create new report
        new_report = QueueReport(
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            queue_length=queue_length
        )
        
        db.session.add(new_report)
        db.session.commit()
        
        return redirect(url_for('index'))
    
    return render_template('report.html')

@app.route('/api/reports')
def get_reports():
    reports = QueueReport.query.all()
    reports_data = []
    for report in reports:
        reports_data.append({
            'id': report.id,
            'location_name': report.location_name,
            'latitude': report.latitude,
            'longitude': report.longitude,
            'queue_length': report.queue_length,
            'report_time': report.report_time.isoformat(),
            'votes': report.votes
        })
    return jsonify(reports_data)

@app.route('/api/vote/<int:report_id>', methods=['POST'])
def vote_report(report_id):
    report = QueueReport.query.get_or_404(report_id)
    report.votes += 1
    db.session.commit()
    return jsonify({'success': True, 'new_votes': report.votes})

if __name__ == '__main__':
    app.run(debug=True)
import os
import io
import base64
import qrcode
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from replit import db

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")

def init_db():
    """Initialize database with required keys if they don't exist"""
    if "workers" not in db:
        db["workers"] = {}
    if "attendance" not in db:
        db["attendance"] = {}

@app.route('/')
def index():
    """Home page with navigation options"""
    init_db()
    workers = db["workers"]
    worker_count = len(workers)
    
    # Get today's attendance count
    today = datetime.now().strftime("%Y-%m-%d")
    attendance_today = 0
    attendance_records = db["attendance"]
    
    for worker_id, records in attendance_records.items():
        if any(record['date'] == today for record in records):
            attendance_today += 1
    
    return render_template('index.html', 
                         worker_count=worker_count, 
                         attendance_today=attendance_today)

@app.route('/add_worker', methods=['GET', 'POST'])
def add_worker():
    """Add a new worker to the system"""
    init_db()
    
    if request.method == 'POST':
        matricule = request.form.get('matricule', '').strip()
        name = request.form.get('name', '').strip()
        
        if not matricule or not name:
            flash('Matricule et nom sont requis', 'error')
            return render_template('add_worker.html')
        
        workers = db["workers"]
        
        if matricule in workers:
            flash('Un ouvrier avec ce matricule existe déjà', 'error')
            return render_template('add_worker.html')
        
        # Add worker to database
        workers[matricule] = {
            'name': name,
            'matricule': matricule,
            'created_at': datetime.now().isoformat()
        }
        db["workers"] = workers
        
        flash(f'Ouvrier {name} ajouté avec succès', 'success')
        return redirect(url_for('worker_qr', matricule=matricule))
    
    return render_template('add_worker.html')

@app.route('/view_workers')
def view_workers():
    """View all workers in the system"""
    init_db()
    workers = db["workers"]
    return render_template('view_workers.html', workers=workers)

@app.route('/worker_qr/<matricule>')
def worker_qr(matricule):
    """Generate and display QR code for a worker"""
    init_db()
    workers = db["workers"]
    
    if matricule not in workers:
        flash('Ouvrier non trouvé', 'error')
        return redirect(url_for('view_workers'))
    
    worker = workers[matricule]
    
    # Generate QR code
    presence_url = request.url_root + f"presence/{matricule}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(presence_url)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for embedding in HTML
    img_buffer = io.BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    qr_code_b64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return render_template('worker_qr.html', 
                         worker=worker, 
                         qr_code=qr_code_b64,
                         presence_url=presence_url)

@app.route('/presence/<matricule>')
def mark_presence(matricule):
    """Mark worker presence when QR code is scanned"""
    init_db()
    workers = db["workers"]
    
    if matricule not in workers:
        return render_template('presence_confirmation.html', 
                             success=False, 
                             message="Matricule non trouvé dans le système")
    
    worker = workers[matricule]
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    # Get attendance records
    attendance = db["attendance"]
    
    # Initialize worker attendance if doesn't exist
    if matricule not in attendance:
        attendance[matricule] = []
    
    # Check if already marked today
    worker_attendance = attendance[matricule]
    already_marked_today = any(record['date'] == date_str for record in worker_attendance)
    
    if already_marked_today:
        return render_template('presence_confirmation.html',
                             success=False,
                             worker=worker,
                             message=f"Présence déjà enregistrée pour aujourd'hui")
    
    # Record attendance
    attendance_record = {
        'date': date_str,
        'time': time_str,
        'timestamp': now.isoformat(),
        'worker_name': worker['name']
    }
    
    worker_attendance.append(attendance_record)
    attendance[matricule] = worker_attendance
    db["attendance"] = attendance
    
    return render_template('presence_confirmation.html',
                         success=True,
                         worker=worker,
                         time=time_str,
                         date=date_str,
                         message="Présence enregistrée avec succès!")

@app.route('/attendance_log')
def attendance_log():
    """View attendance log for all workers"""
    init_db()
    workers = db["workers"]
    attendance = db["attendance"]
    
    # Get date filter from query params
    date_filter = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # Prepare attendance data for the specified date
    attendance_data = []
    
    for matricule, worker in workers.items():
        worker_records = attendance.get(matricule, [])
        # Find record for the specified date
        day_record = next((record for record in worker_records if record['date'] == date_filter), None)
        
        attendance_data.append({
            'matricule': matricule,
            'name': worker['name'],
            'present': day_record is not None,
            'time': day_record['time'] if day_record else None
        })
    
    # Sort by name
    attendance_data.sort(key=lambda x: x['name'])
    
    return render_template('attendance_log.html', 
                         attendance_data=attendance_data,
                         selected_date=date_filter,
                         total_workers=len(workers),
                         present_count=sum(1 for record in attendance_data if record['present']))

@app.route('/delete_worker/<matricule>')
def delete_worker(matricule):
    """Delete a worker from the system"""
    init_db()
    workers = db["workers"]
    attendance = db["attendance"]
    
    if matricule in workers:
        # Remove worker
        del workers[matricule]
        db["workers"] = workers
        
        # Remove attendance records
        if matricule in attendance:
            del attendance[matricule]
            db["attendance"] = attendance
        
        flash('Ouvrier supprimé avec succès', 'success')
    else:
        flash('Ouvrier non trouvé', 'error')
    
    return redirect(url_for('view_workers'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

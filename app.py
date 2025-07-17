from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import CameraDatabase
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Initialize database
db = CameraDatabase()

@app.route('/')
def index():
    """Main page - shows all cameras"""
    cameras = db.get_all_cameras()
    return render_template('index.html', cameras=cameras, search_query='')

@app.route('/api/search')
def api_search():
    """API endpoint for live search"""
    query = request.args.get('q', '').strip()
    
    if query:
        cameras = db.search_cameras(query)
    else:
        cameras = db.get_all_cameras()
    
    return jsonify({
        'cameras': cameras,
        'count': len(cameras),
        'query': query
    })

@app.route('/add', methods=['POST'])
def add_camera():
    """Add a new camera"""
    name = request.form.get('name', '').strip()
    link = request.form.get('link', '').strip()
    
    # Validation
    if not name:
        flash('Camera name is required', 'error')
        return redirect(url_for('index'))
    
    if not link:
        flash('Camera link is required', 'error')
        return redirect(url_for('index'))
    
    try:
        camera_id = db.add_camera(name, link)
        flash(f'Camera "{name}" added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding camera: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/update/<int:camera_id>', methods=['POST'])
def update_camera(camera_id):
    """Update an existing camera"""
    name = request.form.get('name', '').strip()
    link = request.form.get('link', '').strip()
    
    # Validation
    if not name:
        flash('Camera name is required', 'error')
        return redirect(url_for('index'))
    
    if not link:
        flash('Camera link is required', 'error')
        return redirect(url_for('index'))
    
    try:
        if db.update_camera(camera_id, name, link):
            flash(f'Camera "{name}" updated successfully!', 'success')
        else:
            flash('Camera not found', 'error')
    except Exception as e:
        flash(f'Error updating camera: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/delete/<int:camera_id>', methods=['POST'])
def delete_camera(camera_id):
    """Delete a camera"""
    try:
        # Get camera name for the flash message
        camera = db.get_camera_by_id(camera_id)
        if camera and db.delete_camera(camera_id):
            flash(f'Camera "{camera["name"]}" deleted successfully!', 'success')
        else:
            flash('Camera not found', 'error')
    except Exception as e:
        flash(f'Error deleting camera: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/get_camera/<int:camera_id>')
def get_camera(camera_id):
    """API endpoint to get camera data for editing"""
    camera = db.get_camera_by_id(camera_id)
    if camera:
        return jsonify(camera)
    return jsonify({'error': 'Camera not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
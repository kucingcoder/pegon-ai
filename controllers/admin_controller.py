from datetime import datetime, timezone
import hashlib
import os
from flask import Blueprint, flash, redirect, render_template, request, session
from models.admin import Admin
from models.tutorial import Tutorial
from utils import to_webp

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/internal', methods=['GET', 'POST'])
def login_admin():
    if 'admin' in session:
        return redirect('/manage-tutorials')
    
    if request.method == 'POST':
        uname = request.form['username']
        passwd = hash_password(request.form['password'])
        user = Admin.objects(username=uname, password=passwd).first()
        if user:
            session['admin'] = str(user.id)
            return redirect('/manage-tutorials')
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@admin_bp.route('/logout', methods=['GET'])
def logout():
    session.pop('admin', None)
    return redirect('/')

@admin_bp.route('/manage-tutorials', methods=['GET'])
def manage_tutorials():
    if 'admin' not in session:
        return redirect('/internal')
    
    user = Admin.objects(id=session['admin']).first()
    if not user:
        return redirect('/internal')
    
    tutorials = Tutorial.objects().order_by('-created_at')
    return render_template('manage-tutorials.html', tutorials=tutorials)

@admin_bp.route('/add-tutorial', methods=['POST'])
def add_tutorials():
    if 'admin' not in session:
        return redirect('/internal')
    
    user = Admin.objects(id=session['admin']).first()
    if not user:
        return redirect('/internal')
    
    required_fields = ['name', 'description', 'link']
    data = request.form

    for field in required_fields:
        if field not in data or data[field].strip() == '':
            flash('Field ' + field + ' can\'t be empty', 'error')
        
    name = data['name'].title()
    description = data['description']
    link = data['link']

    if Tutorial.objects(name=name).first():
        flash('Tutorial name already exists', 'error')
        return redirect(request.referrer)

    if len(name) > 64:
        flash('Tutorial name too long', 'error')
        return redirect(request.referrer)
        
    if 'thumbnail' not in request.files or request.files['thumbnail'].filename == '':
        flash('Thumbnail can\'t be empty', 'error')
        return redirect(request.referrer)
    
    file = request.files['thumbnail']
    
    if not allowed_file(file.filename):
        flash('Thumbnail must be an image', 'error')
        return redirect(request.referrer)
    
    ext = file.filename.rsplit('.', 1)[1].lower()

    now_str = str(datetime.now())
    md5_hash = hashlib.md5(now_str.encode()).hexdigest()
    input_filename = f'temp-{md5_hash}.{ext}'
    input_path = os.path.join('storage/images/thumbnails', input_filename)

    file.save(input_path)

    output_filename = f'{md5_hash}.webp'
    output_path = os.path.join('storage/images/thumbnails', output_filename)

    to_webp(input_path, output_path)

    tutorial = Tutorial(
        admin_id=user.id,
        name=name,
        description=description,
        link=link,
        thumbnail=output_filename,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    tutorial.save()

    return redirect(request.referrer)

@admin_bp.route('/edit-tutorial/<id>', methods=['POST'])
def edit_tutorials(id):
    if 'admin' not in session:
        return redirect('/internal')
    
    user = Admin.objects(id=session['admin']).first()
    if not user:
        return redirect('/internal')
    
    tutorial = Tutorial.objects(id=id).first()
    if not tutorial:
        flash('Tutorial not found', 'error')
        return redirect(request.referrer)

    required_fields = ['name', 'description', 'link']
    data = request.form

    for field in required_fields:
        if field not in data or data[field].strip() == '':
            flash('Field ' + field + ' can\'t be empty', 'error')
            return redirect(request.referrer)
        
    name = data['name'].title()
    description = data['description']
    link = data['link']

    if Tutorial.objects(name=name, id__ne=id).first():
        flash('Tutorial name already exists', 'error')
        return redirect(request.referrer)

    if len(name) > 64:
        flash('Tutorial name too long', 'error')
        return redirect(request.referrer)
        
    if 'thumbnail' not in request.files or request.files['thumbnail'].filename == '':
        flash('Thumbnail can\'t be empty', 'error')
        return redirect(request.referrer)
    
    file = request.files['thumbnail']
    
    if not allowed_file(file.filename):
        flash('Thumbnail must be an image', 'error')
        return redirect(request.referrer)
        
    ext = file.filename.rsplit('.', 1)[1].lower()

    now_str = str(datetime.now())
    md5_hash = hashlib.md5(now_str.encode()).hexdigest()
    input_filename = f'temp-{md5_hash}.{ext}'
    input_path = os.path.join('storage/images/thumbnails', input_filename)

    file.save(input_path)

    output_filename = f'{md5_hash}.webp'
    output_path = os.path.join('storage/images/thumbnails', output_filename)

    to_webp(input_path, output_path)

    old_thumbnail = os.path.join('storage/images/thumbnails', tutorial.thumbnail)
    if os.path.exists(old_thumbnail):
        os.remove(old_thumbnail)

    tutorial.name = name
    tutorial.description = description
    tutorial.link = link
    tutorial.thumbnail = output_filename
    tutorial.save()

    return redirect(request.referrer)

@admin_bp.route('/delete-tutorial/<id>', methods=['POST'])
def delete_tutorials(id):
    if 'admin' not in session:
        return redirect('/internal')
    
    user = Admin.objects(id=session['admin']).first()
    if not user:
        return redirect('/internal')
    
    tutorial = Tutorial.objects(id=id).first()
    if not tutorial:
        flash('Tutorial not found', 'error')
        return redirect(request.referrer)

    thumbnail = os.path.join('storage/images/thumbnails', tutorial.thumbnail)
    if os.path.exists(thumbnail):
        os.remove(thumbnail)

    tutorial.delete()

    return redirect(request.referrer)
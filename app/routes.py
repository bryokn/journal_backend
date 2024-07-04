from flask import Blueprint, request, jsonify
from app import db
from app.models import User, JournalEntry
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return jsonify({"message": "Welcome to the Journal App API"})

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    
    return jsonify({'message': 'Invalid username or password'}), 401

@main.route('/entries', methods=['POST'])
@jwt_required()
def create_entry():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    entry = JournalEntry(
        title=data['title'],
        content=data['content'],
        category=data['category'],
        date=datetime.fromisoformat(data['date']),
        user_id=user_id
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({'message': 'Entry created successfully', 'id': entry.id}), 201

@main.route('/entries/<int:entry_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_entry(entry_id):
    user_id = get_jwt_identity()
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()

    if not entry:
        return jsonify({'message': 'Entry not found'}), 404

    if request.method == 'GET':
        return jsonify({
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'category': entry.category,
            'date': entry.date.isoformat()
        })

    elif request.method == 'PUT':
        data = request.get_json()
        entry.title = data.get('title', entry.title)
        entry.content = data.get('content', entry.content)
        entry.category = data.get('category', entry.category)
        entry.date = datetime.fromisoformat(data.get('date', entry.date.isoformat()))
        db.session.commit()
        return jsonify({'message': 'Entry updated successfully'})

    elif request.method == 'DELETE':
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Entry deleted successfully'})

@main.route('/entries', methods=['GET'])
@jwt_required()
def get_entries():
    user_id = get_jwt_identity()
    entries = JournalEntry.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': entry.id,
        'title': entry.title,
        'content': entry.content,
        'category': entry.category,
        'date': entry.date.isoformat()
    } for entry in entries])

@main.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    user_id = get_jwt_identity()
    period = request.args.get('period', 'weekly')
    
    if period == 'daily':
        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'weekly':
        start_date = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
    elif period == 'monthly':
        start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        return jsonify({'message': 'Invalid period'}), 400

    entries = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.date >= start_date
    ).all()

    summary = {
        'total_entries': len(entries),
        'categories': {}
    }

    for entry in entries:
        if entry.category not in summary['categories']:
            summary['categories'][entry.category] = 0
        summary['categories'][entry.category] += 1

    return jsonify(summary)

@main.route('/user', methods=['GET', 'PUT'])
@jwt_required()
def manage_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if request.method == 'GET':
        return jsonify({'username': user.username})

    elif request.method == 'PUT':
        data = request.get_json()
        new_username = data.get('username')
        new_password = data.get('password')

        if new_username:
            if User.query.filter_by(username=new_username).first() and new_username != user.username:
                return jsonify({'message': 'Username already exists'}), 400
            user.username = new_username

        if new_password:
            user.set_password(new_password)

        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
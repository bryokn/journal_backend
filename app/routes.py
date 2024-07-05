from flask import Blueprint, request, jsonify
from app import db, blacklist
from app.models import User, JournalEntry
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta, timezone

main = Blueprint('main', __name__)

#home route
@main.route('/')
def home():
    return jsonify({"message": "Welcome to the Journal App API"})

#User registration route
@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    #check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username already exists'}), 400

    #create new user
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

#login route
@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        #create access token if credentials are valid
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=2)
            )
        return jsonify({'access_token': access_token}), 200
    
    return jsonify({'message': 'Invalid username or password'}), 401

#new journal entry route
@main.route('/entries', methods=['POST'])
@jwt_required()
def create_entry():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    entry = JournalEntry(
        title=data['title'],
        content=data['content'],
        category=data['category'],
        date=datetime.now(timezone.utc),
        user_id=user_id
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({'message': 'Entry created successfully', 'id': entry.id}), 201

#manage (get, update, delete) a journal entry by ID route
@main.route('/entries/<int:entry_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def manage_entry(entry_id):
    user_id = get_jwt_identity()
    entry = JournalEntry.query.filter_by(id=entry_id, user_id=user_id).first()

    if not entry:
        return jsonify({'message': 'Entry not found'}), 404

    if request.method == 'GET':
        #retrieve entry
        return jsonify({
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'category': entry.category,
            'date': entry.date.isoformat()
        })

    elif request.method == 'PUT':
        #update entry
        data = request.get_json()
        entry.title = data.get('title', entry.title)
        entry.content = data.get('content', entry.content)
        entry.category = data.get('category', entry.category)
        entry.date = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({'message': 'Entry updated successfully'})

    elif request.method == 'DELETE':
        #delete entry
        db.session.delete(entry)
        db.session.commit()
        return jsonify({'message': 'Entry deleted successfully'})

#get all entries for the current user route
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

#summary route
@main.route('/summary', methods=['GET'])
@jwt_required()
def get_summary():
    #get summary of entries for a specific period
    user_id = get_jwt_identity()
    period = request.args.get('period', 'weekly')
    
    #determine start date based on period
    now = datetime.now(timezone.utc)
    if period == 'daily':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'weekly':
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'monthly':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        return jsonify({'message': 'Invalid period'}), 400
    
    #query entries for the period
    entries = JournalEntry.query.filter(
        JournalEntry.user_id == user_id,
        JournalEntry.date >= start_date
    ).all()
    
    #prepare summary
    summary = {
        'total_entries': len(entries),
        'categories': {}
    }

    for entry in entries:
        if entry.category not in summary['categories']:
            summary['categories'][entry.category] = 0
        summary['categories'][entry.category] += 1

    return jsonify(summary)

#update user route
@main.route('/user', methods=['GET', 'PUT'])
@jwt_required()
def manage_user():
    #manage user profile
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if request.method == 'GET':
        return jsonify({'username': user.username}) #get user info

    elif request.method == 'PUT': #update user info
        data = request.get_json()
        new_username = data.get('username')
        new_password = data.get('password')

        if new_username: #check if new username is already taken
            if User.query.filter_by(username=new_username).first() and new_username != user.username:
                return jsonify({'message': 'Username already exists'}), 400
            user.username = new_username

        if new_password:
            user.set_password(new_password)

        db.session.commit()
        return jsonify({'message': 'User updated successfully'})

#categories route
@main.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    user_id = get_jwt_identity()
    
    # Query all unique categories for the current user
    categories = db.session.query(JournalEntry.category)\
        .filter(JournalEntry.user_id == user_id)\
        .distinct()\
        .all()
    
    # Extract category names from the query result
    category_list = [category[0] for category in categories]
    
    return jsonify({'categories': category_list})

#logout route
@main.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()['jti']
        blacklist.add(jti)
        return jsonify({"message": "Successfully logged out"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
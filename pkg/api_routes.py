from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from pkg import app
from pkg.models import db, User, Organisation, UserOrganisation
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity





@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['first_name', 'last_name', 'email', 'password', 'phone']
    errors = []

    for field in required_fields:
        if field not in data or not data[field]:
            errors.append({"field": field, "message": f"{field} is required."})

    if errors:
        return jsonify({"errors": errors}), 422

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({
            "status": "Bad request",
            "message": "User already exists with this email",
            "statusCode": 400
        }), 400

    hashed_password = generate_password_hash(data['password'])

    user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=hashed_password,
        phone=data['phone']
    )

    db.session.add(user)
    db.session.commit()

    organisation_name = f"{data['first_name']}'s Organisation"
    organisation = Organisation(name=organisation_name)

    db.session.add(organisation)
    db.session.commit()

    user_organisation = UserOrganisation(user_id = user.user_id, org_id = organisation.org_id)

    db.session.add(user_organisation)
    db.session.commit()

    access_token = create_access_token(identity=user.user_id)
    return jsonify({
        "status": "success",
        "message": "Registration successful",
        "data": {
            "accessToken": access_token,
            "user": {
                "userId": user.user_id,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "phone": user.phone
            }
        }
    }), 201



@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({
            "status": "Bad request",
            "message": "Email and password are required",
            "statusCode": 400
        }), 400

    
    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({
            "status": "Bad request",
            "message": "Invalid email or password",
            "statusCode": 401
        }), 401

    
    access_token = create_access_token(identity=user.user_id)
    return jsonify({
        "status": "success",
        "message": "Login successful",
        "data": {
            "accessToken": access_token,
            "user": {
                "userId": user.user_id,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "phone": user.phone
            }
        }
    }), 200



@app.route('/api/organisations', methods=['POST'])
@jwt_required()
def create_organisation():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    if 'name' not in data or not data['name']:
        return jsonify({"errors": [{"field": "name", "message": "Name is required."}]}), 422

    organisation = Organisation(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(organisation)
    db.session.commit()

    user_organisation = UserOrganisation(user_id=current_user_id, org_id=organisation.org_id)
    
    db.session.add(user_organisation)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Organisation created successfully",
        "data": {
            "orgId": organisation.org_id,
            "name": organisation.name,
            "description": organisation.description
        }
    }), 201




@app.route('/api/organisations/<org_id>/users', methods=['POST'])
@jwt_required()
def add_user_to_organisation(org_id):
    data = request.get_json()
    current_user_id = get_jwt_identity()
    user_to_add_id = data.get('user_id')

    if not user_to_add_id:
        return jsonify({"errors": [{"field": "user_id", "message": "User ID is required."}]}), 422

    organisation = Organisation.query.filter_by(org_id=org_id).first()
    if not organisation:
        return jsonify({"status": "error", "message": "Organisation not found", "statusCode": 404}), 404

    user_to_add = User.query.filter_by(user_id=user_to_add_id).first()
    if not user_to_add:
        return jsonify({"status": "error", "message": "User not found", "statusCode": 404}), 404

    user_organisation = UserOrganisation(user_id=user_to_add_id, org_id=org_id)
    db.session.add(user_organisation)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User added to organisation successfully"
    }), 200
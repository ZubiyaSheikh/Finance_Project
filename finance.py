from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Zubiya Tabassum/OneDrive/Desktop/databases/finance.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)   # 'admin' or 'user'
    status = db.Column(db.String(20), nullable=False)

# Records model
class Records(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.String(200), nullable=True)

def access(user_id, action="read"):
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}, 404

    if user.status != "active":
        return {"error": "User is inactive"}, 403

    if user.role == "viewer":
        if action not in ["read"]:
            return {"error": "Access denied. Viewer can only read."}, 403

    elif user.role == "analyst":
        if action not in ["read", "summary"]:
            return {"error": "Access denied. Analyst can only read and view summaries."}, 403

    elif user.role == "admin":
        return None  # Full access

    else:
        return {"error": "Invalid role"}, 403

    return None

# User CRUD with access control
@app.route('/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Access control: only admin can create users
        access_control = access(data.get("user_id"), action="create")
        if access_control:
            return jsonify(access_control[0]), access_control[1]

        required_fields = ['name', 'email', 'role', 'status']
        if not all(key in data for key in required_fields):
            return jsonify({"error": "Missing required fields: name, email, role, status"}), 400

        if not isinstance(data['name'], str) or not data['name'].strip():
            return jsonify({"error": "Name must be a non-empty string"}), 400

        if not isinstance(data['email'], str) or '@' not in data['email']:
            return jsonify({"error": "Invalid email format"}), 400

        if data['role'] not in ['viewer', 'analyst', 'admin']:
            return jsonify({"error": "Role must be one of: viewer, analyst, admin"}), 400

        if data['status'] not in ['active', 'inactive']:
            return jsonify({"error": "Status must be one of: active, inactive"}), 400

        user = User(
            name=data['name'],
            email=data['email'],
            role=data['role'],
            status=data['status']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User created successfully", "id": user.id}), 201

    elif request.method == 'GET':
        user_id_str = request.args.get('id')
        if not user_id_str or not user_id_str.isdigit():
            return jsonify({"error": "Valid user id (integer) is required"}), 400
        user_id = int(user_id_str)

        # Access control: all roles can read user info
        access_control = access(user_id, action="read")
        if access_control:
            return jsonify(access_control[0]), access_control[1]

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "status": user.status
        })

    elif request.method == 'PUT':
        data = request.get_json()
        if not data or 'id' not in data or not isinstance(data['id'], int):
            return jsonify({"error": "Valid id (integer) is required"}), 400

        # Access control: only admin can update users
        access_control = access(data.get("user_id"), action="update")
        if access_control:
            return jsonify(access_control[0]), access_control[1]

        user = User.query.get(data['id'])
        if not user:
            return jsonify({"error": "User not found"}), 404

        if 'name' in data:
            if not isinstance(data['name'], str) or not data['name'].strip():
                return jsonify({"error": "Name must be a non-empty string"}), 400
            user.name = data['name']
        if 'email' in data:
            if not isinstance(data['email'], str) or '@' not in data['email']:
                return jsonify({"error": "Invalid email format"}), 400
            user.email = data['email']
        if 'role' in data:
            if data['role'] not in ['viewer', 'analyst', 'admin']:
                return jsonify({"error": "Role must be one of: viewer, analyst, admin"}), 400
            user.role = data['role']
        if 'status' in data:
            if data['status'] not in ['active', 'inactive']:
                return jsonify({"error": "Status must be one of: active, inactive"}), 400
            user.status = data['status']
        db.session.commit()
        return jsonify({"message": "User data updated successfully"})

    elif request.method == 'DELETE':
        data = request.get_json()
        if not data or 'id' not in data or not isinstance(data['id'], int):
            return jsonify({"error": "Valid id (integer) is required"}), 400

        # Access control: only admin can delete users
        access_control = access(data.get("user_id"), action="delete")
        if access_control:
            return jsonify(access_control[0]), access_control[1]

        user = User.query.get(data['id'])
        if not user:
            return jsonify({"error": "User not found"}), 404
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User data deleted successfully"})

@app.route('/filter_records', methods=['GET'])
def filter_records():
    category = request.args.get('category')
    type_param = request.args.get('type')
    date = request.args.get('date')

    if type_param and type_param not in ['income', 'expense']:
        return jsonify({"error": "type must be 'income' or 'expense'"}), 400

    query = Records.query

    if category:
        query = query.filter(Records.category == category)
    if type_param:
        query = query.filter(Records.type == type_param)
    if date:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d")
            query = query.filter(Records.date == parsed_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    result_ofRecords = query.all()

    return jsonify([{
        "id": record.id,
        "user_id": record.user_id,
        "amount": record.amount,
        "type": record.type,
        "category": record.category,
        "date": record.date.strftime("%Y-%m-%d"),
        "description": record.description
    } for record in result_ofRecords])



# Dashboard route with access control
@app.route('/dashboard', methods=['GET'])
def dashboard():
    user_id_str = request.args.get('user_id')
    if not user_id_str or not user_id_str.isdigit():
        return jsonify({"error": "Valid user id (integer) is required"}), 400
    user_id = int(user_id_str)

    # Access control: only analyst and admin can view dashboard
    access_control = access(user_id, action="summary")
    if access_control:
        return jsonify(access_control[0]), access_control[1]

    total_income = db.session.query(db.func.sum(Records.amount)).filter(Records.type == 'income').scalar() or 0
    total_expense = db.session.query(db.func.sum(Records.amount)).filter(Records.type == 'expense').scalar() or 0
    net_balance = total_income - total_expense

    category_totals = db.session.query(
        Records.category,
        db.func.sum(Records.amount).label('total')
    ).group_by(Records.category).all()
    category_summary = [{"category": cat, "total": total} for cat, total in category_totals]

    recent_activity = db.session.query(Records).order_by(Records.date.desc()).limit(5).all()
    recent_data = [{
        "id": r.id,
        "user_id": r.user_id,
        "amount": r.amount,
        "type": r.type,
        "category": r.category,
        "date": r.date.strftime("%Y-%m-%d"),
        "description": r.description
    } for r in recent_activity]
# Monthly trends
    monthly_trends = db.session.query(
        db.func.strftime('%Y-%m', Records.date).label('month'),
        Records.type,
        db.func.sum(Records.amount).label('total')
    ).group_by(db.func.strftime('%Y-%m', Records.date), Records.type).all()
    trends_data = [{"month": month, "type": type, "total": total} for month, type, total in monthly_trends]

    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance,
        "category_wise_totals": category_summary,
        "recent_activity": recent_data,
        "monthly_trends": trends_data
    })

# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)




from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, db


def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "change-me-in-production"

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json() or {}
        nome = (data.get("nome") or "").strip()
        email = (data.get("email") or "").strip().lower()
        senha = data.get("senha") or ""

        if not nome or not email or not senha:
            return jsonify({"error": "nome, email e senha são obrigatórios"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "email já cadastrado"}), 400

        hashed_password = generate_password_hash(senha)
        user = User(nome=nome, email=email, senha=hashed_password)
        db.session.add(user)
        db.session.commit()

        return (
            jsonify({"message": "cadastro realizado", "user": user.to_dict()}),
            201,
        )

    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        email = (data.get("email") or "").strip().lower()
        senha = data.get("senha") or ""

        if not email or not senha:
            return jsonify({"error": "email e senha são obrigatórios"}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.senha, senha):
            return jsonify({"error": "credenciais inválidas"}), 401

        return jsonify({"message": "login realizado", "user": user.to_dict()}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

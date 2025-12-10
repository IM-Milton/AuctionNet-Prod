# app.py
from flask import Flask, request, send_from_directory, jsonify, render_template_string
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timezone
from dateutil.parser import isoparse
from werkzeug.utils import secure_filename
from zoneinfo import ZoneInfo
from pathlib import Path
import os

from services.repo import YamlRepo, ensure_default_data
from services.auth import hash_password, check_password, ensure_user_uniqueness
from services.auctions import (
    list_auctions, get_auction, create_auction, place_bid,
    open_auction_if_due, close_auction_if_due, product_is_owned_by
)
from models.schemas import RegisterSchema, LoginSchema, ProductSchema, AuctionCreateSchema, BidSchema

# ------------------- Configs globales -------------------
APP_TZ = os.environ.get("APP_TZ", "Europe/Paris")
LOCAL_TZ = ZoneInfo(APP_TZ)

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp"}

MEDIA_ROOT = Path(
    os.environ.get("MEDIA_ROOT", str((Path(__file__).parent / "local_data" / "media")))
).resolve()
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", 10))

DOCS_DIR = Path(__file__).parent / "docs"

def to_utc(dt):
    """Interprète un datetime sans TZ comme Europe/Paris, puis convertit en UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=LOCAL_TZ)
    return dt.astimezone(timezone.utc)

# ------------------- Factory -------------------
def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=False, resources={r"/*": {"origins": "*"}})

    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET", "change_me")
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024
    jwt = JWTManager(app)
    
    # Initialiser SocketIO avec threading (compatible Python 3.13)
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        async_mode='threading',
        logger=True,
        engineio_logger=True
    )

    repo = YamlRepo()
    ensure_default_data(repo)

    # ---------- Backfill / recalage des enchères au démarrage ----------
    def ensure_auction_defaults():
        doc = repo.load("auctions")
        items = doc.get("auctions", [])
        changed = False
        now_utc = datetime.now(LOCAL_TZ).astimezone(timezone.utc)

        for a in items:
            a.setdefault("min_increment", 50)
            a.setdefault("current_price", a.get("start_price", 0))
            a.setdefault("current_bid_id", None)
            try:
                s = to_utc(isoparse(a["start_at"]))
                e = to_utc(isoparse(a["end_at"]))
            except Exception:
                a.setdefault("status", "scheduled")
                continue

            if now_utc < s:
                new_status = "scheduled"
            elif s <= now_utc < e:
                new_status = "running"
            else:
                new_status = "closed"

            if a.get("status") != new_status:
                a["status"] = new_status
                changed = True

        if changed:
            repo.save("auctions", {"auctions": items})

    ensure_auction_defaults()

    # ---------- Scheduler ----------
    scheduler = BackgroundScheduler()
    scheduler.start()

    def schedule_jobs_for_all():
        auctions = repo.load("auctions").get("auctions", [])
        now_utc = datetime.now(LOCAL_TZ).astimezone(timezone.utc)

        for a in auctions:
            try:
                s = to_utc(isoparse(a["start_at"]))
                e = to_utc(isoparse(a["end_at"]))
                status = a.get("status", "scheduled")

                # Rattrapage immédiat si l'instance a raté une fenêtre
                if now_utc >= e and status != "closed":
                    close_auction_if_due(repo, a["id"])
                    continue
                if s <= now_utc < e and status == "scheduled":
                    open_auction_if_due(repo, a["id"])
                    status = "running"

                # Planification futur
                if s > now_utc:
                    scheduler.add_job(lambda aid=a["id"]: open_auction_if_due(repo, aid),
                                      DateTrigger(run_date=s))
                if e > now_utc:
                    scheduler.add_job(lambda aid=a["id"]: close_auction_if_due(repo, aid),
                                      DateTrigger(run_date=e))
            except Exception:
                continue

    schedule_jobs_for_all()

    # ------------------- Routes -------------------
    @app.get('/api/health')
    def health():
        return {"status": "ok"}

    @app.get('/media/<pid>/<path:filename>')
    def serve_media(pid, filename):
        dirpath = os.path.join(str(MEDIA_ROOT), pid)
        return send_from_directory(directory=dirpath, path=filename, as_attachment=False, max_age=3600)

    # --- Auth ---
    @app.post('/api/auth/register')
    def register():
        data = request.get_json() or {}
        payload = RegisterSchema(**data)
        users = repo.load("users")
        ensure_user_uniqueness(users, payload.email)
        new_id = repo.next_id(users, "users", prefix="u_")
        # Extraire username de l'email (partie avant le @)
        username = payload.email.split('@')[0]
        users.setdefault("users", []).append({
            "id": new_id,
            "email": payload.email,
            "username": username,
            "password_hash": hash_password(payload.password),
            "balance": 100000.0,
            "held": 0.0,
            "purchases": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        repo.save("users", users)
        return {"id": new_id, "email": payload.email, "balance": 100000.0}, 201

    @app.post('/api/auth/login')
    def login():
        data = request.get_json() or {}
        payload = LoginSchema(**data)
        users = repo.load("users").get("users", [])
        user = next((u for u in users if u["email"] == payload.email), None)
        if not user or not check_password(payload.password, user["password_hash"]):
            return {"error": "Invalid credentials"}, 401
        token = create_access_token(identity=user["id"])
        return {"access_token": token}

    @app.get('/api/me')
    @jwt_required()
    def me():
        uid = get_jwt_identity()
        users = repo.load("users").get("users", [])
        user = next(u for u in users if u["id"] == uid)
        return {
            "id": user["id"],
            "email": user["email"],
            "balance": user.get("balance", 0.0),
            "held": user.get("held", 0.0),
            "purchases": user.get("purchases", [])
        }

    @app.post('/api/me/credit')
    @jwt_required()
    def credit_account():
        uid = get_jwt_identity()
        data = request.get_json() or {}
        
        # Valider le montant
        amount = data.get('amount', 0)
        if not isinstance(amount, (int, float)) or amount <= 0:
            return {"error": "Le montant doit être un nombre positif"}, 400
        
        if amount > 10000:
            return {"error": "Le montant maximum par crédit est de 10 000 €"}, 400
        
        # Charger les utilisateurs
        users_doc = repo.load("users")
        users = users_doc.get("users", [])
        user = next(u for u in users if u["id"] == uid)
        
        # Ajouter le montant au solde
        current_balance = user.get("balance", 0.0)
        new_balance = float(current_balance) + float(amount)
        user["balance"] = new_balance
        
        # Sauvegarder
        repo.save("users", users_doc)
        
        return {
            "success": True,
            "previous_balance": current_balance,
            "amount_credited": amount,
            "new_balance": new_balance
        }, 200

    # --- Catégories ---
    @app.get('/api/categories')
    def categories():
        return repo.load("categories")

    # --- Produits ---
    @app.post('/api/products')
    @jwt_required()
    def create_product():
        uid = get_jwt_identity()
        data = request.get_json() or {}
        payload = ProductSchema(**data)
        products = repo.load("products")
        new_id = repo.next_id(products, "products", prefix="p_")
        products.setdefault("products", []).append({
            "id": new_id,
            "owner_id": uid,
            "title": payload.title,
            "description": payload.description,
            "category": payload.category,
            "condition": payload.condition,
            "images": payload.images,
        })
        repo.save("products", products)
        return {"id": new_id}, 201

    @app.post('/api/products/<pid>/images')
    @jwt_required()
    def upload_product_image(pid):
        uid = get_jwt_identity()
        products_doc = repo.load("products")
        prod = next((p for p in products_doc.get("products", []) if p["id"] == pid), None)
        if not prod:
            return {"error": "Product not found"}, 404
        if prod.get("owner_id") != uid:
            return {"error": "You do not own this product"}, 403

        if 'file' not in request.files:
            return {"error": "Missing file"}, 400
        file = request.files['file']
        if file.filename == '':
            return {"error": "Empty filename"}, 400

        mime = file.mimetype or ''
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTS or mime not in ALLOWED_IMAGE_MIMES:
            return {"error": "Unsupported file type"}, 400

        safe_name = secure_filename(file.filename)
        target_dir = os.path.join(str(MEDIA_ROOT), pid)
        os.makedirs(target_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        stored_name = f"{ts}_{safe_name}"
        abs_path = os.path.join(target_dir, stored_name)
        file.save(abs_path)

        rel_path = f"media/{pid}/{stored_name}"
        prod.setdefault('images', []).append(rel_path)
        repo.save('products', products_doc)
        return {"path": rel_path}, 201

    # --- Enchères ---
    @app.get('/api/auctions')
    def get_auctions():
        status = request.args.get('status')
        category = request.args.get('category')
        condition = request.args.get('condition')
        q = request.args.get('search')
        return list_auctions(repo, status=status, category=category, condition=condition, search=q)

    @app.get('/api/auctions/<aid>')
    def get_auction_by_id(aid):
        result = get_auction(repo, aid)
        if not result:
            return {"error": "Not found"}, 404
        return result

    @app.post('/api/auctions')
    @jwt_required()
    def post_auction():
        uid = get_jwt_identity()
        data = request.get_json() or {}
        payload = AuctionCreateSchema(**data)

        if not product_is_owned_by(repo, payload.product_id, uid):
            return {"error": "You do not own this product"}, 403

        # 1) Construire l'heure locale Paris (ce qu'on veut VOIR et SAUVER)
        try:
            s_in = isoparse(payload.start_at)
            e_in = isoparse(payload.end_at)
        except Exception:
            return {"error": "Invalid datetime format. Use ISO-8601."}, 400

        # s_local/e_local = heure Europe/Paris avec offset
        s_local = (s_in.replace(tzinfo=LOCAL_TZ) if s_in.tzinfo is None else s_in.astimezone(LOCAL_TZ))
        e_local = (e_in.replace(tzinfo=LOCAL_TZ) if e_in.tzinfo is None else e_in.astimezone(LOCAL_TZ))

        # 2) Logique interne en UTC (pour vérifier ordre et scheduler)
        s_utc = s_local.astimezone(timezone.utc)
        e_utc = e_local.astimezone(timezone.utc)
        if e_utc <= s_utc:
            return {"error": "end_at must be after start_at"}, 400

        # 3) On SAUVE ce qu'on veut VOIR : l'heure locale Paris (avec offset)
        normalized = AuctionCreateSchema(
            product_id=payload.product_id,
            start_price=payload.start_price,
            min_increment=getattr(payload, "min_increment", 50),
            start_at=s_local.isoformat(),   # ← SAUVE LOCAL
            end_at=e_local.isoformat(),     # ← SAUVE LOCAL
        )

        out = create_auction(repo, normalized)  # ne doit PAS reconvertir

        # Recalage + (re)planification
        ensure_auction_defaults()
        schedule_jobs_for_all()
        return out, 201



    @app.get('/api/auctions/<aid>/bids')
    def get_auction_bids(aid):
        """Récupère l'historique de toutes les enchères pour une enchère spécifique"""
        bids_doc = repo.load("bids")
        users_doc = repo.load("users")
        
        bids = bids_doc.get("bids", [])
        users = users_doc.get("users", [])
        user_map = {u["id"]: u for u in users}
        
        # Filtrer les bids pour cette enchère et ajouter les infos utilisateur
        auction_bids = []
        for b in bids:
            if b.get("auction_id") == aid:
                user = user_map.get(b.get("user_id"), {})
                # Le champ est 'placed_at' dans le YAML, pas 'timestamp'
                placed_at = b.get("placed_at", "")
                # Extraire username de l'email si le champ username n'existe pas
                email = user.get("email", "")
                username = user.get("username", email.split('@')[0] if email else "Inconnu")
                auction_bids.append({
                    "id": b.get("id"),
                    "amount": b.get("amount"),
                    "timestamp": placed_at,  # Renommer pour l'API frontend
                    "user": {
                        "id": user.get("id"),
                        "username": username
                    }
                })
        
        # Trier par timestamp décroissant (plus récent en premier)
        auction_bids.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {"bids": auction_bids}

    @app.post('/api/auctions/<aid>/bids')
    @jwt_required()
    def post_bid(aid):
        uid = get_jwt_identity()
        data = request.get_json() or {}
        payload = BidSchema(**data)
        try:
            res = place_bid(repo, aid, uid, payload.amount)
            
            # Émettre l'événement WebSocket pour tous les clients dans cette enchère
            auction_data = get_auction(repo, aid)
            room_name = f'auction_{aid}'
            
            print('\n' + '='*60)
            print(f'📢 WEBSOCKET: Émission bid_placed vers la room: {room_name}')
            print(f'💰 Prix actuel: {res["current_price"]} €')
            print(f'🆔 Enchère ID: {aid}')
            print('='*60 + '\n')
            
            socketio.emit('bid_placed', {
                'auction_id': aid,
                'current_price': res['current_price'],
                'bid_id': res['bid_id'],
                'auction': auction_data
            }, room=room_name)
            
            return res, 201
        except ValueError as e:
            return {"error": str(e)}, 400

    # --- Achats ---
    @app.get('/api/my/purchases')
    @jwt_required()
    def my_purchases():
        uid = get_jwt_identity()
        users = repo.load("users").get("users", [])
        products = repo.load("products").get("products", [])
        user = next(u for u in users if u["id"] == uid)
        ids = set(user.get("purchases", []))
        return {"products": [p for p in products if p["id"] in ids]}

    # --- Docs Swagger ---
    @app.get("/openapi.yaml")
    def get_openapi():
        return send_from_directory(DOCS_DIR, "openapi.yaml", mimetype="text/yaml")

    SWAGGER_UI = """
    <!doctype html><html><head>
      <meta charset="utf-8"/><title>API Docs</title>
      <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
    </head><body>
      <div id="swagger"></div>
      <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
      <script>window.ui = SwaggerUIBundle({ url: '/openapi.yaml', dom_id: '#swagger' });</script>
    </body></html>
    """

    @app.get("/docs")
    def docs():
        return render_template_string(SWAGGER_UI)

    # ------------------- WebSocket Events -------------------
    @socketio.on('connect')
    def handle_connect():
        print('\n' + '='*60)
        print(f'✅ WEBSOCKET: Client connecté - SID: {request.sid}')
        print('='*60 + '\n')
        emit('connected', {'message': 'Connected to auction server'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('\n' + '='*60)
        print(f'❌ WEBSOCKET: Client déconnecté - SID: {request.sid}')
        print('='*60 + '\n')

    @socketio.on('join_auction')
    def handle_join_auction(data):
        auction_id = data.get('auction_id')
        if auction_id:
            room_name = f'auction_{auction_id}'
            join_room(room_name)
            print('\n' + '='*60)
            print(f'🛋️ WEBSOCKET: Client {request.sid} a rejoint la room: {room_name}')
            print('='*60 + '\n')
            emit('joined_auction', {'auction_id': auction_id})

    @socketio.on('leave_auction')
    def handle_leave_auction(data):
        auction_id = data.get('auction_id')
        if auction_id:
            room_name = f'auction_{auction_id}'
            leave_room(room_name)
            print('\n' + '='*60)
            print(f'🚪 WEBSOCKET: Client {request.sid} a quitté la room: {room_name}')
            print('='*60 + '\n')

    return app, socketio

# ------------------- Entrypoint -------------------
import os
from pathlib import Path

if __name__ == '__main__':
    # Dossiers par défaut si besoin (pas d'export nécessaire)
    (Path(__file__).parent / "local_data" / "db").mkdir(parents=True, exist_ok=True)
    (Path(__file__).parent / "local_data" / "media").mkdir(parents=True, exist_ok=True)

    app, socketio = create_app()
<<<<<<< HEAD

    port = int(os.environ.get("PORT", 5000))

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False,                   # en prod -> False
        allow_unsafe_werkzeug=True     # IMPORTANT pour Docker / Railway
    )
=======
    # Note: debug=True avec gevent peut causer des problèmes avec le reloader
    # Utiliser use_reloader=False pour éviter l'erreur WERKZEUG_SERVER_FD
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
>>>>>>> develop

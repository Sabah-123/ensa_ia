"""
ENSA Béni Mellal — Système IA Responsable
Conforme RGPD / Loi 09-08 / Éthique IA
Auteur : Filière IA & Cybersécurité
"""
from dotenv import load_dotenv
load_dotenv()
import os
import json
import logging
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, g, Response
)
from werkzeug.security import generate_password_hash, check_password_hash

from database import init_db, get_db
from ai_service import generate_response
from compliance import check_compliance

# ─── Configuration ────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=2)

# ─── Journalisation ───────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("audit.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ensa_ia")


def audit(action, user=None, detail=""):
    uid = user or session.get("user_id", "anonyme")
    ip  = request.remote_addr or "inconnu"
    logger.info(f"ACTION={action} | USER={uid} | IP={ip} | DETAIL={detail}")


# ─── Décorateurs ──────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Veuillez vous connecter.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Accès réservé aux administrateurs.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


def rate_limit(max_per_hour=30):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            uid = session.get("user_id")
            if uid:
                db = get_db()
                one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
                count = db.execute(
                    "SELECT COUNT(*) FROM requests WHERE user_id=? AND created_at>?",
                    (uid, one_hour_ago)
                ).fetchone()[0]
                if count >= max_per_hour:
                    audit("RATE_LIMIT", detail=f"Limite {max_per_hour}/h atteinte")
                    flash(f"Limite de {max_per_hour} requêtes/heure atteinte.", "danger")
                    return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorated
    return decorator


# ─── Authentification ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Identifiant et mot de passe requis.", "danger")
            return render_template("login.html")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            if user["is_blocked"]:
                audit("LOGIN_BLOCKED", detail=f"Username={username}")
                flash("Votre compte est suspendu. Contactez l'administrateur.", "danger")
                return render_template("login.html")
            session.permanent = True
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            session["role"]     = user["role"]
            audit("LOGIN_SUCCESS", user=user["id"])
            flash(f"Bienvenue, {user['username']} !", "success")
            return redirect(url_for("dashboard"))
        else:
            audit("LOGIN_FAILED", detail=f"Username={username}")
            flash("Identifiant ou mot de passe incorrect.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    audit("LOGOUT")
    session.clear()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        role     = request.form.get("role", "etudiant")
        if not username or len(username) < 3:
            flash("L'identifiant doit contenir au moins 3 caractères.", "danger")
            return render_template("register.html")
        if len(password) < 8:
            flash("Le mot de passe doit contenir au moins 8 caractères.", "danger")
            return render_template("register.html")
        if role not in ("etudiant", "personnel"):
            role = "etudiant"
        db = get_db()
        if db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
            flash("Cet identifiant est déjà utilisé.", "danger")
            return render_template("register.html")
        db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?,?,?)",
            (username, generate_password_hash(password), role)
        )
        db.commit()
        audit("REGISTER", detail=f"Username={username} Role={role}")
        flash("Compte créé avec succès. Veuillez vous connecter.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


# ─── Dashboard ────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    recent = db.execute(
        """SELECT id, prompt_preview, response_preview, created_at, is_flagged
           FROM requests WHERE user_id=? ORDER BY created_at DESC LIMIT 5""",
        (session["user_id"],)
    ).fetchall()
    total = db.execute(
        "SELECT COUNT(*) FROM requests WHERE user_id=?", (session["user_id"],)
    ).fetchone()[0]
    return render_template("dashboard.html", recent=recent, total=total)


# ─── Requêtes IA ──────────────────────────────────────────────────────────────

@app.route("/ask", methods=["GET", "POST"])
@login_required
@rate_limit(max_per_hour=30)
def ask():
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            flash("Veuillez saisir une question.", "warning")
            return render_template("ask.html")
        if len(prompt) > 2000:
            flash("La question ne peut pas dépasser 2000 caractères.", "danger")
            return render_template("ask.html")

        compliance_result = check_compliance(prompt)
        if compliance_result["blocked"]:
            audit("COMPLIANCE_BLOCK", detail=f"Raison: {compliance_result['reason']}")
            flash(f"Saisie refusée : {compliance_result['reason']}", "danger")
            return render_template("ask.html", prompt=prompt)

        response_text, model_used = generate_response(prompt)
        prompt_preview   = (prompt[:120] + "...") if len(prompt) > 120 else prompt
        response_preview = (response_text[:200] + "...") if len(response_text) > 200 else response_text

        db = get_db()
        db.execute(
            """INSERT INTO requests
               (user_id, prompt_preview, prompt_full, response_preview,
                response_full, model_used, is_flagged, flag_reason)
               VALUES (?,?,?,?,?,?,?,?)""",
            (session["user_id"], prompt_preview, prompt,
             response_preview, response_text, model_used,
             1 if compliance_result.get("warned") else 0,
             compliance_result.get("warning", ""))
        )
        db.commit()
        audit("ASK", detail=f"Model={model_used} Flagged={compliance_result.get('warned', False)}")
        return render_template("ask.html", prompt=prompt, response=response_text,
                               model_used=model_used,
                               warned=compliance_result.get("warned"),
                               warning_msg=compliance_result.get("warning", ""))
    return render_template("ask.html")


# ─── Historique ───────────────────────────────────────────────────────────────

@app.route("/history")
@login_required
def history():
    page     = max(1, request.args.get("page", 1, type=int))
    per_page = 10
    offset   = (page - 1) * per_page
    db = get_db()
    total = db.execute(
        "SELECT COUNT(*) FROM requests WHERE user_id=?", (session["user_id"],)
    ).fetchone()[0]
    rows = db.execute(
        """SELECT id, prompt_preview, response_preview, created_at, is_flagged, model_used
           FROM requests WHERE user_id=? ORDER BY created_at DESC LIMIT ? OFFSET ?""",
        (session["user_id"], per_page, offset)
    ).fetchall()
    total_pages = max(1, (total + per_page - 1) // per_page)
    audit("HISTORY_VIEW", detail=f"Page={page}")
    return render_template("history.html", rows=rows, page=page,
                           total_pages=total_pages, total=total)


@app.route("/history/<int:req_id>")
@login_required
def history_detail(req_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM requests WHERE id=? AND user_id=?", (req_id, session["user_id"])
    ).fetchone()
    if not row:
        flash("Requête introuvable.", "danger")
        return redirect(url_for("history"))
    audit("HISTORY_DETAIL", detail=f"RequestID={req_id}")
    return render_template("history_detail.html", row=row)


@app.route("/history/<int:req_id>/delete", methods=["POST"])
@login_required
def delete_request(req_id):
    db = get_db()
    db.execute("DELETE FROM requests WHERE id=? AND user_id=?", (req_id, session["user_id"]))
    db.commit()
    audit("DELETE_REQUEST", detail=f"RequestID={req_id}")
    flash("Requête supprimée (RGPD Art. 17).", "success")
    return redirect(url_for("history"))


# ─── Droits RGPD ──────────────────────────────────────────────────────────────

@app.route("/my-data")
@login_required
def my_data():
    db = get_db()
    user = db.execute(
        "SELECT id, username, role, created_at FROM users WHERE id=?", (session["user_id"],)
    ).fetchone()
    requests_all = db.execute(
        "SELECT id, prompt_preview, response_preview, created_at, model_used FROM requests WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    audit("RGPD_ACCESS_REQUEST")
    return render_template("my_data.html", user=user, requests=requests_all)


@app.route("/my-data/export")
@login_required
def export_data():
    db = get_db()
    user = db.execute(
        "SELECT id, username, role, created_at FROM users WHERE id=?", (session["user_id"],)
    ).fetchone()
    rows = db.execute(
        "SELECT id, prompt_preview, created_at, model_used FROM requests WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    data = {
        "export_date": datetime.now().isoformat(),
        "user": {"id": user["id"], "username": user["username"],
                 "role": user["role"], "created_at": str(user["created_at"])},
        "requests": [dict(r) for r in rows]
    }
    audit("RGPD_EXPORT")
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=mes_donnees.json"}
    )


@app.route("/my-data/delete-all", methods=["POST"])
@login_required
def delete_all_data():
    db = get_db()
    db.execute("DELETE FROM requests WHERE user_id=?", (session["user_id"],))
    db.commit()
    audit("RGPD_DELETE_ALL")
    flash("Tout votre historique a été supprimé (RGPD Art. 17).", "success")
    return redirect(url_for("my_data"))


# ─── Administration ───────────────────────────────────────────────────────────

@app.route("/admin")
@login_required
@admin_required
def admin():
    db = get_db()
    users_count    = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    requests_count = db.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
    flagged_count  = db.execute(
        "SELECT COUNT(*) FROM requests WHERE is_flagged=1 AND admin_action IS NULL"
    ).fetchone()[0]
    recent_flags = db.execute(
        """SELECT r.id, u.username, r.prompt_preview, r.response_preview,
                  r.flag_reason, r.created_at, r.admin_action, r.admin_note, r.admin_at
           FROM requests r JOIN users u ON r.user_id=u.id
           WHERE r.is_flagged=1
           ORDER BY r.created_at DESC LIMIT 20"""
    ).fetchall()
    audit("ADMIN_VIEW")
    return render_template("admin.html", users_count=users_count,
                           requests_count=requests_count,
                           flagged_count=flagged_count,
                           recent_flags=recent_flags)


@app.route("/admin/flag/<int:req_id>/action", methods=["POST"])
@login_required
@admin_required
def admin_action(req_id):
    action = request.form.get("action")
    note   = request.form.get("note", "").strip()
    actions_valides = ("valider", "avertir_utilisateur", "supprimer", "bloquer_utilisateur")
    if action not in actions_valides:
        flash("Action invalide.", "danger")
        return redirect(url_for("admin"))
    db = get_db()
    row = db.execute(
        "SELECT r.*, u.username FROM requests r JOIN users u ON r.user_id=u.id WHERE r.id=?",
        (req_id,)
    ).fetchone()
    if not row:
        flash("Requête introuvable.", "danger")
        return redirect(url_for("admin"))
    now = datetime.now().isoformat()
    if action == "valider":
        db.execute(
            "UPDATE requests SET admin_action='valide', admin_note=?, admin_at=? WHERE id=?",
            (note or "Contenu jugé acceptable", now, req_id)
        )
        audit("ADMIN_VALIDATE", detail=f"RequestID={req_id} User={row['username']}")
        flash(f"Requête #{req_id} validée.", "success")
    elif action == "avertir_utilisateur":
        db.execute(
            "UPDATE requests SET admin_action='averti', admin_note=?, admin_at=? WHERE id=?",
            (note or "Avertissement envoyé", now, req_id)
        )
        try:
            db.execute(
                "INSERT INTO warnings (user_id, req_id, reason, created_at) VALUES (?,?,?,?)",
                (row["user_id"], req_id, note or row["flag_reason"], now)
            )
        except Exception:
            pass
        audit("ADMIN_WARN_USER", detail=f"RequestID={req_id} User={row['username']}")
        flash(f"Avertissement enregistré pour {row['username']}.", "warning")
    elif action == "supprimer":
        db.execute("DELETE FROM requests WHERE id=?", (req_id,))
        audit("ADMIN_DELETE", detail=f"RequestID={req_id} User={row['username']}")
        flash(f"Requête #{req_id} supprimée.", "success")
    elif action == "bloquer_utilisateur":
        db.execute(
            "UPDATE users SET is_blocked=1, blocked_reason=? WHERE id=?",
            (note or "Violation de la politique d'utilisation", row["user_id"])
        )
        db.execute(
            "UPDATE requests SET admin_action='bloque', admin_note=?, admin_at=? WHERE id=?",
            (note, now, req_id)
        )
        audit("ADMIN_BLOCK_USER", detail=f"UserID={row['user_id']} Username={row['username']}")
        flash(f"Compte {row['username']} suspendu.", "danger")
    db.commit()
    return redirect(url_for("admin"))


@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    db = get_db()
    users = db.execute(
        """SELECT u.id, u.username, u.role, u.created_at,
                  COALESCE(u.is_blocked, 0) as is_blocked,
                  u.blocked_reason,
                  COUNT(r.id) as req_count,
                  SUM(CASE WHEN r.is_flagged=1 THEN 1 ELSE 0 END) as flag_count
           FROM users u
           LEFT JOIN requests r ON r.user_id=u.id
           GROUP BY u.id
           ORDER BY flag_count DESC, u.created_at DESC"""
    ).fetchall()
    audit("ADMIN_USERS_VIEW")
    return render_template("admin_users.html", users=users)


@app.route("/admin/users/<int:user_id>/unblock", methods=["POST"])
@login_required
@admin_required
def admin_unblock(user_id):
    db = get_db()
    db.execute("UPDATE users SET is_blocked=0, blocked_reason=NULL WHERE id=?", (user_id,))
    db.commit()
    audit("ADMIN_UNBLOCK", detail=f"UserID={user_id}")
    flash("Compte réactivé.", "success")
    return redirect(url_for("admin_users"))


# ─── Pages légales ────────────────────────────────────────────────────────────

@app.route("/legal")
def legal():
    return render_template("legal.html")


@app.route("/politique")
def politique():
    return render_template("politique.html")


# ─── Teardown & Lancement ─────────────────────────────────────────────────────

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
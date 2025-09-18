import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_from_directory, abort
from ..extensions import db
from ..models import Track, User
from ..services.storage import LocalStorageDriver

tracks_bp = Blueprint("tracks", __name__, url_prefix="/tracks")
storage = LocalStorageDriver(base_dir="uploads")

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("로그인이 필요합니다.", "warning")
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

@tracks_bp.route("/upload", methods=["GET","POST"])
@login_required
def upload():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        file = request.files.get("file")
        if not title or not file:
            flash("제목과 파일을 입력하세요.", "danger")
            return redirect(url_for("tracks.upload"))
        try:
            stored_path = storage.save(file)
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(url_for("tracks.upload"))
        t = Track(
            user_id=session["user_id"],
            title=title,
            filename=os.path.basename(stored_path),
            file_path=stored_path,
        )
        db.session.add(t)
        db.session.commit()
        flash("업로드 완료", "success")
        return redirect(url_for("tracks.list_"))
    return render_template("upload.html", title="업로드")

@tracks_bp.route("")
def list_():
    q = (request.args.get("q") or "").strip()
    query = Track.query.order_by(Track.created_at.desc())
    if q:
        query = query.filter(Track.title.ilike(f"%{q}%"))
    tracks = query.limit(100).all()
    user_map = {u.id: u.username for u in User.query.filter(User.id.in_([t.user_id for t in tracks])).all()}
    items = []
    for t in tracks:
        url = storage.public_url(t.file_path)
        items.append({"id": t.id, "title": t.title, "uploader": user_map.get(t.user_id,"?"), "url": url, "created_at": t.created_at})
    return render_template("list.html", title="트랙 목록", items=items, q=q)

@tracks_bp.route("/media/<path:filename>")
def media(filename):
    base_dir = "uploads"
    full_dir = os.path.abspath(base_dir)
    requested = os.path.abspath(os.path.join(full_dir, filename))
    if not requested.startswith(full_dir):
        abort(404)
    directory = os.path.dirname(requested)
    fname = os.path.basename(requested)
    return send_from_directory(directory, fname, as_attachment=False)

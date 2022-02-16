from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from .models import User, ProfilePicture, Listing, Comments, Likes
import postcodes_io_api
from sqlalchemy import desc
from . import db
import uuid
import os


api  = postcodes_io_api.Api(debug_http=True)

views = Blueprint("views", __name__)


@views.route("/", methods=["GET","POST"])
@views.route("/home", methods=["GET","POST"])
def home():
    page = request.args.get("page",1,type=int)
    listing = Listing.query.order_by(desc(Listing.date_created))
    if request.method == "POST":
        search = request.form.get("search")
        return redirect(url_for("views.search_results", search = search))

    return render_template("home.html", current_user = current_user, listing = listing)

@views.route("/search_results/<search>", methods=["GET","POST"])
def search_results(search):
    listing = Listing.query.filter(Listing.title.contains(search)).all()
    return render_template("listing.html", current_user = current_user, listing = listing)

@views.route("/upload_listing", methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.banned == 1:
        return redirect(url_for("views.home"))
    pathtwo = os.path.abspath(os.getcwd())
    path = fr'{pathtwo}\FLASK PROJECT 5\website\static\uploads'
    if request.method == 'POST':
        file = request.files["input"]
        key = str(uuid.uuid1())
        if file:
            filename = file.filename
            try:
                extension = filename.rsplit('.', 1)[1].lower()
            except:
                extension = "png"
            filename = key + str("." + extension)
            minetype = file.content_type
            file.save(os.path.join(path, filename ))
        else: filename,minetype = "",""
        title = request.form.get("title")
        postcode = request.form.get("postcode")
        description = request.form.get("description")
        postcode_is_valid = api.is_postcode_valid(str(postcode))
        if not postcode_is_valid:
            flash("Invalid postcode", category="error")
        elif str(title) == "":
            flash("No title", category="error")
        else:
            data = api.get_postcode(postcode)
            region = (str(data['result']['region']))
            New_listing = Listing(title=title, postcode=postcode, description=description, user_id = current_user.id, region = region, file = filename, minetype = minetype)
            db.session.add(New_listing)
            db.session.commit()


    return render_template("upload_listing.html", current_user = current_user)


@views.route("/region/<region>")
def region(region):
    listing = Listing.query.filter_by(region = str(region)).order_by(desc(Listing.date_created))
    return render_template("region.html", current_user = current_user, region = region, listing = listing)

@views.route("/listings/<urlforlisting>", methods=["GET", "POST"])
def listings(urlforlisting):
    if current_user.is_authenticated:
        if current_user.banned == 1:
            return redirect(url_for("views.home"))
    listing = Listing.query.filter_by(id = str(urlforlisting)).all()
    flisting = Listing.query.filter_by(id = str(urlforlisting)).first()
    op = User.query.filter_by(id=flisting.user_id).first()
    if flisting:
        if request.method == "POST":
            cmm = request.form.get("cmm")

            if len(cmm) < 1:
                flash("comment too short", category="error")
            else:
                new_comment = Comments(text=cmm, user_id=current_user.id, Listing_id = flisting.id)
                db.session.add(new_comment)
                db.session.commit()
                flash("added", category="success")
        return render_template("listings.html", current_user = current_user, listing = listing, flisting = flisting, op = op, User = User)
    else:
        flash("Listing not found", category="error")
        return redirect(url_for("views.home"))

@views.route("/like/<urlforlisting>", methods=["POST", "GET"])
def like(urlforlisting):
    if current_user.is_authenticated:
        check_like = Likes.query.filter_by(user_id = current_user.id, Listing_id=urlforlisting).first()
        if Listing.query.filter_by(id = str(urlforlisting)).first():
            if check_like:
                db.session.delete(check_like)
                db.session.commit()
            else:
                new_like = Likes(user_id=current_user.id, Listing_id = urlforlisting)
                db.session.add(new_like)
                db.session.commit()
            return redirect(url_for("views.listings", urlforlisting = urlforlisting))
        else:
            flash("Listing not found", category="error")
            return redirect(url_for("views.home"))
    else:
        flash("Login to like posts", category="error")
        return redirect(url_for("views.listings", urlforlisting = urlforlisting))

@views.route("/remove/<urlforlisting>")
@login_required
def remove(urlforlisting):
    if current_user.admin == 1 and current_user.banned == 0:
        listing = Listing.query.filter_by(id=urlforlisting).first()
        if listing.removed == 1:
            listing.removed = 0
        else:
            listing.removed = 1
        db.session.commit()
        return redirect(url_for("views.listings", urlforlisting = urlforlisting))
    else:
        flash("access denied", category="error")
        return redirect(url_for("views.home"))

@views.route("/removecomment/<idforcomment>")
@login_required
def removecomment(idforcomment):
    if current_user.admin == 1 and current_user.banned == 0:
        comment = Comments.query.filter_by(id=idforcomment).first()
        if comment.removed == 1:
            comment.removed = 0
        else:
            comment.removed = 1
        db.session.commit()
        return redirect(url_for("views.listings", urlforlisting = comment.Listing_id))
    else:
        flash("access denied", category="error")
        return redirect(url_for("views.home"))

@views.route("/about")
def about():
    return render_template("about.html", current_user = current_user)

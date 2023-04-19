from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from pprint import pprint
import math

#API INFORMATION
API_ID_SEARCH_ENDPOINT = "https://api.themoviedb.org/3/search/movie"
API_MOVIE_SEARCH_ENDPOINT = "https://api.themoviedb.org/3/movie"
API_KEY = "d798fc485f107444ba0d05314156315a"
MOVIE_TEST = "Die Hard"

parameters_id = {
    "api_key": API_KEY,
    "query": MOVIE_TEST,
}

response_id = requests.get(url=API_ID_SEARCH_ENDPOINT, params=parameters_id)
response_id.raise_for_status()
data = response_id.json()
movie_data = data["results"]
movies = []
for movie in movie_data:
    movies.append(
        {"title": movie["title"],
         "release date": movie["release_date"],
         "id": movie["id"],
        }
    )


# parameters_movie = {
#     "api_key": API_KEY,
# }
#
# response_2 = requests.get(url=f"{API_MOVIE_SEARCH_ENDPOINT}/{MOVIE_ID}", params=parameters_movie)
# response_2.raise_for_status()
# movie_data_2 = response_2.json()
# #pprint(movie_data)


db = SQLAlchemy()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

Bootstrap5(app)

db.init_app(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False )
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String, nullable=True)
    img_url = db.Column(db.String, nullable=False)


class MovieForm(FlaskForm):
    title = StringField('Movie Name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class RatingForm(FlaskForm):
    rating = StringField('Your Rating Out of 10 e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/")
def home():
    all_movies = db.session.query(Movie).order_by(Movie.rating)
    total = all_movies.count()
    count = 0
    for movie in all_movies:
        movie.ranking = total - count
        db.session.commit()
        count += 1
    return render_template("index.html", all_movies=all_movies)


@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):
    form = RatingForm()
    movie_to_update = Movie.query.filter_by(id=index).first()
    movie = movie_to_update
    if form.validate_on_submit():
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=movie)


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        parameters_id = {
            "api_key": API_KEY,
            "query": form.title.data,
        }

        response_id = requests.get(url=API_ID_SEARCH_ENDPOINT, params=parameters_id)
        response_id.raise_for_status()
        data = response_id.json()
        movie_data = data["results"]
        movies = []
        for movie in movie_data:
            movies.append(
                {"title": movie["title"],
                 "year": movie["release_date"],
                 "id": movie["id"],
                 }
            )
        #db.session.add(new_movie)
        #db.session.commit()
        return render_template("select.html", movies=movies)

    return render_template("add.html", form=form)

# @app.route("/entry/<int:id>/<string:title>/<int:year>")
# def entry(id,year,title):
#
#     parameters_movie = {
#         "api_key": API_KEY,
#     }
#
#     MOVIE_ID =
#
#     response_2 = requests.get(url=f"{API_MOVIE_SEARCH_ENDPOINT}/{MOVIE_ID}", params=parameters_movie)
#     response_2.raise_for_status()
#     movie_data_final = response_2.json()


@app.route("/entry/<int:id>", methods=["GET", "POST"])
def add_to_database(id):

    parameters_movie = {
        "api_key": API_KEY,
    }

    MOVIE_ID = id

    response_2 = requests.get(url=f"{API_MOVIE_SEARCH_ENDPOINT}/{MOVIE_ID}", params=parameters_movie)
    response_2.raise_for_status()
    movie_data_final = response_2.json()
    #pprint(movie_data_final)

    id = movie_data_final["id"]
    print(id)
    title=movie_data_final["title"]
    print(title)
    year=movie_data_final["release_date"].split("-")[0]
    print(year)
    description=movie_data_final["overview"]
    print(description)
    rating=movie_data_final["vote_average"]
    rating=math.ceil(rating)
    print(rating)
    img_url=movie_data_final["poster_path"]
    print(img_url)
    new_movie = Movie(
        title=title,
        year=year,
        description=description,
        rating=rating,
        img_url=f"https://image.tmdb.org/t/p/w500{img_url}",
        )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', index=new_movie.id))

def add():
    new_movie = Movie(
        title="Phone Booth",
        year=2002,
        description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
        rating=7.3,
        ranking=10,
        review="My favourite character was the caller.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    )
    db.session.add(new_movie)
    db.session.commit()


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
    with app.app_context():
        db.create_all()
        add()
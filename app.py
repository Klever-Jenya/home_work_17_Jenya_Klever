from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from create_data import data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace("movies")
director_ns = api.namespace("director")
genre_ns = api.namespace("genre")


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = MovieSchema()
directors_schema = MovieSchema(many=True)

genre_schema = MovieSchema()
genres_schema = MovieSchema(many=True)


# -------------------------------------------------========Movies========--------------------------------
@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        movies_query = db.session.query(Movie)  # +

        director_id = request.args.get("director_id")
        if director_id is not None:
            movies_query = movies_query.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            movies_query = movies_query.filter(Movie.genre_id == genre_id)

        return movies_schema.dump(movies_query.all()), 200

    def post(self):
        request_json = request.json
        new_movie = Movie(**request_json)

        with db.session.begin():
            db.session.add(new_movie)

        return "Movie created", 201


@movie_ns.route("/<int:uid>")  # +
class MovieView(Resource):
    def get(self, uid):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "Фильм не найден", 404
        return movie_schema.dump(movie), 200

    def put(self, uid):
        updated_rows = db.session.query(Movie).filter(Movie.id == uid).update(request.json)  # int

        if updated_rows != 1:
            return "not updated", 400

        db.session.commit()
        return "", 204

    def delete(self, uid):
        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "Фильм не найден", 404

        db.session.delete(movie)
        db.session.commit()

        return "", 204


# ---------------------------------========Directors========----------------------------------


@director_ns.route("/")
class DirectorsView(Resource):
    def get(self):
        directors = db.session.query(Director)
        return directors_schema.dump(directors.all()), 200

    def post(self):
        request_json = request.json
        new_director = Director(**request_json)

        db.session.add(new_director)
        db.session.commit()

        return "Director created", 201


@director_ns.route("/<int:uid>")  # +
class DirectorView(Resource):
    def get(self, uid):
        try:
            director = db.session.query(Director).get(uid)
            return director_schema.dump(director), 200
        except Exception:
            return str(Exception), 404

    def put(self, uid):
        director = Director.query.get(uid)
        request_json = request.json
        if "name" in request_json:
            director.name = request_json.get("name")

        db.session.add(director)
        db.session.commit()

        return "", 204

    def delete(self, uid: int):
        director = db.session.query(Director).get(uid)
        if not director:
            return "Режиссер не найден", 404

        db.session.delete(director)
        db.session.commit()

        return "", 204

# --------------------------========Ganres========--------------------------------


@genre_ns.route("/")
class GenresView(Resource):
    def get(self):
        genres_query = db.session.query(Genre)
        return genres_schema.dump(genres_query.all()), 200

    def post(self):
        request_json = request.json
        new_genre = Genre(**request_json)

        with db.session.begin():
            db.session.add(new_genre)

        return "genre created", 201


@genre_ns.route("/<int:uid>")
class GenreView(Resource):
    def get(self, uid):
        genre = db.session.query(Genre).get(uid)
        if not genre:
            return "Жанр не найден", 404
        return genre_schema.dump(genre), 200

    def put(self, uid):
        updated_rows = db.session.query(Genre).filter(Genre.id == uid).update(request.json)  # int

        if updated_rows != 1:
            return "not updated", 400

        db.session.commit()
        return "", 204

    def delete(self, uid):
        genre = db.session.query(Genre).get(uid)
        if not genre:
            return "Жанр не найден", 404

        db.session.delete(genre)
        db.session.commit()

        return "", 204


if __name__ == '__main__':
    app.run(debug=True)

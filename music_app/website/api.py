from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from .models import db, Song

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

class SongResource(Resource):
    def get(self, song_id=None):
        if song_id:
        # If song_id is provided, fetch a single song
            song = Song.query.get_or_404(song_id)
            song_info = {
                'id': song.id,
                'name': song.name,
                'lyrics': song.lyrics,
                'duration': song.duration,
                'singer': song.singer,
                'genre': song.genre,
                'created_at': song.created_at.isoformat(),
                'ratings': song.ratings,
                'num_ratings': song.num_ratings,
                'user_id': song.user_id
            }
            return jsonify(song_info)
        else:
            # If no song_id is provided, fetch all songs
            songs = Song.query.all()
            song_list = []
            for song in songs:
                song_info = {
                    'id': song.id,
                    'name': song.name,
                    'lyrics': song.lyrics,
                    'duration': song.duration,
                    'singer': song.singer,
                    'genre': song.genre,
                    'created_at': song.created_at.isoformat(),
                    'ratings': song.ratings,
                    'num_ratings': song.num_ratings,
                    'user_id': song.user_id
                }
                song_list.append(song_info)

            return jsonify({'songs': song_list})

    def put(self, song_id):
        song = Song.query.get_or_404(song_id)
        # Update the song attributes based on the request data
        data = request.get_json()
        song.name = data.get('name', song.name)
        song.lyrics = data.get('lyrics', song.lyrics)
        song.singer =data.get('singer', song.singer)
        # Update other attributes similarly

        db.session.commit()
        return {'message': 'Song updated successfully'}

    def delete(self, song_id):
        song = Song.query.get_or_404(song_id)
        db.session.delete(song)
        db.session.commit()
        return {'message': 'Song deleted successfully'}

api.add_resource(SongResource,  '/song/',   '/song/<int:song_id>')



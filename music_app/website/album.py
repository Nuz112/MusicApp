from flask import Blueprint, render_template, url_for, session, redirect, render_template, flash, request
from . import db
from .models import Song, Album



album = Blueprint('album', __name__)


@album.route('/view_albums')
def view_albums():
    user_name = session.get('user_name')
    albums = Album.query.all()



    return render_template('view_albums.html', user_name= user_name, albums= albums)






@album.route('/create_album', methods = ['GET', 'POST'])
def create_album():
    user_name = session.get('user_name')
    user_id = session.get('user')
    
    if request.method == 'POST':
        album_name = request.form.get('album_name')
        selected_song_ids = request.form.getlist('selected_songs')  
        album = Album(name=album_name, user_id=user_id)
        db.session.add(album)
        
        # Add selected songs to the album
        selected_songs = Song.query.filter(Song.id.in_(selected_song_ids)).all()
        album.album_songs.extend(selected_songs)

        db.session.commit()
        flash('Album created successfully', 'success')
        return redirect(url_for('album.view_albums'))

    songs = Song.query.all()

    return render_template('create_album.html',  user_name=user_name, songs= songs)









@album.route('/view_album_songs/<album_id>')
def view_album_songs(album_id):
    user_name = session.get('user_name')
    album = Album.query.filter_by(id = album_id).first()
    songs = album.album_songs


    return render_template('view_album_songs.html', user_name= user_name, songs= songs, album=album)







@album.route('/remove_from_album/<int:album_id>/<int:song_id>', methods=['POST', 'GET'])
def remove_from_album(album_id, song_id):
    user_id = session.get('user')
    user_name = session.get('user_name')

    # Check if the user owns the playlist and the song
    album= Album.query.filter_by(id=album_id, user_id= user_id).first()
    songs = Album.query.filter_by(id=album_id)
    song = Song.query.filter_by(id=song_id).first()

    if request.method == 'POST' :
        if album and song:
            if (song in album.album_songs):
                album.album_songs.remove(song)
                db.session.commit()
                flash('Song removed from the Album', 'success')
            else:
                flash('Song is not in the selected Album', 'error')
        else:
            flash('Song or Album not found, or you do not have permission to remove the song from the Album', 'error')

    return redirect(url_for('album.view_album_songs', album_id = album_id))







@album.route('/delete_album/<album_id>' , methods = ['POST'])
def delete_album( album_id ):
    user_id = session.get('user')
    
    
    # Retrieve the selected playlist
    album = Album.query.filter_by(user_id=user_id, id=album_id ).first()
    
    if album:
        # Remove the songs from the playlist
        for song in album.album_songs:
            album.album_songs.remove(song)
        
        # Delete the playlist
        db.session.delete(album)
        db.session.commit()
        
        flash('Album deleted successfully', 'success')
    else:
        flash('Selected Album not found', 'error')

    return redirect(url_for('album.view_albums'))


@album.route('/search_album', methods=['GET'])
def search_album():
    query = request.args.get('query', '')

    if query:
        user_name = session.get('user_name')
        search_results = db.session.query(Album).filter(Album.name.ilike(f'%{query}%')).all()
    else:

        search_results = []

    return render_template('search_album.html', query=query, results=search_results, user_name=user_name)






@album.route('/add_songs_to_album/<int:album_id>', methods=['GET', 'POST'])
def add_songs_to_album(album_id):
    album = Album.query.get_or_404(album_id)
    # Check if the current user is the creator of the album
    if request.method == 'GET':
        if album.user_id != session.get('user'):
            flash('You are not authorized to perform this action.', 'danger')
            return redirect(url_for('album.view_album_songs', album_id=album_id))

        # Fetch the remaining songs not in the album
        remaining_songs = get_remaining_songs(album)

        return render_template('add_songs_to_album.html', album=album, remaining_songs=remaining_songs)
    
    else:
        user_name = session.get('user_name')
        selected_song_ids = request.form.getlist('selected_songs') 
        selected_songs = Song.query.filter(Song.id.in_(selected_song_ids)).all()
        album.album_songs.extend(selected_songs)
        db.session.commit()
        songs = album.album_songs
        flash('Songs added successfully', 'success')
        return render_template('view_album_songs.html', user_name= user_name, songs= songs, album=album) 


def get_remaining_songs(album):
    # Query to get songs that are not in the album
    remaining_songs = Song.query.filter(~Song.albums.any(id=album.id)).all()
    return remaining_songs

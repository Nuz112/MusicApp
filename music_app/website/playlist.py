from flask import Blueprint, render_template, url_for, session, redirect, render_template, flash, request
from . import db
from .models import Song, Playlist, playlist_song_association



playlist = Blueprint('playlist', __name__)





@playlist.route('/add_to_playlist/<int:song_id>', methods=['GET', 'POST'])
def add_to_playlist(song_id):
    user_id = session.get('user')
    user_name = session.get('user_name')
    
    # Get the user's playlists
    playlists = Playlist.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':
        playlist_id = request.form.get('playlist')
        new_playlist_name = request.form.get('new_playlist')

        if not playlist_id and not new_playlist_name:
            flash('Please select an existing playlist or create a new one', 'error')
        else:
            # Add the song to the selected playlist or create a new one
            song = Song.query.get(song_id)

            if playlist_id:
                playlist = Playlist.query.get(playlist_id)
                if playlist:
                    playlist.songs.append(song)
                    db.session.commit()
                    flash('Song added to the selected playlist', 'success')
                else:
                    flash('Selected playlist not found', 'error')

            if new_playlist_name:
                new_playlist = Playlist(name=new_playlist_name, user_id=user_id)
                new_playlist.songs.append(song)
                db.session.add(new_playlist)
                db.session.commit()
                flash('Song added to the new playlist', 'success')

        return redirect(url_for('views.home'))

    return render_template('add_to_playlist.html', song_id=song_id, playlists=playlists, user_name=user_name)








@playlist.route('/select_playlist')
def select_playlist():
    user_id = session.get('user')
    user_name = session.get('user_name')

    # Retrieve the user's playlists
    playlists = Playlist.query.filter_by(user_id=user_id).all()

    return render_template('select_playlist.html', playlists=playlists, user_name=user_name)






@playlist.route('/user_selected_playlist/<playlist_name>')
def user_selected_playlist(playlist_name):
    user_id = session.get('user')
    user_name = session.get('user_name')
    
    # Retrieve the selected playlist
    playlist = Playlist.query.filter_by(user_id=user_id, name=playlist_name).first()
    
    if playlist:
        songs = playlist.songs
        return render_template('user_selected_playlist.html', songs=songs, playlist=playlist, user_name=user_name)
    else:
        flash('Selected playlist not found', 'error')
        return redirect(url_for('playlist.select_playlist'))




@playlist.route('/remove_from_playlist/<int:playlist_id>/<int:song_id>', methods=['POST', 'GET'])
def remove_from_playlist(playlist_id, song_id):
    user_id = session.get('user')
    user_name = session.get('user_name')

    # Check if the user owns the playlist and the song
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
    songs= playlist.songs
    song = Song.query.filter_by(id=song_id).first()
    print(songs)
    if request.method == 'POST' :
        if playlist and song:
            if (song in playlist.songs):
                playlist.songs.remove(song)
                db.session.commit()
                flash('Song removed from the playlist', 'success')
            else:
                flash('Song is not in the selected playlist', 'error')
        else:
            flash('Song or playlist not found, or you do not have permission to remove the song from the playlist', 'error')

    return redirect(url_for('playlist.user_selected_playlist', user_name = user_name, songs= songs, playlist_name= playlist.name))



@playlist.route('/delete_playlist/<playlist_name>')
def delete_playlist(playlist_name):
    user_id = session.get('user')
    user_name = session.get('user_name')
    
    # Retrieve the selected playlist
    playlist = Playlist.query.filter_by(user_id=user_id, name=playlist_name).first()
    
    if playlist:
        # Remove the songs from the playlist
        for song in playlist.songs:
            playlist.songs.remove(song)
        
        # Delete the playlist
        db.session.delete(playlist)
        db.session.commit()
        
        flash('Playlist deleted successfully', 'success')
    else:
        flash('Selected playlist not found', 'error')

    return redirect(url_for('playlist.select_playlist'))

@playlist.route('/search_playlist', methods=['GET'])
def search_playlist():
    query = request.args.get('query', '')

    if query:
        user_id = session.get('user')
        user_name = session.get('user_name')
        
        # Assuming that Playlist has a relationship with User
        user_playlists = db.session.query(Playlist).filter(
            Playlist.name.ilike(f'%{query}%'),
            Playlist.user_id == user_id
        ).all()
    else:
        user_playlists = []

    return render_template('search_playlist.html', query=query, results=user_playlists, user_name=user_name)



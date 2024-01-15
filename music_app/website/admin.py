from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User, Album, Playlist, Song,  db, playlist_song_association
from sqlalchemy.sql import func
from sqlalchemy import or_
import matplotlib.pyplot as plt
from io import BytesIO
import base64




admin = Blueprint('admin', __name__)




@admin.route('/', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if this is the admin's email and password
        admin_email = "patelnujhat114@gmail.com"  
        admin_password = "nuj123"  

        if email == admin_email and password == admin_password:
            
            session['admin'] = True
            flash('Admin login successful', category='success')
            return redirect(url_for('admin.admin_dashboard'))  
        else:
            flash('Admin login failed. Please check your credentials.', category='error')

    return render_template("admin_login.html")









@admin.route('/dashboard')
def admin_dashboard():

    if session.get('admin'):

        num_users = User.query.count()
        num_albums = Album.query.count()
        top_rated_songs = Song.query.order_by(Song.ratings.desc()).limit(10).all()
        num_users_uploaded_songs = User.query.filter(User.songs.any()).count()

        # Query for the top 5 most popular songs based on how many playlists include them
        top_popular_songs = db.session.query(
            Song, func.count(playlist_song_association.c.playlist_id)
        ).join(
            playlist_song_association
        ).group_by(
            Song
        ).order_by(
            func.count(playlist_song_association.c.playlist_id).desc()
        ).limit(5).all()

        labels = [song.name for song, _ in top_popular_songs]
        counts = [count for _, count in top_popular_songs]

        fig, ax = plt.subplots()
        ax.bar(labels, counts)
        ax.set_ylabel('Number of Playlists')
        ax.set_title('Top Songs by Playlist Count')

        ax.set_xticklabels(labels, rotation=35, ha='right')
        plt.subplots_adjust(bottom=0.3)

        # Save the plot to a BytesIO object
        img_io = BytesIO()
        plt.savefig(img_io, format='png')
        img_io.seek(0)

        # Embed the plot in the HTML template
        img_data = base64.b64encode(img_io.read()).decode('utf-8')    








        return render_template('admin_dashboard.html',
                            num_users=num_users,
                            top_rated_songs=top_rated_songs,
                            num_users_uploaded_songs=num_users_uploaded_songs,
                            top_popular_songs =top_popular_songs,
                            num_albums = num_albums,
                            img_data = img_data
                            )
    else:
        flash('You must be logged in as an admin to access this page.', category='error')
        return redirect(url_for('admin.admin_login'))







@admin.route('/songs')
def songs():
    
    if session.get('admin'):
        songs = Song.query.all()
        return render_template("admin_songs.html",  songs=songs)
    else:
        flash('Please Login First')
    return redirect(url_for('admin.login'))







@admin.route('/delete_song/<int:song_id>', methods=['POST', 'GET'])
def delete_song(song_id):
    if session.get('admin'):
        if request.method == 'POST':
                song_to_delete = Song.query.filter_by(id=song_id).first()

                if song_to_delete:
                    # Mark the song for deletion
                    print(f"Deleting song: {song_to_delete.name}")
                    db.session.delete(song_to_delete)
                    db.session.commit()
                    flash('Song deleted successfully', 'success')

    else:
        flash('Please log in to delete a song', 'error')

    return redirect(url_for('admin.songs'))





@admin.route('/admin_album_songs/<album_id>')
def admin_album_songs(album_id):

    album = Album.query.filter_by(id = album_id).first()
    songs = album.album_songs


    return render_template('admin_album_songs.html', songs= songs, album=album)






@admin.route('/admin_albums')
def admin_albums():
    if session.get('admin'):
        albums = Album.query.all()
        return render_template('admin_albums.html', albums= albums)

    else:
        flash('Please log in first', 'error')

        return redirect(url_for('admin.login'))






@admin.route('/remove_from_album/<int:album_id>/<int:song_id>', methods=['POST', 'GET'])
def remove_from_album(album_id, song_id):
    # Check if the user owns the playlist and the song
    album= Album.query.filter_by(id=album_id).first()
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

    return redirect(url_for('admin.admin_album_songs', album_id = album_id))





@admin.route('/delete_album/<album_id>' , methods = ['POST'])
def delete_album( album_id ):

    album = Album.query.filter_by( id=album_id ).first()
    
    if album:
        for song in album.album_songs:
            album.album_songs.remove(song)

        db.session.delete(album)
        db.session.commit()
        
        flash('Album deleted successfully', 'success')
    else:
        flash('Selected Album not found', 'error')

    return redirect(url_for('admin.admin_albums'))







@admin.route('/logout')
def logout():

    if session.get('admin'):
            # If an admin was logged in, log them out too
            session.pop('admin', None)
            
    return redirect(url_for('admin.admin_login'))



@admin.route('/search_music', methods=['GET'])
def search_music():
    query = request.args.get('query', '')

    if query:
        user_name = session.get('user_name')
        search_results = db.session.query(Song).filter(Song.name.ilike(f'%{query}%')).all()
    else:

        search_results = []

    return render_template('admin_search_music.html', query=query, results=search_results)



@admin.route('/user_list', methods=['GET'])
def user_list():
    if session.get('admin'):
        users = User.query.all()

        def is_creator(user):
            return bool(user.songs)

        return render_template('admin_users.html', users=users, is_creator=is_creator)
    

    else:
            flash('You must be logged in as an admin to access this page.', category='error')
            return redirect(url_for('admin.admin_login'))



@admin.route('/toggle_white_list/<int:user_id>', methods=['POST'])
def toggle_white_list(user_id):
    user = User.query.get_or_404(user_id)

    user.white_list = not user.white_list
    db.session.commit()
    return redirect(url_for('admin.user_list'))



@admin.route('/search_user', methods=['GET'])
def search_user():
    query = request.args.get('query', '')

    if query:
        users = db.session.query(User).filter(
                or_(
                User.email.ilike(f'%{query}%'),
                User.first_name.ilike(f'%{query}%'),
                User.last_name.ilike(f'%{query}%')
            )
        ).all()
    else:

        users = []

    def is_creator(user):
        return bool(user.songs)

    return render_template('admin_users.html', users=users, is_creator=is_creator)
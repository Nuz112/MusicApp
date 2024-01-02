from flask import Blueprint, render_template, url_for, session, redirect, render_template, flash, request
from . import db
from .models import Song, Rating, Playlist, Album, User
from os.path import join





views = Blueprint('views', __name__)



@views.route('/home')
def home():
    user_name = session.get('user_name')
    if user_name:
        songs = Song.query.all()
        return render_template("home.html",  user_name=user_name, songs=songs)
    else:
        flash('Please Login First')
    return redirect(url_for('auth.login'))



@views.route('/filter_songs', methods=['POST'])
def filter_songs():
    user_name = session.get('user_name')
    selected_genre = request.form.get('genre')

    if selected_genre == 'All':
        songs = Song.query.all()
    else:
        songs = Song.query.filter_by(genre=selected_genre).all()

    return render_template("home.html", user_name=user_name, songs=songs, selected_songs= selected_genre)





@views.route('/upload_song', methods=['GET', 'POST'])
def upload_song():
    user_name = session.get('user_name')
    
    if not user_name:
        flash('Please Login First')
        return redirect(url_for('auth.login'))
    
    songs = Song.query.filter_by(user_id = session.get('user'))
    if request.method == 'POST':
            user_id = session.get('user')
            user= User.query.get(user_id)
            if user.white_list:
                song_name = request.form['songName']
                singer_name = request.form['singer_name']
                lyrics = request.form['lyrics']
                duration = request.form['duration']
                genre = request.form['genre']
                song_file = request.files['song']
                user_id = session['user']



                print(song_file.filename)
                if song_file:
                # Create a new song instance and populate its attributes
                    new_song = Song(
                        name=song_name,
                        singer=singer_name,
                        lyrics=lyrics,
                        genre = genre,
                        duration=duration,
                        user_id= user_id, 


                    )

                    # Add the song to the database
                    db.session.add(new_song)
                    db.session.commit()

                # Save the song file to a storage location
                    #song_file.save('website/static' + song_file.filename)
                    song_file.save(join('website', 'static', 'songs', song_file.filename))
                    flash('Song uploaded successfully', 'success')
                    return redirect(url_for('views.upload_song'))
                

            
                else:
                    flash('No file was uploaded', 'error')
            
            else:
                flash("You are in a Black List, You can't upload a Song", 'error')



    return render_template("upload_song.html", user_name=user_name, songs = songs)









@views.route('/rate_song/<int:song_id>', methods=['POST'])
def rate_song(song_id):
    user_id = session.get('user')

    # Check if the user has already rated this song
    existing_rating = Rating.query.filter_by(user_id=user_id, song_id=song_id).first()

    if existing_rating:
        flash('You have already rated this song.', 'error')
    else:
        # Get the rating from the form
        rating = int(request.form.get('rating'))

        if 1 <= rating <= 5:
            # Create a new rating record
            new_rating = Rating(user_id=user_id, song_id=song_id, rating=rating)

            # Update the song's total ratings and the number of ratings
            song = Song.query.get(song_id)
            song.ratings = (song.ratings * song.num_ratings + rating) / (song.num_ratings + 1)
            song.num_ratings += 1

            # Commit the changes to the database
            db.session.add(new_rating)
            db.session.commit()

            flash(f'You rated the song with {rating} stars.', 'success')
        else:
            flash('Invalid rating value. Please rate the song from 1 to 5 stars.', 'error')

    return redirect(url_for('views.home'))



@views.route('/lyrics/<int:song_id>')
def lyrics(song_id):
    song = Song.query.get(song_id)
    return render_template('lyrics.html', song=song)




@views.route('/edit_song/<int:song_id>', methods = ['POST','GET'])
def edit_song(song_id):
    song = Song.query.get(song_id)
    if request.method == 'GET':
        return render_template('edit_song.html', song=song)
    else:
        name = request.form.get('name')
        lyrics = request.form.get('lyrics')
        singer = request.form.get('singer')

        # Update the song details
        song.name = name
        song.lyrics = lyrics
        song.singer = singer

        # Commit changes to the database
        db.session.commit()

        flash('Song updated successfully', 'success')
        return redirect(url_for('views.upload_song'))








@views.route('/delete_song/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    # Get the current user's ID or any other way to identify the user
    user_id = session.get('user')

    if user_id:
        if request.method == 'POST':
            try:
            # Retrieve the song from the database based on song_id and user_id
                song_to_delete = Song.query.filter_by(id=song_id, user_id=user_id).first()

                if song_to_delete:
                    # Mark the song for deletion
                    print(f"Deleting song: {song_to_delete.name}")
                    db.session.delete(song_to_delete)
                    db.session.commit()
                    flash('Song deleted successfully', 'success')
                else:
                    flash('Song not found or you do not have permission to delete it', 'error')
            except Exception as e:
                flash(f'Error deleting song: {str(e)}', 'error')

    else:
        flash('Please log in to delete a song', 'error')

    return redirect(url_for('views.home'))






@views.route('/user_summary')
def user_summary():

    user_id = session.get('user')
    user_name = session.get('user_name')
    user = User.query.get(user_id)

    # Number of songs uploaded by the user
    num_songs = len(user.songs)

    # Number of playlists created by the user 
    num_playlists = len(user.playlists)

    # Number of albums created by the user
    num_albums = len(user.albums)

    # Average rating of all songs uploaded by the user
    total_rating = 0
    for song in user.songs:
        total_rating += song.ratings
    average_rating = total_rating / num_songs if num_songs > 0 else 0

    # The song(s) with the highest rating uploaded by the user
    highest_rated_songs = (
        Song.query.filter_by(user_id=user_id)
        .order_by(Song.ratings.desc())
        .limit(5)  # You can limit to a specific number of top-rated songs
        .all()
    )

    return render_template(
        'user_summary.html',
        user=user,
        user_name = user_name,
        num_songs=num_songs,
        num_playlists=num_playlists,
        num_albums=num_albums,
        average_rating=average_rating,
        highest_rated_songs=highest_rated_songs,
    )



@views.route('/privacy_policy')
def privacy_policy():
    user_name = session.get('user_name')

    return render_template('privacy_policy.html', user_name = user_name)





@views.route('/search_music', methods=['GET'])
def search_music():
    query = request.args.get('query', '')

    if query:
        user_name = session.get('user_name')
        search_results = db.session.query(Song).filter(Song.name.ilike(f'%{query}%')).all()
    else:

        search_results = []

    return render_template('search_music.html', query=query, results=search_results, user_name=user_name)


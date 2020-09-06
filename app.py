#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

import sys
import datetime
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String)
    website = db.Column(db.String(120))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String)
    website = db.Column(db.String(120))
  
class Show(db.Model):
    __tablename__ = 'Show'
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
    start_time = db.Column(db.String, primary_key=True)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  cities_state = []
  
  for venue in Venue.query.distinct(Venue.city):
    cities_state.append((venue.city, venue.state))

  datas = []

  # Organize venues into groups of different city - state pairs
  for city_state_pair in cities_state:
    data = {
      "city": city_state_pair[0],
      "state": city_state_pair[1],
      "venues": Venue.query.filter_by(city=city_state_pair[0]).all()
    }
    datas.append(data)
  

  return render_template('pages/venues.html', areas=datas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = (request.form.get('search_term', '')).lower()
  venues = Venue.query.all()

  count = 0
  datas = []
  # Search in venues with case-insensitive search term
  for venue in venues:
    if search_term in (venue.name).lower():
      count += 1
      data = {
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": 0
      }

      datas.append(data)

  response = {
    "count": count,
    "data": datas
  }


  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # Shows the venue page with the given venue_id
  venue = Venue.query.filter_by(id=venue_id).all()[0]
  shows = Show.query.filter_by(venue_id=venue_id).all()

  current_time = datetime.datetime.now()

  past_shows = []
  upcoming_shows =[]

  # Check for shows at this venue whether they are in the past or in the future
  for show in shows:
    each_show = {
      "artist_id" : show.artist_id,
      "artist_name" : Artist.query.get(show.artist_id).name,
      "artist_image_link" : Artist.query.get(show.artist_id).image_link,
      "start_time" : show.start_time
    }

    if int(show.start_time[:4]) < int(str(current_time)[:4]):
      past_shows.append(each_show)
    elif int(show.start_time[:4]) > int(str(current_time)[:4]):
      upcoming_shows.append(each_show)
    else:
      if int(show.start_time[5:7]) < int(str(current_time)[5:7]):
        past_shows.append(each_show)
      elif int(show.start_time[5:7]) > int(str(current_time)[5:7]):
        upcoming_shows.append(each_show)
      else:
        if int(show.start_time[8:10]) > int(str(current_time)[8:10]):
          past_shows.append(each_show)
        elif int(show.start_time[8:10]) < int(str(current_time)[8:10]):
          upcoming_shows.append(each_show)
        else:
          if int(show.start_time[11:13]) < int(str(current_time)[11:13]):
            past_shows.append(each_show)
          elif int(show.start_time[11:13]) > int(str(current_time)[11:13]):
            upcoming_shows.append(each_show)
          else:
            if int(show.start_time[14:]) < int(str(current_time)[14:16]):
              past_shows.append(each_show)
            elif int(show.start_time[14:]) > int(str(current_time)[14:16]):
              upcoming_shows.append(each_show)
            else:
              past_shows.append(each_show)
      
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # Create new record for a venue
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  genres = request.form.getlist('genres')
  phone =  request.form['phone']
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website = request.form['website']
  seeking_talent = request.form['seeking_talent']
  seeking_description = request.form['seeking_description']

  # Make sure the value seeking_talent is boolean
  if seeking_talent == 'True':
    seeking_talent = True
  else:
    seeking_talent = False

  exists = db.session.query(Venue.id).filter_by(name=name).scalar() is not None

  validPhone = True
  if phone:
    validPhone = valid_phone(phone)

  if exists:
    # Check if venue is already in database
    flash('An error occurred. Venue ' + name + ' already exists!.')
    return redirect(url_for('create_venue_form'))
  elif not validPhone:
    # Check if phone is valid
    flash('An error occurred. Invalid phone number!')
    return redirect(url_for('create_venue_form'))
  else:
    # Try input data into database
    try:
      venue = Venue(
        name=name,
        city=city,
        state=state,
        address=address,
        phone=phone,
        genres=genres,
        facebook_link=facebook_link,
        image_link=image_link,
        website=website,
        seeking_talent=seeking_talent,
        seeking_description=seeking_description
      )

      db.session.add(venue)
      db.session.commit()

      # On successful db insert, flash success
      flash('Venue ' + name + ' was successfully listed!')
    except:
      # On unsuccessful db insert, flash error
      db.session.rollback()
      flash('An error occurred. Venue ' + name + ' could not be listed.')
      print(sys.exc_info())
    finally:
      db.session.close()

  return render_template('pages/home.html')

def valid_phone(number):
  # Check if input phone number is formatted correctly for creation or 
  # edit of venue or artist
  if len(number) != 12:
    return False
  for i in range(0, 12):
    if i != 3 and i != 7:
      try:
        val = int(number[i])
      except ValueError:
        return False
    else:
      if number[i] != '-':
        return False
  
  return True

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # Delete venue with venue_id

  venue = Venue.query.get(venue_id)
  name = venue.name
  shows = Show.query.filter_by(venue_id=venue_id).all()

  # Delete any show at the to-be-delete venue first to ensure data integrity
  try:
    for show in shows:
      db.session.delete(show)
    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Show with venue ' + name + ' could not be deleted!')
    print(sys.exc_info())
  finally:
    db.session.close()

  # Actually delete the venue
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('Venue ' + name + ' along with any show at this venue were successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be deleted.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return jsonify({'success': True})

@app.route('/artist/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
  # Delete artist with artist_id

  artist = Artist.query.get(artist_id)
  name = artist.name
  shows = Show.query.filter_by(artist_id=artist_id).all()
  # Delete any show with the to-be-delete artist first to ensure data integrity
  try:
    for show in shows:
      db.session.delete(show)
    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Show with artist ' + name + ' could not be deleted!')
    print(sys.exc_info())
  finally:
    db.session.close()

  # Actually delete artist
  try:
    db.session.delete(artist)
    db.session.commit()
    flash('Artist ' + name + ' along with any show with this artist were successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + name + ' could not be deleted.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = (request.form.get('search_term', '')).lower()
  artists = Artist.query.all()

  count = 0
  datas = []
  # Search in artists with case-insensitive search term 
  for artist in artists:
    if search_term in (artist.name).lower():
      count += 1
      data = {
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": 0
      }
      datas.append(data)

  response = {
    "count": count,
    "data": datas
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # Shows the venue page with the given venue_id

  artist = Artist.query.filter_by(id=artist_id).all()[0]
  shows = Show.query.filter_by(artist_id=artist_id).all()
  current_time = datetime.datetime.now()

  past_shows = []
  upcoming_shows =[]

  # Check for shows with this artist whether they are in the past or in the future
  for show in shows:
    each_show = {
      "venue_id" : show.venue_id,
      "venue_name" : Venue.query.get(show.venue_id).name,
      "venue_image_link" : Venue.query.get(show.venue_id).image_link,
      "start_time" : show.start_time
    }

    if int(show.start_time[:4]) < int(str(current_time)[:4]):
      past_shows.append(each_show)
    elif int(show.start_time[:4]) > int(str(current_time)[:4]):
      upcoming_shows.append(each_show)
    else:
      if int(show.start_time[5:7]) < int(str(current_time)[5:7]):
        past_shows.append(each_show)
      elif int(show.start_time[5:7]) > int(str(current_time)[5:7]):
        upcoming_shows.append(each_show)
      else:
        if int(show.start_time[8:10]) > int(str(current_time)[8:10]):
          past_shows.append(each_show)
        elif int(show.start_time[8:10]) < int(str(current_time)[8:10]):
          upcoming_shows.append(each_show)
        else:
          if int(show.start_time[11:13]) < int(str(current_time)[11:13]):
            past_shows.append(each_show)
          elif int(show.start_time[11:13]) > int(str(current_time)[11:13]):
            upcoming_shows.append(each_show)
          else:
            if int(show.start_time[14:]) < int(str(current_time)[14:16]):
              past_shows.append(each_show)
            elif int(show.start_time[14:]) > int(str(current_time)[14:16]):
              upcoming_shows.append(each_show)
            else:
              past_shows.append(each_show)
      
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone =  request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website = request.form['website']
  seeking_venue = request.form['seeking_venue']
  seeking_description = request.form['seeking_description']

  # Ensure seeking_venue is Boolean
  if seeking_venue == 'True':
    seeking_venue = True
  else:
    seeking_venue = False
  
  validPhone = True
  if phone:
    validPhone = valid_phone(phone)

  if not validPhone:
    # Check if phone is valid
    flash('An error occurred. Invalid phone number!')
    return redirect(url_for('edit_artist', artist_id=artist_id))

  # Try to input data into database
  try:
    artist = Artist.query.get(artist_id)
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.facebook_link = facebook_link
    artist.image_link = image_link
    artist.website = website
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description

    db.session.commit()

    # On successful db insert, flash success
    flash('Artist ' + name + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + name + ' could not be edited.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  genres = request.form.getlist('genres')
  phone =  request.form['phone']
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website = request.form['website']
  seeking_talent = request.form['seeking_talent']
  seeking_description = request.form['seeking_description']

  # Ensure seeking_talent is Boolean
  if seeking_talent == 'True':
    seeking_talent = True
  else:
    seeking_talent = False

  validPhone = True
  if phone:
    validPhone = valid_phone(phone)

  if not validPhone:
    # Check if phone is valid
    flash('An error occurred. Invalid phone number!')
    return redirect(url_for('edit_venue', venue_id=venue_id))

  # Try input data into database
  try:
    venue = Venue.query.get(venue_id)
    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.image_link = image_link
    venue.website = website
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description

    db.session.commit()

    # On successful db insert, flash success
    flash('Venue ' + name + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be edited.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # Called upon submitting the new artist listing form
  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone =  request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website = request.form['website']
  seeking_venue = request.form['seeking_venue']
  seeking_description = request.form['seeking_description']

  # Ensure seeking_venue is Boolean
  if seeking_venue == 'True':
    seeking_venue = True
  else:
    seeking_venue = False

  exists = db.session.query(Artist.id).filter_by(name=name).scalar() is not None
  
  validPhone = True
  if phone:
    validPhone = valid_phone(phone)

  if exists:
    # Check if artist is already in database
    flash('An error occurred. Artist ' + name + ' already exists!.')
    return redirect(url_for('create_artist_form'))
  elif not validPhone:
    # Check if phone is valid
    flash('An error occurred. Invalid phone number!')
    return redirect(url_for('create_artist_form'))
  else:
    # Try to input data into database
    try:
      artist = Artist(
        name=name,
        city=city,
        state=state,
        phone=phone,
        genres=genres,
        facebook_link=facebook_link,
        image_link=image_link,
        website=website,
        seeking_venue=seeking_venue,
        seeking_description=seeking_description
      )

      db.session.add(artist)
      db.session.commit()

      # On successful db insert, flash success
      flash('Artist ' + name + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + name + ' could not be listed.')
      print(sys.exc_info())
    finally:
      db.session.close()
  
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.all()
  datas=[]

  for show in shows:
    data = {
      "venue_id" : show.venue_id,
      "venue_name" : Venue.query.get(show.venue_id).name,
      "artist_id" : show.artist_id,
      "artist_name" : Artist.query.get(show.artist_id).name,
      "artist_image_link" : Artist.query.get(show.artist_id).image_link,
      "start_time" : show.start_time
    }
    datas.append(data)

  return render_template('pages/shows.html', shows=datas)

@app.route('/shows/create')
def create_shows():
  # Renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # Called to create new shows in the db, upon submitting new show listing form

  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  valid_time = True

  # Check if IDs are valid
  try:
    artist_int = int(artist_id)
    venue_int = int(venue_id)
  except ValueError:
    flash('An error occured. Invalid ID(s)!')
    return redirect(url_for('create_shows'))

  # Check if IDs are missing
  if not artist_id or not venue_id or not start_time:
    flash('An error occured. Missing field(s)!')
    return redirect(url_for('create_shows'))

  # Check if start time is valid
  if len(start_time) == 16:
    for i in range(0, 16):
      if i != 4 and i != 7 and i != 10 and i != 13:
        try:
          val = int(start_time[i])
        except ValueError:
          valid_time = False
      elif (i == 4 or i == 7) and start_time[i] != '-':
        valid_time = False
      elif (i == 10) and start_time[i] != ' ':
        valid_time = False
      elif (i == 13) and start_time[i] != ':':
        valid_time = False
  else:
    valid_time = False

  if not valid_time:
    flash('An error occured. Invalid Start Time!')
    return redirect(url_for('create_shows'))

  # Check if artist and venue exist in database
  artist_exists = db.session.query(Artist.id).filter_by(id=artist_id).scalar() is not None
  venue_exists = db.session.query(Venue.id).filter_by(id=venue_id).scalar() is not None
    
  if not artist_exists and not venue_exists:
    flash('An error occurred. Artist ID ' + artist_id + ' and Venue ID ' + venue_id + ' do not exist' )
    return redirect(url_for('create_shows'))
  elif not artist_exists:
    flash('An error occurred. Artist ID ' + artist_id + ' does not exists!')
    return redirect(url_for('create_shows'))
  elif not venue_exists:
    flash('An error occurred. Venue ID ' + venue_id + ' does not exists!')
    return redirect(url_for('create_shows'))

  # Check if an artist or a venue is having another show at the given time
  same_start_times = db.session.query(Show).filter_by(start_time=start_time).all()
  for show_same_time in same_start_times:
    if show_same_time.artist_id == int(artist_id):
      flash('Artist with ID ' + artist_id + ' is not available at time ' + start_time)
      return redirect(url_for('create_shows'))
    if show_same_time.venue_id == int(venue_id):
      flash('Venue with ID ' + venue_id + ' is not available at time ' + start_time)
      return redirect(url_for('create_shows'))

  # Try to input data into database
  try:
    show = Show(
      venue_id = venue_id,
      artist_id = artist_id,
      start_time = start_time,
    )

    db.session.add(show)
    db.session.commit()

    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

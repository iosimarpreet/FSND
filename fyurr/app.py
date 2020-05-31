# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import datetime
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# flask migrate set up
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


venue_shows = db.Table(
    'venue_shows',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id')),
    db.Column('show_id', db.Integer, db.ForeignKey('shows.id'))
)

artist_shows = db.Table(
    'artist_shows',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id')),
    db.Column('show_id', db.Integer, db.ForeignKey('shows.id'))
)


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(1000), default=f"Looking for new artists!")
    shows = db.relationship('Show', secondary=venue_shows, lazy='subquery', backref=db.backref('venues', lazy=True))
    genre = db.Column(db.String)


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(1000), default=f"Looking to perform at a show!")
    shows = db.relationship('Show', secondary=artist_shows, lazy='subquery', backref=db.backref('artists', lazy=True))
    genre = db.Column(db.String)


class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    venue = db.relationship("Venue", backref=db.backref("venues", uselist=False))
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
    artist = db.relationship("Artist", backref=db.backref("artists  ", uselist=False))
    start_time = db.Column(db.DateTime)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    all_areas_and_venues = [{"area": venue.city + venue.state, "venue": venue} for venue in Venue.query.all()]

    venues_by_area = {}

    for venue in all_areas_and_venues:
        print(venue.keys())
        if venue["area"] in venues_by_area.keys():
            venues_by_area[venue.area].append(venue.venue)
        else:
            venues_by_area[venue["area"]] = [venue["venue"]]

    data = [{"city": venues_by_area[area][0].city,
             "state": venues_by_area[area][0].state,
             "venues": [{"id": venue.id,
                         "name": venue.name,
                         "num_upcoming_shows": len(venue.shows)}
                        for venue in venues_by_area[area]]}
            for area in venues_by_area]

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term', '')
    search = f"%{search_term}%"
    venues_found = Venue.query.filter(Venue.name.like(search)).all()
    response = {
        "count": len(venues_found),
        "data": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(venue.shows),
        }
            for venue in venues_found]
    }
    return render_template('pages/search_venues.html', results=response,
                           search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    current_venue = Venue.query.get(venue_id)
    past_shows = [{"artist_id": show.artist_id,
                   "artist_name": show.artist.name,
                   "artist_image_link": show.artist.image_link,
                   "start_time": str(show.start_time)}
                  for show in current_venue.shows if show.start_time < datetime.now()]
    upcoming_shows = [{"artist_id": show.artist_id,
                       "artist_name": show.artist.name,
                       "artist_image_link": show.artist.image_link,
                       "start_time": str(show.start_time)}
                      for show in current_venue.shows if show.start_time > datetime.now()]

    data = {
        "id": current_venue.id,
        "name": current_venue.name,
        "genres": [current_venue.genre],
        "address": current_venue.address,
        "city": current_venue.city,
        "state": current_venue.state,
        "phone": current_venue.state,
        "website": current_venue.website,
        "facebook_link": current_venue.facebook_link,
        "seeking_talent": current_venue.seeking_talent,
        "seeking_description": current_venue.seeking_description,
        "image_link": current_venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
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
    form = request.form
    error = False
    try:
        new_venue = Venue(name=form["name"],
                          city=form["city"],
                          state=form["state"],
                          address=form["address"],
                          phone=form["phone"],
                          website=form["website"],
                          image_link=form["image_link"],
                          facebook_link=form["facebook_link"],
                          seeking_talent=form["seeking_talent"] == "True",
                          seeking_description=form["seeking_description"],
                          genre=form["genre"])
        db.session.add(new_venue)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        flash('Venue ' + Venue.query.filter_by(name=form["name"],
                                               city=form["city"]).first().name + ' was successfully listed!')
    else:
        flash('ERROR: Venue ' + request.form['name'] + ' was was not listed :(!')
    return render_template('pages/home.html')


# edit venue

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    current_venue = Venue.query.get(venue_id)
    venue = {
        "id": current_venue.id,
        "name": current_venue.name,
        "genres": [current_venue.genre],
        "address": current_venue.address,
        "city": current_venue.city,
        "state": current_venue.state,
        "phone": current_venue.phone,
        "website": current_venue.website,
        "facebook_link": current_venue.facebook_link,
        "seeking_talent": current_venue.seeking_talent,
        "seeking_description": current_venue.seeking_description,
        "image_link": current_venue.image_link
    }
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = request.form
    error = False
    try:
        current_venue = Venue.query.get(venue_id)
        current_venue.name = form["name"]
        current_venue.city = form["city"]
        current_venue.state = form["state"]
        current_venue.address = form["address"]
        current_venue.phone = form["phone"]
        current_venue.website = form["website"]
        current_venue.image_link = form["image_link"]
        current_venue.facebook_link = form["facebook_link"]
        current_venue.seeking_talent = form["seeking_talent"] == "True"
        current_venue.seeking_description = form["seeking_description"]
        current_venue.genre = form["genre"]
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        flash('Venue was successfully edited!')
    else:
        flash('ERROR: Venue ' + str(venue_id) + ' was was not edited :(!')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  delete venue

@app.route('/venues/delete/<venue_id>')
def delete_venue(venue_id):
    error = False
    try:
        current_venue = Venue.query.get(venue_id)
        db.session.delete(current_venue)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        flash('Venue was successfully deleted!')
    else:
        flash('ERROR: Venue ' + str(venue_id) + ' was was not deleted :(!')
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = [{"id": artist.id, "name": artist.name} for artist in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term', '')
    search = f"%{search_term}%"
    artists_found = Artist.query.filter(Artist.name.like(search)).all()
    response = {
        "count": len(artists_found),
        "data": [{
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(artist.shows),
        }
            for artist in artists_found]
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    current_artist = Artist.query.get(artist_id)
    past_shows = [{"artist_id": show.artist_id,
                   "artist_name": show.artist.name,
                   "artist_image_link": show.artist.image_link,
                   "start_time": str(show.start_time)}
                  for show in current_artist.shows if show.start_time < datetime.now()]
    upcoming_shows = [{"artist_id": show.artist_id,
                       "artist_name": show.artist.name,
                       "artist_image_link": show.artist.image_link,
                       "start_time": str(show.start_time)}
                      for show in current_artist.shows if show.start_time > datetime.now()]
    data = {
        "id": current_artist.id,
        "name": current_artist.name,
        "genres": [current_artist.genre],
        "city": current_artist.city,
        "state": current_artist.state,
        "phone": current_artist.phone,
        "website": current_artist.website,
        "facebook_link": current_artist.facebook_link,
        "seeking_venue": current_artist.seeking_venue,
        "seeking_description": current_artist.seeking_description,
        "image_link": current_artist.image_link,
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
    current_artist = Artist.query.get(artist_id)
    artist = {
        "id": current_artist.id,
        "name": current_artist.name,
        "genres": [current_artist.genre],
        "city": current_artist.city,
        "state": current_artist.state,
        "phone": current_artist.phone,
        "website": current_artist.website,
        "facebook_link": current_artist.facebook_link,
        "seeking_venue": current_artist.seeking_venue,
        "seeking_description": current_artist.seeking_description,
        "image_link": current_artist.image_link
    }
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = request.form
    error = False
    try:
        current_artist = Artist.query.get(artist_id)
        current_artist.name = form["name"]
        current_artist.city = form["city"]
        current_artist.state = form["state"]
        current_artist.phone = form["phone"]
        current_artist.website = form["website"]
        current_artist.image_link = form["image_link"]
        current_artist.facebook_link = form["facebook_link"]
        current_artist.seeking_venue = form["seeking_venue"] == "True"
        current_artist.seeking_description = form["seeking_description"]
        current_artist.genre = form["genre"]
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        flash('Artist was successfully edited!')
    else:
        flash('ERROR: Artist ' + str(artist_id) + ' was was not edited :(!')
    return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = request.form
    error = False
    try:
        new_artist = Artist(name=form["name"],
                            city=form["city"],
                            state=form["state"],
                            phone=form["phone"],
                            website=form["website"],
                            image_link=form["image_link"],
                            facebook_link=form["facebook_link"],
                            seeking_venue=form["seeking_venue"] == "True",
                            seeking_description=form["seeking_description"],
                            genre=form["genre"])
        db.session.add(new_artist)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        flash('Artist ' + Artist.query.filter_by(name=form["name"],
                                                 city=form["city"]).first().name + ' was successfully listed!')
    else:
        flash('ERROR: Artist ' + request.form['name'] + ' was was not listed :(!')
    return render_template('pages/home.html')


#  delete venue


@app.route('/artists/delete/<artist_id>')
def delete_artist(artist_id):
    error = False
    try:
        current_artist = Artist.query.get(artist_id)
        db.session.delete(current_artist)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        flash('Artist was successfully deleted!')
    else:
        flash('ERROR: Artist ' + str(artist_id) + ' was was not deleted :(!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows

    all_shows = Show.query.all()

    data = [{"venue_id": show.venue_id,
             "venue_name": show.venue.name,
             "artist_id": show.artist_id,
             "artist_name": show.artist.name,
             "artist_image_link": show.artist.image_link,
             "start_time": str(show.start_time)}
            for show in all_shows]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = request.form
    error = False
    try:
        new_show = Show(artist_id=form["artist_id"],
                        venue_id=form["venue_id"],
                        start_time=form["start_time"])
        db.session.add(new_show)

        current_artist = Artist.query.get(form["artist_id"])
        current_artist.shows.append(new_show)
        current_venue = Venue.query.get(form["venue_id"])
        current_venue.shows.append(new_show)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
        error = True
    finally:
        db.session.close()

    if not error:
        flash('Show was successfully listed!')
    else:
        flash('ERROR: Show was was not listed :(!')
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
    # manager.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

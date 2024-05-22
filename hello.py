from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Optional
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text

#Create a Flask Instance
app = Flask(__name__)
#Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/fostats'
#Secret Key
app.config['SECRET_KEY'] = "F0stats!!"
#Initialize the database
db = SQLAlchemy(app)

#Create Tournament Model
class Tournament(db.Model):
 	tournament_id = db.Column(db.Integer, primary_key=True)
 	tournament_name = db.Column(db.String(200), nullable=False, unique=True)
 	game = db.relationship('Game', back_populates='tournament')

 	#Create A String
 	def __repr__(self):
 		return '<Tournament %r>' % self.tournament_name

# Create Game Model
class Game(db.Model):
    game_id = db.Column(db.Integer, primary_key=True)
    game_venue = db.Column(db.String(200), nullable=True, unique=False)
    game_date = db.Column(db.Date, nullable=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.tournament_id'), nullable=False)
    tournament = db.relationship('Tournament', back_populates='game')
    
    home_team = db.Column(db.Integer, db.ForeignKey('team.team_id'), nullable=False)
    away_team = db.Column(db.Integer, db.ForeignKey('team.team_id'), nullable=False)
    
    hometeam = db.relationship('Team', foreign_keys=[home_team], back_populates='home_games')
    awayteam = db.relationship('Team', foreign_keys=[away_team], back_populates='away_games')

    home_coach = db.Column(db.Integer, db.ForeignKey('personell.personell_id'), nullable=False)
    away_coach = db.Column(db.Integer, db.ForeignKey('personell.personell_id'), nullable=False)
    
    homecoach = db.relationship('Personell', foreign_keys=[home_coach], back_populates='home_c')
    awaycoach = db.relationship('Personell', foreign_keys=[away_coach], back_populates='away_c')
    
    # Create a String
    def __repr__(self):
        return '<Game %r>' % self.game_venue

#Create Team Model
class Team(db.Model):
 	team_id = db.Column(db.Integer, primary_key=True)
 	team_name = db.Column(db.String(200), nullable=False, unique=True)
 	team_type = db.Column(db.String(200), nullable=False)
 	nickname = db.Column(db.String(200), nullable=True)
 	personnel = db.relationship('Personell', back_populates='team')
 	
 	home_games = db.relationship('Game', foreign_keys=[Game.home_team], back_populates='hometeam')
 	away_games = db.relationship('Game', foreign_keys=[Game.away_team], back_populates='awayteam')
 	
 	#Create A String
 	def __repr__(self):
 		return '<Team %r>' % self.team_name

#Create Personell Model
class Personell(db.Model):
 	personell_id = db.Column(db.Integer, primary_key=True)
 	personell_name = db.Column(db.String(200), nullable=False, unique=True)
 	personell_type = db.Column(db.Enum('Player', 'Coach'), nullable=False)
 	DOB = db.Column(db.Date, nullable=True)
 	team_id = db.Column(db.Integer, db.ForeignKey('team.team_id'), nullable=False)
 	team = db.relationship('Team', back_populates='personnel')
 	home_c = db.relationship('Game', foreign_keys=[Game.home_coach], back_populates='homecoach')
 	away_c = db.relationship('Game', foreign_keys=[Game.away_coach], back_populates='awaycoach')
 	

 	#Create A String
 	def __repr__(self):
 		return '<Personell %r>' % self.personell_name

#Create Action Model
class Actions(db.Model):
 	action_id = db.Column(db.Integer, primary_key=True)
 	action_type = db.Column(db.String(255), nullable=False, unique=True)

 	#Create A String
 	def __repr__(self):
 		return '<Action %r>' % self.action_type

#Create Tournament Form Class
class TournamentForm(FlaskForm):
	tournament_name = StringField("Tournament Name?", validators=[DataRequired()])
	submit = SubmitField("Submit")

#Create Team Form Class
class TeamForm(FlaskForm):
	team_name = StringField("Team Name", validators=[DataRequired()])
	team_type = SelectField("Team Type", validate_choice=True)
	nickname = StringField("Team NickName")
	submit = SubmitField("Submit")

# Create Personell Form Class
class PersonellForm(FlaskForm):
    personell_name = StringField("Personell Name", validators=[DataRequired()])
    personell_type = SelectField("Select Personell Type", validate_choice=True)
    DOB = DateField("Choose Date of Birth", format='%Y-%m-%d', validators=[Optional()])
    personell_team = SelectField("Select Team", validate_choice=True)
    submit = SubmitField("Submit")

#Create Action Form Class
class ActionForm(FlaskForm):
	action_type = StringField("Action Name", validators=[DataRequired()])
	submit = SubmitField("Submit")

#Create Game Form Class
class GameForm(FlaskForm):
	game_venue = StringField("Game Venue", validators=[DataRequired()])
	game_date = DateField("Game Date", format='%Y-%m-%d', validators=[Optional()])
	game_tournament = SelectField("Select Tournament", validate_choice=True)
	home_team = SelectField("Select Home Team", validate_choice=True)
	away_team = SelectField("Select Away Team", validate_choice=True)
	home_coach = SelectField("Select Home Team Coach", validate_choice=True)
	away_coach = SelectField("Select Away Team Coach", validate_choice=True)
	submit = SubmitField("Submit")

#Get ENUM values from table.column
def get_enum_values(table, column):
    enum_type_query = text(f"SHOW COLUMNS FROM {table} WHERE Field = '{column}'")
    result = db.session.execute(enum_type_query).fetchone()
    # The result is a tuple, and the 'Type' is the second element
    enum_values = result[1][5:-1].replace("'", "").split(',')
    return [(value, value) for value in enum_values]

#Create a route decorator
@app.route('/')

def index():
	return render_template('index.html')

#Create Tournament Page
@app.route('/tournament', methods=['GET', 'POST'])

def tournament():
	tournament_name = None
	form  = TournamentForm()
	#Validate Form
	if form.validate_on_submit():
		tourna = Tournament.query.filter_by(tournament_name=form.tournament_name.data).first()
		if tourna is None:
			tourna = Tournament(tournament_name=form.tournament_name.data)
			db.session.add(tourna)
			db.session.commit()
		tournament_name = form.tournament_name.data
		form.tournament_name.data = ''
		flash("Tournament Created Successfully")
	our_tournaments = Tournament.query
	return render_template('tournament.html',
		tournament_name = tournament_name,
		form = form,
		our_tournaments=our_tournaments
		)

#Create Team Page
@app.route('/team', methods=['GET', 'POST'])

def team():
	team_name = None
	team_type = None
	nickname = None
	form  = TeamForm()
	
	# Set choices for team_type field
	form.team_type.choices = get_enum_values('team', 'team_type')

	#Validate Form
	if form.validate_on_submit():
		team = Team.query.filter_by(team_name=form.team_name.data).first()
		if team is None:
			team = Team(
				team_name=form.team_name.data,
				team_type=form.team_type.data,
				nickname=form.nickname.data
				)
			db.session.add(team)
			db.session.commit()
			flash("Team Created Successfully")
		else:
			flash("Team already exists")

		team_name = form.team_name.data
		team_type = form.team_type.data
		nickname = form.nickname.data

		# Clear the form fields
		form.team_name.data = ''
		form.team_type.data = ''
		form.nickname.data = ''

	our_teams = Team.query
	return render_template('team.html',
		team_name=team_name,
		team_type=team_type,
		nickname=nickname,
		form=form,
		our_teams=our_teams
		)

#Create Personell Page
@app.route('/personell', methods=['GET', 'POST'])

def personell():
	personell_name = None
	personell_type = None
	DOB = None
	personell_team = None
	form  = PersonellForm()

	# Set choices for personell_type field
	form.personell_type.choices = get_enum_values('personell', 'personell_type')
	# Set choices for personell_team field
	form.personell_team.choices = [(team.team_id, team.team_name) for team in Team.query.all()]

	#Validate Form
	if form.validate_on_submit():
		person = Personell.query.filter_by(personell_name=form.personell_name.data).first()

		if person is None:
			person = Personell(
			personell_name=form.personell_name.data,
			personell_type=form.personell_type.data,
			DOB=form.DOB.data if form.DOB.data else None,
			team_id=form.personell_team.data
			)
		db.session.add(person)
		db.session.commit()

		personell_name=form.personell_name.data
		personell_type=form.personell_type.data
		DOB=form.DOB.data
		personell_team=form.personell_team.data

		# Clear the form fields
		form.personell_name.data = ''
		form.personell_type.data = ''
		form.DOB.data = None
		form.personell_team.data = ''
		flash("Personell Created Successfully")

	our_personell = Personell.query
	return render_template('personell.html',
		personell_name=personell_name,
		personell_type=personell_type,
		DOB=DOB,
		personell_team=personell_team,
		form=form,
		our_personell=our_personell
		)

#Create Action Page
@app.route('/action', methods=['GET', 'POST'])

def action():
	action_type = None
	form  = ActionForm()
	#Validate Form
	if form.validate_on_submit():
		actions = Actions.query.filter_by(action_type=form.action_type.data).first()
		if actions is None:
			actions = Actions(action_type=form.action_type.data)
			db.session.add(actions)
			db.session.commit()
		action_type = form.action_type.data
		form.action_type.data = ''
		flash("Action Created Successfully")
	our_actions = Actions.query
	return render_template('action.html',
		action_type = action_type,
		form = form,
		our_actions=our_actions
		)

#Create Game Page
@app.route('/game', methods=['GET', 'POST'])

def game():
	game_venue = None
	game_date = None
	game_tournament = None
	home_team = None
	away_team = None
	home_coach = None
	away_coach = None
	form  = GameForm()

	# Set choices for game_tournament field
	form.game_tournament.choices = [(tournament.tournament_id, tournament.tournament_name) for tournament in Tournament.query.all()]
	# Set choices for home_team/away_team field
	form.home_team.choices = [(hometeam.team_id, hometeam.team_name) for hometeam in Team.query.all()]
	form.away_team.choices = [(awayteam.team_id, awayteam.team_name) for awayteam in Team.query.all()]

	form.home_coach.choices = [(homecoach.personell_id, homecoach.personell_name) for homecoach in Personell.query.all()]
	form.away_coach.choices = [(awaycoach.personell_id, awaycoach.personell_name) for awaycoach in Personell.query.all()]

	#Validate Form
	if form.validate_on_submit():
		match_game = Game(
			game_venue=form.game_venue.data,
			game_date=form.game_date.data if form.game_date.data else None,
			tournament_id=form.game_tournament.data,
			home_team=form.home_team.data,
			away_team=form.away_team.data,
			home_coach=form.home_coach.data,
			away_coach=form.away_coach.data
			)
		db.session.add(match_game)
		db.session.commit()

		# Clear the form fields
		form.game_venue.data = ''
		form.game_date.data = ''
		form.game_tournament.data = ''
		form.home_team.data = ''
		form.away_team.data = ''
		form.home_coach.data = ''
		form.away_coach.data = ''
		flash("Game Created Successfully")
	
	our_games = Game.query
	return render_template('game.html',
		game_venue = game_venue,
		game_date = game_date,
		game_tournament = game_tournament,
		home_team = home_team,
		away_team = away_team,
		home_coach = home_coach,
		away_coach = away_coach,
		form=form,
		our_games = our_games
		)
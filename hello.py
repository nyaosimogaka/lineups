from flask import Flask, render_template

#Create Flask Instance
app = Flask(__name__)

#Create a route decorator
@app.route('/')

def index():
	return render_template('index.html')
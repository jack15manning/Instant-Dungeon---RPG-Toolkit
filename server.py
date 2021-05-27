from flask import Flask, render_template, flash, request
from wtforms import Form, IntegerField, validators, SubmitField, SelectField
import pdfkit
import dungeonGeneration
import copy

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

latestImage = 'static/latestDungeon.PNG'

class ReusableForm(Form):
    size = SelectField(u'Size', choices=[('Tiny'), ('Small'), ('Medium'), ('Large')])
    shape = SelectField(u'Shape', choices=[('Square'), ('Rectangle')])
    corridorAlgorithm = SelectField(u'CorridorAlgorithm', choices=[('BSP'), ('Drunkard')])
    Seed = IntegerField('Seed', validators=[validators.required()])
    PopSeed = IntegerField('PopSeed', validators=[validators.required()])
    theme = SelectField(u'Theme')
    partySize = IntegerField('PartySize', validators=[validators.required()])
    partyLevel = IntegerField('PartyLevel', validators=[validators.required()])
    density = SelectField(u'Density')
    tileset = SelectField(u'Tileset')
    
class RepopulateForm(Form):
    theme = SelectField(u'Theme')
    partySize = IntegerField('PartySize', validators=[validators.required()])
    partyLevel = IntegerField('PartyLevel', validators=[validators.required()])
    density = SelectField(u'Density')
        
#Home Page  
@app.route("/", methods=['GET', 'POST'])
def home():
    form = ReusableForm(request.form)
    
    if request.method == 'POST':
        global size
        size = request.form['Size']
        print("Size: {0}".format(size))#
        
        global shape
        shape = request.form['Shape']
        print("Shape: {0}".format(shape))
        
        global corridorAlgorithm
        corridorAlgorithm = request.form['CorridorAlgorithm']
        print("Corridor Algorithm: {0}".format(corridorAlgorithm))
        
        global Seed
        Seed = int(request.form['Seed'])
        if Seed == 0:
            print("No Dungeon Seed")
        else:
            print("Dungeon Seed: {0:0=8d}".format(Seed))
            
        PopSeed = int(request.form['PopSeed'])
        if PopSeed == 0:
            print("No Population Seed")
        else:
            print("Population Seed: {0:0=4d}".format(PopSeed))
        
        theme = request.form['Theme']
        print("Dungeon Theme: {0}".format(theme))
        
        partySize = int(request.form['PartySize'])
        if partySize == 0:
            print("Random Party Size")
        else:
            print("Party Size: {0}".format(partySize))
            
        partyLevel = int(request.form['PartyLevel'])
        if partyLevel == 0:
            print("Random Party Level")
        else:
            print("Party Average Level: {0}".format(partyLevel))
        
        density = request.form['Density']
        print("Density: {0}".format(density))
        
        global tileset
        tileset = request.form['Tileset']
        print("Tileset: {0}".format(tileset))
        print(Seed)
        enc, seed1, seed2 , partySize, partyLevel= dungeonGeneration.main(size, shape, corridorAlgorithm, Seed, PopSeed, theme, partySize, partyLevel, density, tileset)
        DungeonSeed = "{0:0=8d}".format(seed1)
        PopulationSeed = "{0:0=4d}".format(seed2)
        Seed = seed1
        return render_template('dungeon.html', user_image = latestImage, data = enc, dunSeed = DungeonSeed, popSeed = PopulationSeed, partySize = partySize, partyLevel = partyLevel)
    return render_template('home.html', form=form)

#Repopulate function  
@app.route("/repop", methods=['GET', 'POST'])
def repopulate():
    form = RepopulateForm(request.form)
    if request.method == 'POST':
        
        theme = request.form['Theme']
        print("Dungeon Theme: {0}".format(theme))
        
        partySize = int(request.form['PartySize'])
        if partySize == 0:
            print("Random Party Size")
        else:
            print("Party Size: {0}".format(partySize))
            
        partyLevel = int(request.form['PartyLevel'])
        if partyLevel == 0:
            print("Random Party Level")
        else:
            print("Party Average Level: {0}".format(partyLevel))
        
        density = request.form['Density']
        print("Density: {0}".format(density))
        print(Seed)
        PopSeed = 0
        enc, seed1, seed2, partySize, partyLevel= dungeonGeneration.main(size, shape, corridorAlgorithm, Seed, PopSeed, theme, partySize, partyLevel, density, tileset)
        DungeonSeed = "{0:0=8d}".format(seed1)
        PopulationSeed = "{0:0=4d}".format(seed2)
        return render_template('dungeon.html', user_image = latestImage, data = enc, dunSeed = DungeonSeed, popSeed = PopulationSeed, partySize = partySize, partyLevel = partyLevel)
    return render_template('home.html', form=form)
    
#About page 
@app.route("/about", methods=['GET','POST'])
def about():
    return render_template('about.html')
#Contact page    
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response
   
if __name__ == "__main__":
    app.run()

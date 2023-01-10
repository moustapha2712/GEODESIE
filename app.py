#!/usr/bin/env python3
# -*- coding: UTF-8 -*-''
# -*- coding : Latin-1 -*

import os
from flask import Flask
from werkzeug.routing import Map, Rule, RequestRedirect
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import Integer, Text, String, DateTime, Float
import folium
import geopandas as gpd


app = Flask(__name__)
app.secret_key = "9d263e09465118fcc3b288369ed53396922588fc3e8f466845ef8ab6a00cef25"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///GEOdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


engine = create_engine('sqlite:///GEOdata.db')  # db is the one from the question

with app.app_context():
 #db.drop_all()
 #db.create_all()


 class point_Géodésique(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     Nom = db.Column(db.String(100), nullable=False)
     Localités = db.Column(db.String(100), nullable=False)
     X = db.Column(db.Float, nullable=False)
     Y = db.Column(db.Float, nullable=False)
     Altitude = db.Column(db.Float, nullable=True)
     Ordre = db.Column(db.String(50), nullable=True)
     H_Ellipsoidale = db.Column(db.Float, nullable=False)
     Etat = db.Column(db.String, nullable=True)
     Observations = db.Column(db.String, nullable=True)
     Année_de_mesure = db.Column(db.Integer)
     Référentiel = db.Column(db.String, nullable=True)
     Epoque = db.Column(db.Float, nullable=True)

     def __repr__(self):
         return f'<point_Géodésique {self.Nom}>'



 engine = create_engine('sqlite:///GEOdata.db')


 jobs_df1 = pd.read_excel("Points_Géodésiques_Sénégal_m0.xlsx")
 Pts_GEO = jobs_df1.copy()
 #print(jobs_df1)
 #print(jobs_df1.info())
 #jobs_df1.head()
 #Insert to DB
 Pts_GEO.to_sql(
    'point_Géodésique',
    engine,
    if_exists='replace',
    index=False,
    chunksize=500,
    dtype={
        "id": Integer,
        "Nom": String(100),
        "Localités": String(100),
        "X":  Float,
        "Y": Float,
        "Altitude": Float,
        "Ordre": String(50),
        "H_Ellipsoidale": Float,
        "Etat": String,
        "Observations": String,
        "Année_de_mesure": String,
        "Référentiel": DateTime,
        "Epoque":  Float,
    }
)

# (B) HELPER - GET ALL POİNTS FROM DATABASE
def getpoints():
  DBFILE = "GEOdata.db"
  conn = sqlite3.connect(DBFILE)
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM `point_Géodésique`")
  results = cursor.fetchall()
  conn.close()
  return results


@app.route('/') #@login_required
def home():
  return render_template("home.html")

#gdf = gpd.read_file('Points_Géodésiques_Sénégal_m1.geojson')
gdf= gpd.read_file('Points_Géodésiques_Sénégal_m0EXPORT1.shp')
BBox = [(11.797560835339684,-18.678549810014765),(17.170174257102456,-10.101376646393428)]
m = folium.Map(location=[-17.44, 14.721], zoom_start=11, control_scale=True)
m.fit_bounds(BBox)



# Add custom base maps to folium
basemaps = {
    'Google Maps': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Maps',
        overlay = True,
        control = True
    ),
    'Google Satellite': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True
    ),
    'Google Terrain': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Terrain',
        overlay = True,
        control = True
    ),
    'Google Satellite Hybrid': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True
    ),
    'Esri Satellite': folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = True,
        control = True
    )
}


# import plugins
from folium import plugins

# Add a layer control panel to the map.
#m.add_child(folium.LayerControl())

# fullscreen
plugins.Fullscreen().add_to(m)

# GPS
plugins.LocateControl().add_to(m)

# mouse position
fmtr = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
plugins.MousePosition(position='topright', separator=' | ', prefix="Mouse:", lat_formatter=fmtr,
                      lng_formatter=fmtr).add_to(m)

# Add the draw
plugins.Draw(export=True, filename='data.geojson', position='topleft', draw_options=None, edit_options=None).add_to(m)

# Add measure tool
#plugins.MeasureControl(position='topright', primary_length_unit='meters', secondary_length_unit='miles',
                       #primary_area_unit='sqmeters', secondary_area_unit='acres').add_to(m)


# create a layer on the map object
Couche1 = folium.FeatureGroup(name=" Réseau géodésique du Sénégal").add_to(m)


basemaps['Google Satellite Hybrid'].add_to(m)# Add custom basemaps
basemaps['Google Maps'].add_to(m)
basemaps['Google Terrain'].add_to(m)


def style_function(feature):
    Ordre = feature['properties']['Ordre']
    return {
        'fillOpacity': 0.5,
        'weight': 0.5,
        'fillColor': 'green' if Ordre == '1er ordre' \
               else 'blue'if Ordre == '2e ordre' \
               else 'orange' if Ordre == 'RBUS' \
               else 'pink' if Ordre == 'BD_2020' \
               else 'purple' if Ordre == 'JICA' \
               else 'red'
    }


#pd.set_option('display.max_columns', 20)
#pd.set_option('display.width', 1000)
#print(gdf)


gjson = folium.GeoJson(gdf,
               marker=folium.CircleMarker(
                   radius=5,
                   fill_color="white",
                   fill_opacity=0.4,
                   color="black",
                   weight=1),
               style_function=style_function,
               tooltip=folium.GeoJsonTooltip(fields=["Nom", "X", "Y","Altitude","Ordre","H_Ellipsoi"]),
               highlight_function=lambda x: {"fillOpacity": 0.8},
               popup=folium.GeoJsonPopup(fields=["Nom","Localités"]),
               zoom_on_click=True).add_to(Couche1)

from folium.plugins import Search
Bornesearch = Search(
    search_zoom=20,
    layer=Couche1,
    geom_type="Point",
    placeholder="Trouver mon point",
    collapsed=True,
    search_label="Nom",
).add_to(m)

######################

######################

import folium
from geopy.geocoders import GeoNames
gn = GeoNames(username='[ FALL_DTGC ]')

#gdf = gdf.to_json()
# create a layer on the map object
#gdf = gdf.to_json()

from branca.element import Template, MacroElement

template = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>jQuery UI Draggable - Default functionality</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            right: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>


<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>

<div class='legend-title'>Legend (Réseau Géodésique Sénégal)</div>
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background:green;opacity:0.7;'></span>1er ordre</li>
    <li><span style='background:blue;opacity:0.7;'></span>2e ordre</li>
    <li><span style='background:orange;opacity:0.7;'></span>Réseau de Référence Urbain du Sénégal</li>
	<li><span style='background:pink;opacity:0.7;'></span>BD_2020</li>
	<li><span style='background:purple;opacity:0.7;'></span>JICA</li>

  </ul>
</div>
</div>

</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""

macro = MacroElement()
macro._template = Template(template)

m.get_root().add_child(macro)

title_html = '''
             <h3 align="center" style="font-size:20px"><b>Carte du Réseau Géodésique du Sénégal</b></h3>
             
             '''
m.get_root().html.add_child(folium.Element(title_html))

############

from folium.plugins import Geocoder
#Add search bar
Geocoder().add_to(m)

folium.LayerControl().add_to(m)

m.save('index.html')

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/Plateforme_GEODESIE")
def Plateforme_GEODESIE():
  # (C1) GET ALL POİNTS
  points = getpoints()
  # (C2) RENDER HTML PAGE
  return render_template("Plateforme_GEODESIE.html", points=points)


# flask app to display pdf on the browser
from flask import Flask, send_from_directory
import os


from flask import render_template, Blueprint
from flask import send_from_directory
import os

routes = Blueprint('routes', __name__)

@app.route('/downloads/Contenu_Portail')
def Contenu_Portail():
    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + '/static/files/'
    return send_from_directory(filepath, 'ModeleContenuPortailGéodésiqueNational.pdf')

utilisateurs = [
     {"nom": "admin", "mdp": "1234"},
     {"nom": "marie", "mdp": "nsi"},
     {"nom": "paul", "mdp": "azerty"},
     {"nom": "moustapha", "mdp": "salah129"}
 ]


def recherche_utilisateur(nom_utilisateur, mot_de_passe):
     for utilisateur in utilisateurs:
         if utilisateur['nom'] == nom_utilisateur and utilisateur['mdp'] == mot_de_passe:
             return utilisateur
     return None


@app.route("/login", methods=["POST", "GET"])
def login():
     if request.method == "POST":
         donnees = request.form
         nom = donnees.get('nom')
         mdp = donnees.get('mdp')

         utilisateur = recherche_utilisateur(nom, mdp)

         if utilisateur is not None:
             print("utilisateur trouvé")
             session['nom_utilisateur'] = utilisateur['nom']
             print(session)
             return redirect(url_for('home'))
         else:
             print("utilisateur inconnu")
             return redirect(request.url)
     else:
         print(session)
         if 'nom_utilisateur' in session:
             return redirect(url_for('home'))
         return render_template("login.html")


@app.route('/logout')
def logout():
     print(session)
     session.pop('nom_utilisateur', None)
     print(session)
     return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
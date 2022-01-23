import requests
import pandas as pd
import numpy as np
import psycopg2
import sqlalchemy
import csv
import time
from decimal import Decimal
from flask import Flask, render_template, redirect
from flask import Flask, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask import Response
from flask import request
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, session
from sqlalchemy import create_engine, func
from sqlalchemy_utils import database_exists, create_database
from flask import Flask, jsonify

password = 1234
states = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','DC','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']
states_abbrev = ['AL','AK','AZ','AR','CA','CO','CT','DE','DC','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
df_columns = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','District of Columbia','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{password}@localhost:5432/project_3'
sql = SQLAlchemy(app)

# Creating Engine
engine = create_engine(f"postgresql://postgres:{password}@localhost:5432/project_3")

# reflecting database
Base = automap_base()
# reflecting tables
Base.prepare(engine, reflect=True)

@app.route('/', methods =["GET", "POST"])
def input():
    if request.method == 'POST':
      year = request.form['year']
      return redirect(f'migration_data_2019/{year}')
    else:
        year = request.args.get('year')
        return render_template('form.html')

@app.route("/map")
def index():

    connection_string = f"postgres:{password}@localhost:5432/project_3"
    engine = create_engine(f'postgresql://{connection_string}')
    if not database_exists(engine.url):
        create_database(engine.url)

    session = Session(engine)
    time.sleep(2)

    all_data = []
    for i in range(len(states)):
        data = session.execute(f"select sum(movedin) from migration_data_2019 where state1_name = '{states[i]}' group by state1_name, state2_name order by state2_name").all()
        data_fixed = []
        for row in data:
            data_fixed.append(list(map(int, list(row))))
        data_fixed = [data_fixed[i][0] for i in range(len(data_fixed))]
        all_data.append(data_fixed)

    df = pd.DataFrame(data=all_data, index=[states_abbrev, states], columns=df_columns)
    df.reset_index(inplace=True)
    df = df.rename(columns={'level_0':'abbrev', 'level_1':'state'})
    df = df.set_index(['abbrev','state'])
    coming_df = df
    coming_df = coming_df.apply(pd.to_numeric)
    for i in range(len(states)):
        coming_df.iloc[i,i] = 0 
    for i in range(len(states)):
        df.iloc[i,i] = "N/A"
    df.fillna(0, inplace=True)
    coming = df.to_csv(path_or_buf="static/coming.csv")

    all_data = []
    for i in range(len(states)):
        data = session.execute(f"select sum(movedout) from migration_data_2019 where state1_name = '{states[i]}' group by state1_name, state2_name order by state2_name").all()
        data_fixed = []
        for row in data:
            data_fixed.append(list(map(int, list(row))))
        data_fixed = [data_fixed[i][0] for i in range(len(data_fixed))]
        all_data.append(data_fixed)

    df = pd.DataFrame(data=all_data, index=[states_abbrev, states], columns=df_columns)
    df.reset_index(inplace=True)
    df = df.rename(columns={'level_0':'abbrev', 'level_1':'state'})
    df = df.set_index(['abbrev','state'])
    new_df = df
    new_df = new_df.apply(pd.to_numeric)
    for i in range(len(states)):
        new_df.iloc[i,i] = 0 
    df['total_imm']=coming_df.sum(axis=1)
    df['total_emm']=new_df.sum(axis=1)
    going_df = df
    for i in range(len(states)):
        df.iloc[i,i] = "N/A"
    df.fillna(0, inplace=True)
    going = df.to_csv(path_or_buf="static/going.csv")

    session.close()

    return render_template("index.html", coming=coming)

# Route that will trigger the scrape function
@app.route("/migration_data_2019/<year>")
def md2019 (year):

    url = f"https://api.census.gov/data/{year}/acs/flows?get=MOVEDIN,STATE1_NAME,STATE2_NAME,MOVEDOUT,FULL2_NAME,MOVEDNET&for=county:*"

    migration_data_2019 = pd.read_json(url)
    migration_data_2019.columns = migration_data_2019.iloc[0]
    migration_data_2019 = migration_data_2019.drop(index=0)

    migration_data_2019.columns  = [i.lower() for i in migration_data_2019.columns]

    not_states = ["Asia", "Europe", "U.S. Island Areas", "Africa", "Caribbean", "Oceania and At Sea", "Central America","Puerto Rico", "South America", "Northern America"] 
    for i in not_states:
        migration_data_2019 = migration_data_2019[migration_data_2019["state2_name"] != i]

    migration_data_2019["movedin"] = pd.to_numeric(migration_data_2019["movedin"])
    migration_data_2019["movedout"] = pd.to_numeric(migration_data_2019["movedout"])

    connection_string = f"postgres:{password}@localhost:5432/project_3"
    engine = create_engine(f'postgresql://{connection_string}')
    if not database_exists(engine.url):
        create_database(engine.url)

    migration_data_2019.to_sql(name='migration_data_2019', con=engine, if_exists='replace', index=False)

    return redirect("/map")

    session.close()


if __name__ == "__main__":
    app.run(debug=True)
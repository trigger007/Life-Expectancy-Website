from flask import Flask, render_template, redirect, url_for, request
import pandas as pd
import numpy as np
from scipy import stats
import logging
import datetime
import os.path
from flask import Markup

app=Flask(__name__)
app.config["DEBUG"]= True

BASE_DIR= os.path.dirname(os.path.abspath(__file__))
src= os.path.join(BASE_DIR, 'WHOSIS_000001,WHOSIS_000015.CSV')
who_list=pd.read_csv(src)
who_list = who_list[['GHO (DISPLAY)', 'YEAR (CODE)' , 'COUNTRY (DISPLAY)', 'SEX (DISPLAY)', 'Numeric']]
who_list['COUNTRY (DISPLAY)'] = [ctry.title() for ctry in who_list['COUNTRY (DISPLAY)'].values]
country_list= sorted(set(who_list['COUNTRY (DISPLAY)'].values))

def get_life_expectancy(age, country, sex):
    # pull latest entries for birth and 60 years
    sub_set = who_list[who_list['COUNTRY (DISPLAY)'].str.startswith(country, na=False)]
    sub_set = sub_set[sub_set['SEX (DISPLAY)'] == sex]
    sub_set = sub_set.sort_values('YEAR (CODE)', ascending=False)
    sub_set_birth = sub_set[sub_set['GHO (DISPLAY)'] == 'Life expectancy at birth (years)']
    sub_set_60 = sub_set[sub_set['GHO (DISPLAY)'] == 'Life expectancy at age 60 (years)']

    # not all combinations exsits so check that we have data for both
    if len(sub_set_birth['Numeric']) > 0 and len(sub_set_60['Numeric']) > 0:
        # create data set with both points as shown in first example
        lf_at_birth = sub_set_birth['Numeric'].values[0]
        lf_at_60 = sub_set_60['Numeric'].values[0]

        # model
        slope, intercept, r_value, p_value, std_err = stats.linregress([0,60],[lf_at_birth, lf_at_60])

        # predict for the age variable
        return(np.ceil(slope * age + intercept))
    else:
        return None

@app.route('/', methods=['POST', 'GET'])
def interact_life_expectancy():
    default_age='Select Age'
    selected_age=default_age
    default_sex='Select Gender'
    selected_sex=default_sex
    default_country='Select Country'
    selected_country=default_country
    string_print= ''
    healthy_image_list=[]
    if request.method=='POST':
        selected_age=request.form['age']
        selected_country=request.form['country']
        selected_sex=request.form['sex']

        time_left=get_life_expectancy(int(selected_age),selected_country,selected_sex)
        string_print=Markup("you have <font size='+10'> "+ str(int(np.ceil(time_left))) + "</font> healthy years left to live")
    return render_template('time.html', country_list=country_list,
                           default_country=selected_country,
                           default_age=selected_age,
                           default_sex=selected_sex,
                           string_print=string_print)
        

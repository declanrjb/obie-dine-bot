import os
import requests
import pandas as pd
import datetime
import json
import re
import avi

target_date = datetime.datetime.today().strftime("%Y-%m-%d")

food = avi.get_meal_info(None,target_date)

menu = avi.html_format_meal(food)

with open('template.html', 'r') as in_file:
    in_text = in_file.read()

in_text = in_text.replace('{{content}}', menu)

with open('index.html', 'w+') as out_file:
    out_file.write(in_text)
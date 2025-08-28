import os
import requests
import pandas as pd
import datetime
import json
import re

halls = {
    'Stevenson':{
        'id':111,
        'meals':{
            'breakfast':182,
            'lunch':183,
            'dinner':184
        }
    },
    'Lord Saunders':{
        'id':184,
        'meals':{
            'dinner':470
        }
    },
    'Heritage':{
        'id':185,
        'meals':{
            'lunch':479,
            'dinner':480
        }
    },
    'Clarity':{
        'id':107,
        'meals':{
            'lunch':174,
            'dinner':175
        }
    }
}

def summarize_item(item):
    if type(item) == dict:
        main_cols = [k for k in item.keys() if k not in ['preferences','nutritionals','allergens']]
        filtered_dict = {k:item[k] for k in main_cols}
        for k in filtered_dict:
            if type(filtered_dict[k]) == list:
                filtered_dict[k] = ', '.join(filtered_dict[k])

        df = pd.DataFrame(filtered_dict, index=[0])

        return df
    else:
        print(item)
        return None

def scrape_session(date, hall_num, meal_num):
    response = requests.get(
        f'https://dish.avifoodsystems.com/api/menu-items/week?date={date}&locationId={hall_num}&mealId={meal_num}'
    )
    data = response.json()
    if len(data) > 0:
        try:
            result = pd.concat([summarize_item(item) for item in data])
        except:
            result = None
        return result
    else:
        return None

def scrape_week(date):
    results = []
    for hall in halls:
        for meal in halls[hall]['meals']:
            temp = scrape_session(date, halls[hall]['id'], halls[hall]['meals'][meal])
            if temp is not None:
                temp['hall'] = hall
                temp['meal'] = meal
                results.append(temp)
    if len(results) > 0:
        return pd.concat(results)
    else:
        return None

def get_meal_info(meal=None,today=datetime.datetime.today().strftime("%Y-%m-%d")):
    #today = datetime.datetime.today().strftime("%m/%d/%y")
    df = scrape_week(today)
    df = df.reset_index(drop = True)

    df['time'] = df['date'].apply(lambda date: date.split('T')[1])
    df['date'] = df['date'].apply(lambda date: date.split('T')[0])

    df = df[df['date'] == today]
    
    if meal is None:
        current_hour = int(datetime.datetime.today().strftime("%H"))
        if current_hour < 11:
            current_meal = 'breakfast'
        elif current_hour >= 11 and current_hour < 15:
            current_meal = 'lunch'
        else:
            current_meal = 'dinner'
    else:
        current_meal = meal

    df = df[df['meal'] == current_meal]

    result = {}
    for hall in df['hall'].unique():
        result[hall] = {}
        hall_all_stations = df[df['hall'] == hall]
        for station in hall_all_stations['stationName'].unique():
            station_data = hall_all_stations[hall_all_stations['stationName'] == station]
            result[hall][station] = station_data[['name','description']].to_dict(orient = 'records')
    
    return result

def format_meal(food):
    formatted = ''
    for hall in food:
        formatted += f'--- {hall} ---\n'
        stations = food[hall]
        for station in stations:
            items = [item['name'] for item in stations[station]]
            formatted += f"**{station}**: {', '.join(items)}\n"
        formatted += '\n'
    formatted = formatted.strip()
    return formatted

def html_format_meal(food):
    formatted = ''
    for hall in food:
        formatted += f'<h1>{hall}</h1>'
        stations = food[hall]
        for station in stations:
            items = [item['name'] for item in stations[station]]
            formatted += f"<p><b>{station}</b>: {', '.join(items)}</p>"
    formatted = formatted.strip()
    return formatted
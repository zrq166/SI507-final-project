import json
import requests
import sqlite3
from bs4 import BeautifulSoup
import plotly.graph_objs as go
from secret import TMDBKEY
CACHE_FNAME = 'cache.json'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/51.0.2704.63 Safari/537.36'}
DBNAME = 'finalproject.db'
help_text = '''
    Commands available:
    tv popularity and rating
            Description: Lists tv name, popularity and rating according to the specified parameters. 
            (The results are ordered by the descending order of popularity)
            Options:
                    * top=<limit> | bottom=<limit> [default: top=50] [<limit>range: 0 to 200]
                    Description: Specifies whether to list the top <limit> matches or the 
                    bottom <limit> matches. 
    
    tv country and rating
            Description: Lists country name and rating according to the specified parameters.
            Options:
                    * minrating=<limit> [default:minrating 0] [<limit>range: 0 to 9]
                    Description: The results are countries that has average ratings higher than <limit>
    
    tv #released per month
            Description: Show the number of tv released per month in 2018 in pie chart.
    
    tv ratings and month
            Description: Show the trend of ratings in all months in 2018.
'''


class Country():
    def __init__(self, name='', code='', population=0, area=0, gdp=''):
        self.name = name
        self.code = code
        self.population = population
        self.area = area
        self.gdp = gdp


def make_request_using_cache(url):
    unique_ident = url

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        # print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        # print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url, headers)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME, "w")
        fw.write(dumped_json_cache)
        fw.close()  # Close the open file
        return CACHE_DICTION[unique_ident]


try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

# create db
conn = sqlite3.connect(DBNAME)
cur = conn.cursor()
# Drop tables
statement = '''
            DROP TABLE IF EXISTS 'TV';
        '''
cur.execute(statement)
statement = '''
            DROP TABLE IF EXISTS 'Country';
        '''
cur.execute(statement)
conn.commit()
statement = '''
            CREATE TABLE 'Country' (
                    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                    'CountryName' TEXT NOT NULL,
                    'CountryCode' TEXT NOT NULL,
                    'Population' INTEGER NOT NULL,
                    'Area' INTEGER NOT NULL,
                    'GDP' TEXT NOT NULL
            );        
        '''
cur.execute(statement)
statement = '''
            CREATE TABLE 'TV' (
                    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                    'TvName' TEXT NOT NULL,
                    'Popularity' REAL NOT NULL,
                    'DateMonth' INTEGER NOT NULL,
                    'DateDay' INTEGER NOT NULL,
                    'Rating' REAL NOT NULL,
                    'CountryId' INTEGER,
                    FOREIGN KEY ('CountryId') REFERENCES Country('Id')
            );        
        '''
cur.execute(statement)
conn.commit()
conn.close()

url_country = 'https://countrycode.org/'
country_text = make_request_using_cache(url_country)
country_soup = BeautifulSoup(country_text, 'html.parser')
country_total = country_soup.find(class_='table table-hover table-striped main-table')
country_list = country_total.find_all('tr')
country_instances = []
first_flag = 1
for i in country_list:
    if first_flag == 1:
        first_flag = 0
        continue
    info_list = i.find_all('td')
    popu = info_list[3].string.replace(',', '')
    area = info_list[4].string.replace(',', '')
    temp_instance = Country(info_list[0].text, info_list[2].text[0:2], popu, area, info_list[5].text)
    country_instances.append(temp_instance)

# import data into table Country
conn = sqlite3.connect(DBNAME)
cur = conn.cursor()
for country1 in country_instances:
    name_ = country1.name
    code_ = country1.code
    population_ = country1.population
    area_ = country1.area
    gdp_ = country1.gdp
    insertion = (None, name_, code_, population_, area_, gdp_)
    statement = 'INSERT INTO "Country" '
    statement += 'VALUES (?, ?, ?, ?, ?, ?)'
    cur.execute(statement, insertion)
conn.commit()
conn.close()

tv_list_total = []
url_tv = 'https://api.themoviedb.org/3/discover/tv?api_key=' + TMDBKEY + '&first_air_date_year=2018&sort_by=popularity.desc'
for i in range(1, 11):
    url_tv_temp = url_tv + '&page=' + str(i)
    list_temp = json.loads(make_request_using_cache(url_tv_temp))["results"]
    tv_list_total = tv_list_total + list_temp

# import tv data into table TV
conn = sqlite3.connect(DBNAME)
cur = conn.cursor()
for dic_1 in tv_list_total:
    tv_name = dic_1['name']
    tv_popularity = dic_1['popularity']
    tv_month = str(dic_1['first_air_date'][5:7]).lstrip('0')
    tv_day = str(dic_1['first_air_date'][8:10]).lstrip('0')
    tv_rating = dic_1['vote_average']
    countryAb = str(dic_1['origin_country']).replace('[', '').replace(']', '').strip("'")
    statement = '''
            SELECT Id FROM Country
            WHERE CountryCode = ?
            '''
    cur.execute(statement, (countryAb,))
    try:
        id_country = cur.fetchone()[0]
    except:
        id_country = None
    insertion = (None, tv_name, tv_popularity, tv_month, tv_day, tv_rating, id_country)
    statement = 'INSERT INTO "TV" '
    statement += 'VALUES (?, ?, ?, ?, ?, ?, ?)'
    cur.execute(statement, insertion)
conn.commit()
conn.close()


def get_content(command, text):
    index = command.find(text)
    index += len(text)
    try:
        content = command[index:].split(' ')[0]
    except:
        content = None
    return content


def process_command(command):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    result = []

    if command[:24] == 'tv popularity and rating':
        query_tuple = ()
        where_temp = ''
        remains = command.replace('tv popularity and rating', '').strip()
        if remains != '' and not remains.startswith('top=') and not remains.startswith('bottom='):
            raise NameError

        if command.find('bottom=') != -1:
            num = get_content(command, 'bottom=')
            where_temp += ' ASC LIMIT ? '
            query_tuple += (num,)
        else:
            num = 50
            if command.find('top=') != -1:
                num = get_content(command, 'top=')
            where_temp += ' DESC LIMIT ? '
            query_tuple += (num,)

        statement = '''
                        SELECT TvName, Popularity, Rating FROM TV ORDER BY Popularity
                        '''

        statement += where_temp
        cur.execute(statement, query_tuple)
        result = cur.fetchall()

    elif command[:21] == 'tv country and rating':
        query_tuple = ()
        where_temp = ''
        remains = command.replace('tv country and rating', '').strip()
        if remains != '' and not remains.startswith('minrating='):
            raise NameError

        if command.find('minrating=') != -1:
            num = get_content(command, 'minrating=')
            where_temp += ' GROUP BY t.CountryId HAVING t.Rating > ? '
            query_tuple += (num,)
        else:
            num = 0
            where_temp += ' GROUP BY t.CountryId HAVING t.Rating > ? '
            query_tuple += (num,)

        statement = '''
                        SELECT c.CountryName, t.Rating FROM TV AS t 
                        LEFT JOIN Country AS c
                        ON t.CountryId = c.Id
                                '''

        statement += where_temp
        statement += ' ORDER BY t.Rating DESC'
        cur.execute(statement, query_tuple)
        result = cur.fetchall()

    elif command[:22] == 'tv #released per month':
        if command != 'tv #released per month':
            raise NameError
        statement = '''
                       SELECT DateMonth, COUNT(Id) FROM TV GROUP BY DateMonth
                                '''
        cur.execute(statement)
        result = cur.fetchall()

    elif command[:20] == 'tv ratings and month':
        if command != 'tv ratings and month':
            raise NameError
        statement = '''
                          SELECT DateMonth, ROUND( AVG(Rating),1) FROM TV GROUP BY DateMonth
                                   '''
        cur.execute(statement)
        result = cur.fetchall()

    conn.close()
    return result


def interactive():
    response = ''
    while True:
        response = input('Enter a command: ')
        if response.strip() == '':
            continue
        if response == 'help':
            print(help_text)
            continue
        elif response == 'exit':
            print("bye")
            break
        elif response[:24] == 'tv popularity and rating' or response[:21] == 'tv country and rating' or response[
                                                                                                        :22] == 'tv #released per month' or response[
                                                                                                                                            :20] == 'tv ratings and month':
            try:
                tuple = process_command(response)
            except:
                print("Command not recognized: " + response)
                continue
            length_format = []
            if not tuple:
                print("No matched results")
                continue
            if response[:24] == 'tv popularity and rating':
                tuple_print = [('TvName', 'Popularity', 'Rating')] + tuple
            elif response[:21] == 'tv country and rating':
                tuple_print = [('Country', 'Rating')] + tuple
            elif response[:22] == 'tv #released per month':
                tuple_print = [('Month', 'Count')] + tuple
            elif response[:20] == 'tv ratings and month':
                tuple_print = [('Month', 'Avg Rating')] + tuple
            else:
                continue

            # print out results
            for index in range(len(tuple_print[0])):
                maxlen = -1
                for row1 in tuple_print:
                    if len(str(row1[index])) > maxlen:
                        maxlen = len(str(row1[index]))
                length_format.append(maxlen)
            for line_temp in tuple_print:
                for j in range(len(line_temp)):
                    format_string = "{0:<" + str(length_format[j]) + "s}"
                    print(format_string.format(str(line_temp[j])), end="  ")
                print("")

            if response[:24] == 'tv popularity and rating':
                x_rating = []
                y_popularity = []
                for line_data in tuple:
                    y_popularity.append(line_data[1])
                    x_rating.append(line_data[2])

                trace = go.Scatter(
                    x=x_rating,
                    y=y_popularity,
                    mode='markers'
                )

                layout = dict(
                    title='Population v.s. rating',
                    xaxis_title="Rating",
                    yaxis_title="Popularity"
                )
                data = [trace]
                fig = go.Figure(data=data)
                fig = fig.update_layout(layout)
                fig.write_html('scatter.html', auto_open=True)
            elif response[:21] == 'tv country and rating':
                x_bar = []  # rating
                y_bar = []  # country
                for line_data in tuple:
                    x_bar.insert(0, line_data[1])
                    y_bar.insert(0, line_data[0])
                trace = go.Bar(
                    x=x_bar,
                    y=y_bar,
                    orientation='h',
                    marker=dict(
                        color='rgba(246, 78, 139, 0.8)',
                    )
                )

                layout = dict(
                    title='Barplot of country with Tv rating',
                    xaxis_title="Rating",
                    yaxis_title="Country"
                )
                data = [trace]
                fig = go.Figure(data=data)
                fig = fig.update_layout(layout)
                fig.write_html('bar.html', auto_open=True)

            elif response[:22] == 'tv #released per month':
                values_pie = []
                labels_pie = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                              'October', 'November', 'December']
                for line_data in tuple:
                    values_pie.append(line_data[1])
                trace = go.Pie(
                    labels=labels_pie,
                    values=values_pie,
                    sort=False,
                )

                layout = dict(
                    title='Pie chart of the number of TVs per month',
                )
                data = [trace]
                fig = go.Figure(data=data)
                fig = fig.update_layout(layout)
                fig.write_html('pie.html', auto_open=True)
            elif response[:20] == 'tv ratings and month':
                x_line=[]
                y_line=[]
                for line_data in tuple:
                    x_line.append(line_data[0])
                    y_line.append(line_data[1])
                trace = go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode='lines+markers',
                    name='lines+markers'
                )

                layout = dict(
                    title='Line chart of ratings v.s. month in 2018',
                    xaxis_title="Month",
                    yaxis_title="Rating"
                )
                data = [trace]
                fig = go.Figure(data=data)
                fig = fig.update_layout(layout)
                fig.write_html('line.html', auto_open=True)
        else:
            print("Command not recognized: " + response)


if __name__ == "__main__":
    interactive()

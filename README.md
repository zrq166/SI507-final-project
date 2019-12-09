# SI507-final-project
 
* ## Data Source 
> There are two data sources in my project. Country table and TV table have a relation of Country Name. The TV table has a Foriegn key of CountryId, which references Id in Country table.
>> 1. Country table is composed of data from <https://countrycode.org/>. I scrape COUNTRY, ISO CODES, POPULATION, AREA KM2, and GDP $USD from the website.  
>> 2. TV table is composed of data returned from **The Movie Database API:** <https://developers.themoviedb.org/>.  

* ## Environment
To run this program, your environment should satisfy requirements.txt.

* ## Code structure
> ### Database construction  
> To construct database, the program first scrapes from <https://countrycode.org/> to get COUNTRY, ISO CODES, POPULATION, AREA KM2, and GDP $USD, which is enough to construct table Country. Second, the program uses **The Movie Database API** to get the 200 most popular tv shows in 2018.
> ### Class: Country
> There is a class named as Country, which is powerful in storing each country's information temporarily when scraping from website. 
> ### Function: process_command()
> This function takes user's input, generates SQL sentences, and applies them on database. Finally, it returns the results getting from database.
> ### Function: interactive()
> This function supports interaction and prompt with users. It roughly estimates user's input and then calls process_command() to get data from database. After that, it uses plotly to draw different kinds of charts accorading to user's input.
> ### Lists
> There are several lists in the whole program. For example, x_rating and y_popularity are created when drawing scatter plot.

* ## Guide
To run the program, just input
```python
python3 main.py
```
Then you will see "Enter a command:". To start with it, you can first type "help" to get the help information about how to use this program. Just like the following shows.
 ```python
 Enter a command: help
 ```
 There are mainly four kinds of command you can choose. 
 ```
    Commands available:
    tv popularity and rating
            Description: Lists tv name, popularity and rating according to the specified parameters. 
            (The results are ordered by the descending order of popularity)
            Options:
                    * top=<limit> | bottom=<limit> [default: top=50] [<limit>range: 0 to 100]
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
 ```
For example, if your input is
```
 Enter a command: tv country and rating minrating=6
```
You will get the results in the terminal: country names and the average ratings of Tv shows of countries which have ratings more than 6. Also, you will get a bar chart which shows country name with average rating of Tv shows corresponds to the country.

from itertools import cycle

import requests
from bs4 import BeautifulSoup

from events.scrapers.common import wait, get_proxies

ALL_MOVIES_URL = 'https://www.seret.co.il/movies/index.asp?catCase=2'
ALL_THEATERS_URL = 'https://www.seret.co.il/movies/theatres.asp'

s0 = 'width:99%;padding:4px;height:145px;line-height:141px;text-align:right;direction:rtl;overflow:hidden;padding:4px 0;margin:0 0 4px 0;'
s1 = 'width:99%;padding:4px;height:145px;line-height:141px;text-align:right;direction:rtl;overflow:hidden;padding:4px 0;margin:0 0 4px 0;border-top:solid 1px #e9e9e9;'
s2 = 'display:inline-block;width:25%;max-width:220px;text-align:center;vertical-align:top;'
s3 = 'width:100%;max-height:290px;'
s4 = 'display:inline-block;width:70%;position:relative;text-align:right;margin-right:2%;margin-top:-2px;height:100%;vertical-align:top;'
s5 = 'display:inline-block;width:73%;margin-right:1%;vertical-align:middle;'



def scraper_seret():
    proxies = cycle(get_proxies())

    all_movies_response = requests.get(ALL_MOVIES_URL)
    b = BeautifulSoup(all_movies_response.content, 'html.parser')
    main_content = b.find('div', attrs={'id': 'maincontent'}).find('div', attrs={'class': 'flexcol2-3'})

    movies_divs = main_content.find_all('div', attrs={'style': s0}) + main_content.find_all('div', attrs={'style': s1})
    movies = {}
    for m in movies_divs:
        proxy = next(proxies)
        link = m.find('a', attrs={'class':'DarkGreenStrong18'}).attrs['href']
        movie_url = 'https://www.seret.co.il/movies/' + link
        movie_response = requests.get(movie_url, proxies={"http": proxy, "https": proxy})
        b_movie = BeautifulSoup(movie_response.content, 'html.parser')
        main_movie_content = b_movie.find('div', {'id': 'maincontent'})
        title_heb =  main_movie_content.find('h1').contents[0]
        title =  main_movie_content.find('h2').contents[0]
        description_heb = main_movie_content.find('span', {'itemprop': 'description'}).contents[0]
        img_link = main_movie_content.find('div', {'style': s2}).find('img', {'style': 'width:100%;max-height:290px;'}).attrs['src']
        metadata = main_movie_content.find('div', {'style': s4})
        actors = metadata.find('span', {'style': s5}).find_all('a')
        actors_names = [a.find('span').contents[0] for a in actors]
        director_name_span = main_movie_content.find('span', {'itemprop': 'director'})
        director_name = director_name_span.contents[0] if director_name_span else None
        score = main_movie_content.find('span', {'itemprop': 'ratingValue'}).contents[0]
        genre = main_movie_content.find('a', {'itemprop': 'genre'}).contents[0]
        movies[title_heb] = {
            'link': movie_url,
            'title': title,
            'title_heb': title_heb,
            'description_heb': description_heb,
            'img': img_link,
            'metadata': {'actors': ','.join(actors_names), 'director_name': director_name, 'score': score, genre: 'genre'}
        }
        wait()

    all_theaters_response = requests.get(ALL_THEATERS_URL)
    b = BeautifulSoup(all_theaters_response.content, 'html.parser')
    mc = b.find('div', {'id': 'maincontent'})
    per_city = {}
    for d in mc.find_all('div'):
        if d.attrs.get('class') and d.attrs.get('class')[0] == 'cityname':
            city_name = d.find('a').contents[0]
            current_city = city_name
            per_city[city_name] = []
        elif d.attrs.get('class') and d.attrs.get('class')[0] == 'trow':
            per_city[current_city].append((d.find('a').contents[0], d.find('a').attrs['href']))

    theaters = {}

    for city in per_city:
        print ('Doing city: ' + city)
        for theater_name, theater_link in per_city[city]:
            theater_url = 'https://www.seret.co.il/movies/' + theater_link
            theater_response = requests.get(theater_url)
            b = BeautifulSoup(theater_response.content, 'html.parser')
            showtimes_div = b.find(id='showtimespanel')
            divs_titles = showtimes_div.find_all('div', {'class': 'cityname DarkGreen14'})
            divs_showtimes = showtimes_div.find_all('div', {'class': 'trow'})
            for title_div, showtime_div in zip(divs_titles, divs_showtimes):
                title_heb = title_div.find('a').contents[0]
                print (title_heb)
                for day_span, hours_span in zip(showtime_div.find_all('span', {'class': 'dayname'}), showtimes_div.find_all('span', {'class': 'dayhours'})):
                    print (day_span.contents[0])
                    print (hours_span.contents[0])



    # result: {city1name: {theater1name: theater1link, theater2name: theater2link}, city2name: .... }



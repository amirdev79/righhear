import email
import tempfile
from itertools import cycle

import requests
from bs4 import BeautifulSoup

from righthear import settings
from django.core.mail import EmailMessage

from events.models import Venue
from events.scrapers.common import wait, get_proxies
from events.utils import get_gmaps_info

ALL_MOVIES_URL = 'https://www.seret.co.il/movies/index.asp?catCase=2'
ALL_THEATERS_URL = 'https://www.seret.co.il/movies/theatres.asp'

s0 = 'width:99%;padding:4px;height:145px;line-height:141px;text-align:right;direction:rtl;overflow:hidden;padding:4px 0;margin:0 0 4px 0;'
s1 = 'width:99%;padding:4px;height:145px;line-height:141px;text-align:right;direction:rtl;overflow:hidden;padding:4px 0;margin:0 0 4px 0;border-top:solid 1px #e9e9e9;'
s2 = 'display:inline-block;width:25%;max-width:220px;text-align:center;vertical-align:top;'
s3 = 'width:100%;max-height:290px;'
s4 = 'display:inline-block;width:70%;position:relative;text-align:right;margin-right:2%;margin-top:-2px;height:100%;vertical-align:top;'
s5 = 'display:inline-block;width:73%;margin-right:1%;vertical-align:middle;'

CSV_THEATER_FIELDS = [
    'name', 'name_heb', 'street_address', 'street_address_heb', 'city', 'city_heb', 'phone_number', 'longitude',
    'latitude', 'link', 'additional_info'
]


def scraper_seret():
    proxies = cycle(get_proxies())

    all_movies_response = requests.get(ALL_MOVIES_URL)
    b = BeautifulSoup(all_movies_response.content, 'html.parser')
    main_content = b.find('div', attrs={'id': 'maincontent'}).find('div', attrs={'class': 'flexcol2-3'})

    movies_divs = main_content.find_all('div', attrs={'style': s0}) + main_content.find_all('div', attrs={'style': s1})
    movies = {}
    for m in movies_divs:
        proxy = next(proxies)
        link = m.find('a', attrs={'class': 'DarkGreenStrong18'}).attrs['href']
        movie_url = 'https://www.seret.co.il/movies/' + link
        movie_response = requests.get(movie_url, proxies={"http": proxy, "https": proxy})
        b_movie = BeautifulSoup(movie_response.content, 'html.parser')
        main_movie_content = b_movie.find('div', {'id': 'maincontent'})
        title_heb = main_movie_content.find('h1').contents[0]
        title = main_movie_content.find('h2').contents[0]
        description_heb = main_movie_content.find('span', {'itemprop': 'description'}).contents[0]
        img_link = \
            main_movie_content.find('div', {'style': s2}).find('img', {'style': 'width:100%;max-height:290px;'}).attrs[
                'src']
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
            'metadata': {'actors': ','.join(actors_names), 'director_name': director_name, 'score': score,
                         genre: 'genre'}
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
        print('Doing city: ' + city)
        for theater_name, theater_link in per_city[city]:
            theater_url = 'https://www.seret.co.il/movies/' + theater_link
            theater_response = requests.get(theater_url)
            b = BeautifulSoup(theater_response.content, 'html.parser')
            showtimes_div = b.find(id='showtimespanel')
            divs_titles = showtimes_div.find_all('div', {'class': 'cityname DarkGreen14'})
            divs_showtimes = showtimes_div.find_all('div', {'class': 'trow'})
            for title_div, showtime_div in zip(divs_titles, divs_showtimes):
                title_heb = title_div.find('a').contents[0]
                print(title_heb)
                for day_span, hours_span in zip(showtime_div.find_all('span', {'class': 'dayname'}),
                                                showtimes_div.find_all('span', {'class': 'dayhours'})):
                    print(day_span.contents[0])
                    print(hours_span.contents[0])

    # result: {city1name: {theater1name: theater1link, theater2name: theater2link}, city2name: .... }

def parse_theaters():
    all_theaters_response = requests.get(ALL_THEATERS_URL)
    b = BeautifulSoup(all_theaters_response.content, 'html.parser')
    mc = b.find('div', {'id': 'maincontent'})
    per_city = {}
    theaters = []
    current_city = ''
    for d in mc.find_all('div'):
        if d.attrs.get('class') and d.attrs.get('class')[0] == 'cityname':
            city_name = d.find('a').contents[0]
            current_city = city_name
            per_city[city_name] = []
            lastd = d
        elif d.attrs.get('class') and d.attrs.get('class')[0] == 'trow':
            theater_name_heb = d.find('a').contents[0]
            link = d.find('a').attrs['href']
            address = d.find('span', {'style': 'float:right;width:20%;margin-top:4px;margin-right:10px;'}).contents[
                0]
            gmaps_address = get_gmaps_info(address)
            if gmaps_address:
                address_arr = gmaps_address['formatted_address'].split(',')
                theater_city_heb = current_city
                theater_address_eng = address_arr[0]
                lat = gmaps_address['lat']
                lng = gmaps_address['lng']
            phone_elements = d.find_all('span', {'class': 'DarkGreen12'})[1:]
            phone_theater = phone_elements[0].contents[0].replace('טלפון: ', '') if phone_elements[
                0].contents else None
            phone_tickets = phone_elements[0].contents[2].replace("טל' כרטיסים: ", '') if len(
                phone_elements[0].contents) == 3 else None
            # phone_tickets =  phone_elements[0].contents[0].replace("טל' כרטיסים: ", '') if phone_tickets_elements else None

            # phone_tickets =
            # phone_theater, phone_tickets = phone_elements.contents[0].replace('טלפון: ', ''), phone_elements.contents[2].replace("טל' כרטיסים: ", ''),
            theaters.append(
                {'name_heb': theater_name_heb,
                 'city_heb': theater_city_heb,
                 'street_address': theater_address_eng,
                 'longitude': lng,
                 'latitude': lat,
                 'additional_info': {'phone_tickets': phone_tickets, 'scraper_name_heb': theater_name_heb},
                 'phone_number': phone_theater})

    theaters_lines = [','.join(CSV_THEATER_FIELDS)]
    for theater in theaters:
        theaters_lines.append(
            ','.join(['"' + str((theater.get(field, '') or '')).replace('"', '""').strip() + '"' for field in
                      CSV_THEATER_FIELDS]))

    theaters_csv_file = tempfile.NamedTemporaryFile(suffix='.csv')
    with open(theaters_csv_file.name, 'w+') as f:
        f.write('\n'.join(theaters_lines))

    email = EmailMessage(
        'Seret Theaters list',
        'See attached CSV. please update all the missing fields',
        settings.DEFAULT_EMAIL,
        [settings.DEFAULT_EMAIL],
    )
    email.attach_file(theaters_csv_file.name)
    email.send()

    # address, phone =  d.find_all('span', {'class': 'DarkGreen12'})
    # else:
    #     print (gmaps_address)

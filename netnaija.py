import requests
from bs4 import BeautifulSoup

def movie_link(movie_name):
    url = f'https://netnaija.xyz/{movie_name.replace(" ", "-")}'
    get_movie = requests.get(url).content
    soup = BeautifulSoup(get_movie, 'lxml')
    link_btn = soup.find('div', class_='wp-block-button')
    if link_btn:
        link = link_btn.a['href']
        return link
    return None

# def movie_link(movie_name):
#     url = f'https://goku.watch/search?keyword={movie_name}'
#     get_movie = requests.get(url).content
#     soup = BeautifulSoup(get_movie, 'lxml')
#     link_btn = soup.find('div', class_='is-watch')
#     if link_btn:
#         link = link_btn.a['href']
#         return link
#     return None

def movie_series_link(serial_name):
    series_url = f'https://series.netnaija.xyz/{serial_name.replace(" ", "-")}'
    get_series_movie = requests.get(series_url).content
    soup = BeautifulSoup(get_series_movie, 'lxml')
    link_btn = soup.find_all('div', class_='wp-block-button')
    for links in link_btn:
        link = links.find('a')
        return link

# def series_episode_links(serial_name):
#     series_url = f'https://series.netnaija.xyz/{serial_name.replace(" ", "-")}'
#     get_series_movie = requests.get(series_url).content
#     soup = BeautifulSoup(get_series_movie, 'lxml')
#     episodes = soup.find_all('div', class_='episode')
#     episode_links = []

#     for episode in episodes:
#         link = episode.find('a')['href']
#         episode_links.append(link)

#     return episode_links


def movie_series_link(series_name):
    series_url = f'https://series.netnaija.xyz/{series_name.replace(" ", "-")}'
    get_series_movie = requests.get(series_url).content
    soup = BeautifulSoup(get_series_movie, 'lxml')
    links = []
    
    link_btns = soup.find_all('div', class_ = 'wp-block-button')
    for link_btn in link_btns:
        link = link_btn.find('a')['href']
        links.append(link)
    
    return links

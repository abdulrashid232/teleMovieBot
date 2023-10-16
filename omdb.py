import os
import requests

class OMDB:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "http://www.omdbapi.com/?apikey=" + self.api_key

    def movie_info(self, movieTitle):
        param = {"t": movieTitle}
        response = requests.get(self.url, params=param).json()

        if response.get("Response") != "True":
            return None

        movie_info = {}
        movie_info["title"] = response.get("Title")
        movie_info["year"] = response.get("Year")
        movie_info["plot"] = response.get("Plot")
        movie_info["actors"] = response.get("Actors")
        movie_info["ratings"] = response.get("Ratings")
        movie_info["imdb_ratings"] = response.get("imdbRating")
        movie_info['poster'] = response.get('Poster')

        # Fetch the YouTube trailer link
        youtube_trailer_url = self.fetch_youtube_trailer(response.get("imdbID"))
        movie_info["youtube_trailer"] = youtube_trailer_url

        return movie_info

    def fetch_youtube_trailer(self, imdb_id):
        youtube_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": self.api_key,  # Use your actual YouTube API key
            "q": f"{imdb_id} trailer",
            "part": "id",
            "maxResults": 1,
            "type": "video"
        }
        response = requests.get(youtube_url, params=params).json()

        if "items" in response and len(response["items"]) > 0:
            video_id = response["items"][0]["id"]["videoId"]
            youtube_trailer_link = f"https://www.youtube.com/watch?v={video_id}"
            return youtube_trailer_link

        return None






# def movie__series_link():
# 	print('Enter The movie Title')
# 	name = input('>').replace(' ','-')
# 	series_url = f'https://series.netnaija.xyz/{name}'

# 	get_series_movie = requests.get(series_url).content
# 	soup = BeautifulSoup(get_series_movie, 'lxml')
# 	link_btn = soup.find_all('div', class_ = 'wp-block-button')
# 	for links in link_btn:
# 		link = links.find('a')
#         return link

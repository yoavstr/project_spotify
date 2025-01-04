from pydantic import BaseModel, Field
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from wordcloud import WordCloud
import requests
from collections import Counter
import matplotlib.pyplot as plt

# Loading environment variables
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

scope = "user-top-read user-read-recently-played"


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope,
                                               show_dialog=True))    


def generate_simple_top_artist_wordcloud(term: str = Field(pattern="^(short_term|medium_term|long_term)$")):
    """This function generates a word cloud of the top genres of the user"""
    # Spotify API request for top artists
    top_artists = sp.current_user_top_artists(limit=50, time_range=term)
    print("Top artists retrieved with API request")

    # Extract the relevant information
    all_genres = [genre for item in top_artists['items'] for genre in item['genres']]

    # Count the genres
    sorted_genre_count = dict(sorted(dict(Counter(all_genres)).items(), key=lambda item: item[1], reverse=True))
    print("Genre information extracted and counted")

    # Generate the word cloud
    wordcloud = WordCloud(width=1920,
                        height=1080,
                        font_path="./fonts/BebasNeue-Regular.ttf",
                        background_color="black",
                        min_font_size=30,
                        max_font_size=150,
                        relative_scaling=0.15,
                        colormap="summer",
                        random_state=42,
                        ).generate_from_frequencies(sorted_genre_count)
    print("Word cloud generated")

    # Save the word cloud as an image
    output_file = "wordcloud_top_genres.png"
    wordcloud.to_file(output_file)
    print(f"Word cloud saved as {output_file}")
    print(sorted_genre_count)

if __name__ == "__main__":
    generate_simple_top_artist_wordcloud(term="long_term")
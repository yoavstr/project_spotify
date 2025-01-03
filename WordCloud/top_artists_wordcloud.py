from pydantic import BaseModel, Field
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from wordcloud import WordCloud


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


class TopArtistWordCloudInput(BaseModel):
    number_of_artists: int = Field(default=20, ge=10, se=50)
    term: str = Field(pattern="^(short_term|medium_term|long_term)$")
    size_by: str = Field(default="favorite", pattern="^(popularity|followers_count|favorite)$")


def generate_simple_top_artist_wordcloud(input: TopArtistWordCloudInput):
    """This function creates a simple WordCloud from the user's top artists. Inputs are:
    - Number of artists
    - Term - top artists since when? (long_term, medium_term, short_term)
    """
    # Spotify API request for top artists
    top_artists = sp.current_user_top_artists(limit=input.number_of_artists, time_range=input.term)

    # Extract the relevant information
    top_artists_info_list = [
    {
        "artist": artist["name"],
        "genres": ", ".join(artist["genres"]),
        "popularity": artist["popularity"],
        "followers_count": artist["followers"]["total"],
        "artist_id": artist["id"],
        "place": idx
    }
    for idx, artist in enumerate(top_artists["items"], start=1)
]
    
    # Generate the word frequencies based on the selected size_by parameter
    match input.size_by:
        case "popularity":
            word_frequencies = {entry["artist"]: entry["popularity"] for entry in top_artists_info_list}
        case "followers_count":
            word_frequencies = {entry["artist"]: entry["followers_count"] for entry in top_artists_info_list}
        case "favorite":
            word_frequencies = {entry["artist"]: 1 / entry["place"] for entry in top_artists_info_list}

    # https://matplotlib.org/stable/users/explain/colors/colormaps.html for colormap options

    # Generate the word cloud
    wordcloud = WordCloud(
        font_path="./fonts/DMSerifText-Regular.ttf",
        prefer_horizontal=0.5, # 50% chance of horizontal text
        colormap="spring", # Set the color map
        scale=3,
        width=1920, # 3840 × 2160 is 4K resolution
        height=1080,
        background_color="black",
        relative_scaling=0.25, # Reduce the impact of frequency on word size
    ).generate_from_frequencies(word_frequencies)

    # Save the word cloud as an image
    output_file = "wordcloud_top_artists.png"
    wordcloud.to_file(output_file)
    print(f"Word cloud saved as {output_file}")


if __name__ == "__main__":

    input_data = TopArtistWordCloudInput(number_of_artists=50, term="medium_term", size_by="favorite")
    generate_simple_top_artist_wordcloud(input_data)

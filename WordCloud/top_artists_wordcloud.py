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
    # Generate the word frequencies
    word_frequencies = {entry["artist"]: 1 / entry["place"] for entry in top_artists_info_list}

    # Generate the word cloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="black",
        max_font_size=100,          # Adjust the maximum font size
        relative_scaling=0.25,       # Reduce the impact of frequency on word size
        # contour_width=100,            # Add a contour to help words stand out
        # contour_color="blue"   # Set the contour color
    ).generate_from_frequencies(word_frequencies)

    # Save the word cloud as an image
    output_file = "wordcloud.png"
    wordcloud.to_file(output_file)
    print(f"Word cloud saved as {output_file}")


if __name__ == "__main__":

    input_data = TopArtistWordCloudInput(number_of_artists=45, term="long_term")
    generate_simple_top_artist_wordcloud(input_data)

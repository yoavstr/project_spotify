from pydantic import BaseModel, Field
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from wordcloud import WordCloud
import requests
from colorthief import ColorThief
from io import BytesIO

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

class TopTracksWordCloudInput(BaseModel):
    number_of_tracks: int = Field(default=20, ge=10, se=50)
    term: str = Field(default="long_term", pattern="^(short_term|medium_term|long_term)$")
    size_by: str = Field(default="favorite", pattern="^(popularity|duration|favorite)$")
    color_by_album: bool = Field(default=True)


# Function to download the image from a URL
def get_image_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return BytesIO(response.content)

# Extract the dominant color using ColorThief
def get_dominant_color(url):
    image_data = get_image_from_url(url)
    color_thief = ColorThief(image_data)
    dominant_color = color_thief.get_color(quality=1)
    # Convert to hex
    return f"#{dominant_color[0]:02x}{dominant_color[1]:02x}{dominant_color[2]:02x}"


def generate_top_track_wordcloud_by_album_color(input: TopTracksWordCloudInput):
    """This function creates a WordCloud from the user's top tracks. Inputs are:
    - Number of tracks
    - Term - top tracks since when? (long_term, medium_term, short_term)
    - Size by - how to determine the size of the word (popularity, duration, favorite)
    - Color by album - use the dominant color of the album cover as the word color
    """

    # Spotify API request for top tracks
    top_tracks = sp.current_user_top_tracks(limit=input.number_of_tracks, time_range=input.term)


    if input.color_by_album:
        # Extract the relevant information
        top_tracks_info = [{"track": track["name"],
                        "artists": ", ".join(artist["name"] for artist in track["artists"]),
                        "popularity": track["popularity"],
                        "album_name": track["album"]["name"],
                        "track_duration_sec": track['duration_ms'] / 1000,
                        "release_date": track["album"]["release_date"],
                        "track_id": track["id"],
                        "cover_color": get_dominant_color(top_tracks["items"][idx]["album"]["images"][0]["url"]),
                        "place": idx + 1
                        } for idx, track in enumerate(top_tracks["items"])]
        
        # Custom color function
        def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
            return track_colors.get(word, "#000000")  # Default to black if no color is found

        # Map each track to its cover color
        track_colors = {entry["track"]: entry["cover_color"] for entry in top_tracks_info}

    else:
        # Extract the relevant information
        top_tracks_info = [{"track": track["name"],
                        "artists": ", ".join(artist["name"] for artist in track["artists"]),
                        "popularity": track["popularity"],
                        "album_name": track["album"]["name"],
                        "track_duration_sec": track['duration_ms'] / 1000,
                        "release_date": track["album"]["release_date"],
                        "track_id": track["id"],
                        "place": idx + 1
                        } for idx, track in enumerate(top_tracks["items"])]
        

    
    # Generate the word frequencies based on the selected size_by parameter
    match input.size_by:
        case "popularity":
            word_frequencies = {entry["track"]: entry["popularity"] for entry in top_tracks_info}
        case "duration":
            word_frequencies = {entry["track"]: entry["track_duration_sec"] for entry in top_tracks_info}
        case "favorite":
            word_frequencies = {entry["track"]: 1 / entry["place"] for entry in top_tracks_info}

    if input.color_by_album:
        # Generate the word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            max_font_size=100,          # Adjust the maximum font size
            relative_scaling=0.25,       # Reduce the impact of frequency on word size
            contour_width=0.1,            # Thickness of the outline
            contour_color="black"       # Color of the outline (white in this case)
        ).generate_from_frequencies(word_frequencies)

        wordcloud = wordcloud.recolor(color_func=color_func)

    else:
        # Generate the word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="black",
            max_font_size=100,          # Adjust the maximum font size
            relative_scaling=0.25,       # Reduce the impact of frequency on word size
            contour_width=0.1,            # Thickness of the outline
            contour_color="black"       # Color of the outline (white in this case)
        ).generate_from_frequencies(word_frequencies)
    
    # Save the word cloud as an image
    output_file = "wordcloud_top_tracks.png"
    wordcloud.to_file(output_file)
    print(f"Word cloud saved as {output_file}")


if __name__ == "__main__":
    input_data = TopTracksWordCloudInput(number_of_tracks=45, term="long_term", size_by="popularity", color_by_album=False)
    generate_top_track_wordcloud_by_album_color(input_data)

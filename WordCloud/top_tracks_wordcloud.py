from pydantic import BaseModel, Field
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from wordcloud import WordCloud
import requests
from colorthief import ColorThief
from io import BytesIO
import math

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

def extract_track_info(track, idx, color_by_album=False):
    track_info = {
        "track": track["name"],
        "artists": ", ".join(artist["name"] for artist in track["artists"]),
        "popularity": track["popularity"],
        "album_name": track["album"]["name"],
        "track_duration_sec": track['duration_ms'] / 1000,
        "release_date": track["album"]["release_date"],
        "track_id": track["id"],
        "place": idx + 1
    }
    if color_by_album:
        track_info["cover_color"] = get_dominant_color(track["album"]["images"][0]["url"])
    return track_info

def generate_wordcloud(word_frequencies, track_colors=None, color_by_album=False):
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return track_colors.get(word, "#000000") if track_colors else "#000000"

    wordcloud = WordCloud(
        font_path="./fonts/SpecialElite-Regular.ttf",
        width=1920,
        height=1080,
        background_color="white" if color_by_album else "black",
        relative_scaling=0.1,
        contour_width=0.1,
        contour_color="black" if color_by_album else "white",
    ).generate_from_frequencies(word_frequencies)

    if color_by_album:
        wordcloud = wordcloud.recolor(color_func=color_func)

    return wordcloud

def generate_top_track_wordcloud_by_album_color(input: TopTracksWordCloudInput):
    top_tracks = sp.current_user_top_tracks(limit=input.number_of_tracks, time_range=input.term)

    top_tracks_info = [
        extract_track_info(track, idx, color_by_album=input.color_by_album)
        for idx, track in enumerate(top_tracks["items"])
    ]
    
    
    # Generate the word frequencies based on the selected size_by parameter

    # Generate the word frequencies based on the selected size_by parameter
    match input.size_by:
        case "popularity":
            word_frequencies = {entry["track"]: entry["popularity"] for entry in top_tracks_info}
        case "duration":
            word_frequencies = {entry["track"]: entry["track_duration_sec"] for entry in top_tracks_info}
        case "favorite":
            # Exponential decay e^(-0.5)+1
            word_frequencies = {entry["track"]: math.e**(-0.5 * entry["place"]) + 1 for entry in top_tracks_info}
    track_colors = {entry["track"]: entry["cover_color"] for entry in top_tracks_info} if input.color_by_album else None
    print(word_frequencies)
    wordcloud = generate_wordcloud(word_frequencies, track_colors, input.color_by_album)
    output_file = "wordcloud_top_tracks.png"
    wordcloud.to_file(output_file)
    print(f"Word cloud saved as {output_file}")

if __name__ == "__main__":
    input_data = TopTracksWordCloudInput(number_of_tracks=40, term="medium_term", size_by="favorite", color_by_album=False)
    generate_top_track_wordcloud_by_album_color(input_data)

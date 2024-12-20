import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from collections import defaultdict

# Loading environment variables
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

scope = "user-library-read user-read-email user-read-private playlist-modify-private playlist-modify-public"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

def get_all_saved_tracks():
    all_results = []
    limit = 50
    offset = 0

    while True:
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = results["items"]

        if not items:
            break  # Exit the loop if there are no more items
        
        for idx, item in enumerate(items, start=offset + 1):
            track = item["track"]
            result = {
                "index": idx,
                "artist_name": track["artists"][0]["name"],
                "track_name": track["name"],
                "track_uri": track["uri"],
                "release_date": track["album"]["release_date"],
            }
            all_results.append(result)

        offset += limit  # Increment the offset for the next batch
    print("Successfully retrieved all liked songs.")
    return all_results


saved_tracks = get_all_saved_tracks()
saved_tracks_sorted = sorted(saved_tracks, key=lambda x: x["release_date"])

def group_tracks_by_decade(saved_tracks_sorted):
    # Dictionary to hold lists of tracks for each decade
    decades = defaultdict(list)

    for track in saved_tracks_sorted:
        # Extract the year from the release date
        year = int(track["release_date"].split("-")[0])
        # Determine the decade
        decade = (year // 10) * 10
        # Add the track to the corresponding decade list
        decades[decade].append(track)

    return decades

# Group tracks into decades
grouped_tracks = group_tracks_by_decade(saved_tracks_sorted)

# Extract individual lists for each decade
tracks_50s = [track["track_uri"] for track in grouped_tracks[1950]]
tracks_60s = [track["track_uri"] for track in grouped_tracks[1960]]
tracks_70s = [track["track_uri"] for track in grouped_tracks[1970]]
tracks_80s = [track["track_uri"] for track in grouped_tracks[1980]]
tracks_90s = [track["track_uri"] for track in grouped_tracks[1990]]
tracks_00s = [track["track_uri"] for track in grouped_tracks[2000]]
tracks_10s = [track["track_uri"] for track in grouped_tracks[2010]]
tracks_20s = [track["track_uri"] for track in grouped_tracks[2020]]

# Get User ID
user_id = sp.current_user()['id']

# Create a Playlist
def create_playlist(user_id, playlist_name, description, public=True):
    playlist = sp.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=public,
        description=description
    )
    print(f"Playlist created: {playlist['name']} (ID: {playlist['id']})")
    return playlist['id']

# Add Songs to the Playlist
def add_songs_to_playlist(playlist_id, track_uris):
    chunk_size = 100  # Spotify API limit
    for i in range(0, len(track_uris), chunk_size):
        chunk = track_uris[i:i + chunk_size]
        sp.playlist_add_items(playlist_id, chunk)
        print(f"Added {len(chunk)} tracks to playlist {playlist_id} (Chunk {i // chunk_size + 1})")


playlist_id_1950s = create_playlist(user_id, "1950s Playlist", 
                "A 1950s playlist created with Spotipy.", public=True)
playlist_id_1960s = create_playlist(user_id, "1960s Playlist", 
                "A 1960s playlist created with Spotipy.", public=True)
playlist_id_1970s = create_playlist(user_id, "1970s Playlist", 
                "A 1970s playlist created with Spotipy.", public=True)
playlist_id_1980s = create_playlist(user_id, "1980s Playlist", 
                "A 1980s playlist created with Spotipy.", public=True)
playlist_id_1990s = create_playlist(user_id, "1990s Playlist", 
                "A 1990s playlist created with Spotipy.", public=True)
playlist_id_2000s = create_playlist(user_id, "2000s Playlist", 
                "A 2000s playlist created with Spotipy.", public=True)
playlist_id_2010s = create_playlist(user_id, "2010s Playlist", 
                "A 2010s playlist created with Spotipy.", public=True)
playlist_id_2020s = create_playlist(user_id, "2020s Playlist", 
                "A 2020s playlist created with Spotipy.", public=True)


add_songs_to_playlist(playlist_id_1950s, tracks_50s)
add_songs_to_playlist(playlist_id_1960s, tracks_60s)
add_songs_to_playlist(playlist_id_1970s, tracks_70s)
add_songs_to_playlist(playlist_id_1980s, tracks_80s)
add_songs_to_playlist(playlist_id_1990s, tracks_90s)
add_songs_to_playlist(playlist_id_2000s, tracks_00s)
add_songs_to_playlist(playlist_id_2010s, tracks_10s)
add_songs_to_playlist(playlist_id_2020s, tracks_20s)

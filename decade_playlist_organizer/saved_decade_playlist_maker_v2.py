import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
from collections import defaultdict

NOTE = """
THIS IS THE SAME SCRIPT AS ./saved_decade_plalist_maker.py, WITH THE ONLY CHANGE BEING:
- Checks if a playlist with a given name already exists to avoid creating duplicates.
- Handles the conditional logic for creating playlists only if they dont already exist
- The script now verifies existing playlists before proceeding, ensuring no duplicates

PROBLEM IS:
- When the name of the playlist is changed, it still creates the playlist.
E.g.
When the name of "1950s Playlist" is changed, to anything else, it will create the 1950s playlist,
skipping the other ones.
"""

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

# Get all saved tracks
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

# Sort tracks by release date
saved_tracks = get_all_saved_tracks()
saved_tracks_sorted = sorted(saved_tracks, key=lambda x: x["release_date"])

# Group tracks by decade
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

# Check if a playlist exists
def playlist_exists(playlist_name):
    playlists = sp.current_user_playlists(limit=50)
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            print(f"Playlist '{playlist_name}' already exists.")
            return True
    return False

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

# Create playlists if they do not exist
def create_playlists_if_not_exist():
    playlists_to_create = {
        "1950s Playlist": tracks_50s,
        "1960s Playlist": tracks_60s,
        "1970s Playlist": tracks_70s,
        "1980s Playlist": tracks_80s,
        "1990s Playlist": tracks_90s,
        "2000s Playlist": tracks_00s,
        "2010s Playlist": tracks_10s,
        "2020s Playlist": tracks_20s,
    }

    for playlist_name, track_uris in playlists_to_create.items():
        if not playlist_exists(playlist_name):
            # Create the playlist
            playlist_id = create_playlist(user_id, playlist_name, f"A {playlist_name} created with Spotipy.", public=True)
            # Add songs to the playlist
            add_songs_to_playlist(playlist_id, track_uris)
        else:
            print(f"Skipping creation of '{playlist_name}' as it already exists.")

# Call the function to create playlists only if they do not exist
create_playlists_if_not_exist()

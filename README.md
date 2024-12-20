# Spotify Playlist Organizer by Decade

This Python script organizes your saved (liked) songs on Spotify into playlists based on their release decades. Using the Spotify Web API and the Spotipy library, the script automates the creation of playlists (1950s, 1960s, etc.) and adds tracks accordingly. 

(The script (v2) ensures that no duplicate playlists are created by checking for existing playlists before proceeding)


## Features

- Retrieves all your liked songs from Spotify.
- Organizes songs into playlists by release decades (1950s to 2020s).
- Automatically adds songs to the created playlists.
- Skips playlist creation if a playlist already exists. (v2)

## Setup

### 1. Create a Spotify Developer Application

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Create a new application.
3. Note down your **Client ID** and **Client Secret**.
4. Set the redirect URI.

### 2. Install Dependencies

To install required Python packages and libraries, simply run:
```bash
pip install -r requirements.txt

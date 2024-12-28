# Project Spotify

This is a fun side project using the Spotify API with spotipy.

## Spotify Playlist Organizer by Decade

This Python script organizes your saved (liked) songs on Spotify into playlists based on their release decades. Using the Spotify Web API and the Spotipy library, the script automates the creation of playlists (1950s, 1960s, etc.) and adds tracks accordingly. 

(The script (v2) ensures that no duplicate playlists are created by checking for existing playlists before proceeding)

- Retrieves all your liked songs from Spotify.
- Organizes songs into playlists by release decades (1950s to 2020s).
- Automatically adds songs to the created playlists.
- Skips playlist creation if a playlist already exists. (v2)


## Word Clouds

Creates word clouds from your top tracks and top artists with insightful visualizations either from your top artists, or top tracks.


This allows to input:
- **Number of Artists**: Specify the number of artists/tracks to include.
- **Term**: Select from short-term, medium-term, or long-term listening data.

- **Top Tracks Specific**:
    - *Dominant Color*: Words can match the dominant color of the track album cover.
    - *Size Criteria*: Size words by popularity, duration, or favorite metric.


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
```

### 3. Configure Environment Variables

Create a `.env` file in the project root directory and add the following:

```
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=your_redirect_uri
```

Replace `your_client_id`, `your_client_secret`, and `your_redirect_uri` with your actual Spotify Developer credentials.

---

Who needs Spotify Wrapped? Enjoy :)
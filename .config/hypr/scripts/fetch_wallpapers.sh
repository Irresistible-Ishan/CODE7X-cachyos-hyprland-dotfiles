#!/bin/bash

# Target directories
ANIME_DIR="$HOME/Wallpapers/Anime"
CYBER_DIR="$HOME/Wallpapers/Cyberpunk"

mkdir -p "$ANIME_DIR" "$CYBER_DIR"

download_walls() {
    local query=$1
    local category_bitmask=$2 # General/Anime/People (e.g., 010 for Anime only)
    local target_dir=$3
    local count=$4

    echo "Searching Wallhaven for: $query..."
    
    # Wallhaven API search
    # categories: 111 (General/Anime/People)
    # purity: 100 (SFW)
    # sorting: relevance
    local api_url="https://wallhaven.cc/api/v1/search?q=$(echo $query | sed 's/ /%20/g')&categories=$category_bitmask&purity=100&sorting=random"
    
    # Get image URLs
    local urls=$(curl -s "$api_url" | jq -r ".data[:$count] | .[] | .path")

    for url in $urls; do
        local filename=$(basename "$url")
        if [ ! -f "$target_dir/$filename" ]; then
            echo "Downloading $filename to $target_dir..."
            curl -s -L "$url" -o "$target_dir/$filename"
        else
            echo "Skipping $filename, already exists."
        fi
    done
}

# Download 5 Anime/Cyberpunk mix
download_walls "anime cyberpunk" "010" "$ANIME_DIR" 5

# Download 5 Sci-fi/Futuristic city
download_walls "sci-fi futuristic city" "100" "$CYBER_DIR" 5

# Download 5 General Cyberpunk/Tech
download_walls "cyberpunk tech" "110" "$CYBER_DIR" 5

echo "Download complete!"

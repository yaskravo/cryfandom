#!/bin/bash

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Make CLI script executable
chmod +x bin/fandom-article-creator

# Create symbolic link
sudo ln -sf "$(pwd)/bin/fandom-article-creator" /usr/local/bin/fandom-article-creator

echo "Fandom Article Creator installed successfully!"

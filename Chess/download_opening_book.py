#!/usr/bin/env python3
"""
Download Opening Book Script
This script downloads a sample Polyglot opening book for use with the chess AI.
"""

import os
import sys
import urllib.request
import shutil
import zipfile

# URLs for sample opening books
BOOK_URLS = {
    "small": "https://github.com/official-stockfish/books/raw/master/bin/gm2600.bin",
    "medium": "https://github.com/official-stockfish/books/raw/master/bin/varied.bin",
    "large": "https://github.com/official-stockfish/books/raw/master/bin/perfect2021.bin"
}

def download_file(url, destination):
    """Download a file from a URL to a destination path."""
    print(f"Downloading from {url}...")
    
    try:
        with urllib.request.urlopen(url) as response, open(destination, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"Downloaded to {destination}")
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def main():
    """Main function to download the opening book."""
    # Create the books directory if it doesn't exist
    books_dir = os.path.join("chess_ai", "books")
    os.makedirs(books_dir, exist_ok=True)
    
    # Ask the user which book to download
    print("Which opening book would you like to download?")
    print("1. Small (GM2600 - ~1MB)")
    print("2. Medium (Varied - ~2MB)")
    print("3. Large (Perfect2021 - ~4MB)")
    
    choice = input("Enter your choice (1-3) or 'q' to quit: ").strip()
    
    if choice == 'q':
        print("Exiting without downloading.")
        return 0
    
    try:
        choice_num = int(choice)
        if choice_num < 1 or choice_num > 3:
            print("Invalid choice. Please enter a number between 1 and 3.")
            return 1
        
        book_type = ["small", "medium", "large"][choice_num - 1]
        url = BOOK_URLS[book_type]
        
        # Destination path
        dest_path = os.path.join(books_dir, "book.bin")
        
        # Download the file
        if download_file(url, dest_path):
            print("\nOpening book downloaded successfully!")
            print(f"The book is now available at {dest_path}")
            print("You can use it with the chess AI by enabling the opening book:")
            print("- In the GUI: Press 'b' to toggle the opening book")
            print("- In the CLI: Type 'book on' to enable the opening book")
            return 0
        else:
            print("Failed to download the opening book.")
            return 1
        
    except ValueError:
        print("Invalid input. Please enter a number.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

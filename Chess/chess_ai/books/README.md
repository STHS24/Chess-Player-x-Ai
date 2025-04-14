# Chess Opening Books

This directory is for storing Polyglot opening book files (.bin) that can be used by the chess engine.

## Supported Formats

The engine supports Polyglot opening book files (.bin format). These are binary files that contain chess positions and corresponding moves with weights.

## Default Book

To use a default opening book, place a file named `book.bin` in this directory.

## Where to Find Opening Books

You can find Polyglot opening books from various sources:

1. **FICS Books**: http://ficsgames.org/openings/
2. **Cerebellum**: https://github.com/official-stockfish/books
3. **Lichess**: https://github.com/lichess-org/chess-openings

## Creating Your Own Books

You can create your own Polyglot opening books using tools like:

1. **Polyglot**: http://hardy.uhasselt.be/Toga/polyglot.html
2. **pgn2book**: https://github.com/michaeldv/pgn2book

## Usage

The opening book is automatically used by the engine if available. You can configure the opening book usage in the settings.

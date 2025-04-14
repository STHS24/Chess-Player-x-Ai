# Chess AI with Sunfish

![Chess Game](https://img.shields.io/badge/Chess-Game-brightgreen)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

A modern, customizable chess application with an integrated AI opponent powered by the Sunfish chess engine. This project features a clean graphical interface built with Pygame and leverages the python-chess library for game logic and move validation.

## 🎮 Features

- **Intelligent AI Opponent**: Play against the Sunfish chess engine with adjustable difficulty levels
- **Interactive GUI**: Clean, minimalist interface with black and gray board design
- **Customizable Experience**: Adjust difficulty, switch sides, and toggle analysis features
- **Undo/Redo Moves**: Easily take back moves or replay previously undone moves
- **Real-time Analysis**: View the engine's evaluation and thinking process
- **Opening Book Support**: Use Polyglot opening books for more varied and stronger play
- **Opening Repertoire**: Choose from different playing styles and learn from game results
- **Opening Traps**: Surprise your opponent with tricky opening variations
- **Position Caching**: Transposition table for faster evaluation of repeated positions
- **Advanced Search**: Alpha-beta pruning with move ordering for stronger play
- **Tactical Awareness**: Quiescence search for accurate evaluation of tactical positions
- **Search Optimization**: Null-move pruning for faster search and deeper analysis
- **Machine Learning**: Adaptive evaluation that improves from game results
- **Positional Understanding**: Advanced evaluation of pawn structure, king safety, and mobility
- **Complete Chess Rules**: Full implementation of chess rules including castling, en passant, promotion, and game-ending conditions

## 🖼️ Screenshots

*[Screenshots will be added soon]*

## 🔧 Requirements

- Python 3.7+
- Dependencies (automatically installed with instructions below):
  - pygame==2.5.2
  - python-chess==1.9.4

## 📦 Installation

### Option 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/chess-ai-sunfish.git
cd chess-ai-sunfish

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install as a package (for development)
pip install -e .
```

### Option 2: Download ZIP

1. Download the ZIP file from the GitHub repository
2. Extract the contents to a folder of your choice
3. Open a command prompt or terminal in that folder
4. Follow the dependency installation steps above

## 🚀 How to Play

### Graphical Interface

1. Run the main script:

```bash
python main.py
```

2. **Game Controls**:
   - **Mouse**: Click on a piece to select it, then click on a destination square to move
   - **R key**: Reset the game
   - **S key**: Switch sides (play as black or white)
   - **Number keys 1-9**: Adjust difficulty (1 is easiest, 9 is hardest)
   - **A key**: Toggle the analysis panel
   - **Z key or Left Arrow**: Undo move
   - **Y key or Right Arrow**: Redo move

3. The game automatically detects checkmate, stalemate, and other game-ending conditions.

### Text-Based Interface

For those who prefer a command-line interface or want to test the engine without graphics:

1. Run the text-based interface:

```bash
python text_chess.py
```

2. **Commands**:
   - Enter moves in UCI format (e.g., `e2e4`) or algebraic notation (e.g., `e4`, `Nf3`)
   - `help`: Show available commands
   - `board`: Redraw the board
   - `resign`: Resign the current game
   - `new`: Start a new game
   - `flip`: Switch sides with the computer
   - `level [1-20]`: Set difficulty level
   - `hint`: Get a move suggestion
   - `eval`: Show position evaluation
   - `book on`: Enable the opening book
   - `book off`: Disable the opening book
   - `book status`: Show opening book status
   - `cache on`: Enable position caching (transposition table)
   - `cache off`: Disable position caching
   - `cache status`: Show cache statistics
   - `search on`: Enable alpha-beta search algorithm
   - `search off`: Disable alpha-beta search (use simple search)
   - `search status`: Show search algorithm status
   - `tactical on`: Enable quiescence search for tactical positions
   - `tactical off`: Disable quiescence search
   - `tactical status`: Show quiescence search status
   - `pruning on`: Enable null-move pruning for faster search
   - `pruning off`: Disable null-move pruning
   - `pruning status`: Show null-move pruning status
   - `positional on`: Enable advanced positional evaluation
   - `positional off`: Disable advanced positional evaluation (use simple material counting)
   - `positional status`: Show positional evaluation status
   - `style solid`: Use solid, defensive opening repertoire
   - `style aggressive`: Use aggressive, attacking opening repertoire
   - `style tricky`: Use tricky, surprising opening repertoire with traps
   - `style balanced`: Use balanced, standard opening repertoire
   - `opening stats`: Show opening repertoire statistics
   - `undo` or `u`: Undo the last move
   - `redo` or `r`: Redo a previously undone move
   - `learn on`: Enable machine learning system
   - `learn off`: Disable machine learning system
   - `learn status`: Show learning system statistics
   - `result [1/0.5/0]`: Record game result (1=white win, 0.5=draw, 0=black win)
   - `learn`: Process recorded positions and learn from the game
   - `quit`: Exit the program

## 🔍 Analysis Panel

The analysis panel shows:
- Current position evaluation
- Top moves considered by the engine
- Thinking time

Toggle it on/off with the 'A' key during gameplay.

## 📚 Opening Book

The chess AI supports Polyglot opening books for stronger and more varied play in the opening phase.

### Downloading an Opening Book

Run the provided script to download a sample opening book:

```bash
python download_opening_book.py
```

This will download a Polyglot opening book file to the `chess_ai/books` directory.

### Using the Opening Book

- **In the GUI**: Press the 'B' key to toggle the opening book on/off
- **In the CLI**: Use the following commands:
  - `book on`: Enable the opening book
  - `book off`: Disable the opening book
  - `book status`: Show the current opening book status

When the opening book is enabled, the engine will use book moves for the opening phase of the game, resulting in more varied and stronger play.

## 💾 Position Caching

The chess AI uses a transposition table to cache position evaluations, significantly improving performance when positions are repeated or reached through different move orders.

### Using Position Caching

- **In the GUI**: Press the 'C' key to toggle position caching on/off
- **In the CLI**: Use the following commands:
  - `cache on`: Enable position caching
  - `cache off`: Disable position caching
  - `cache status`: Show cache statistics

Position caching is particularly effective in the middlegame and endgame, where the same positions are often evaluated multiple times during the search process.

## 🧠 Advanced Search

The chess AI uses alpha-beta pruning with move ordering to search more efficiently and play stronger moves.

### Using Advanced Search

- **In the GUI**: Press the 'S' key to toggle alpha-beta search on/off
- **In the CLI**: Use the following commands:
  - `search on`: Enable alpha-beta search
  - `search off`: Disable alpha-beta search (use simple search)
  - `search status`: Show search algorithm statistics

When alpha-beta search is enabled, the engine can look deeper into the position and find stronger moves. The search depth automatically adjusts based on the difficulty level.

## 🎯 Tactical Awareness

The chess AI uses quiescence search to accurately evaluate tactical positions with captures and checks.

### Using Quiescence Search

- **In the GUI**: Press the 'Q' key to toggle quiescence search on/off
- **In the CLI**: Use the following commands:
  - `tactical on`: Enable quiescence search
  - `tactical off`: Disable quiescence search
  - `tactical status`: Show quiescence search statistics

Quiescence search prevents the "horizon effect" by continuing to search captures and checks beyond the regular search depth. This helps the engine avoid tactical blunders and find tactical opportunities.

## 🚀 Search Optimization

The chess AI uses null-move pruning to search deeper by skipping certain moves in positions where one side is likely ahead.

### Using Null-Move Pruning

- **In the GUI**: Press the 'N' key to toggle null-move pruning on/off
- **In the CLI**: Use the following commands:
  - `pruning on`: Enable null-move pruning
  - `pruning off`: Disable null-move pruning
  - `pruning status`: Show null-move pruning statistics

Null-move pruning significantly speeds up the search by allowing the engine to skip certain branches that are unlikely to be better than the current best move. This optimization is automatically disabled in endgame positions where it could lead to incorrect evaluations.

## 🧠 Machine Learning

The chess AI uses a simple machine learning system to adapt and improve its evaluation based on game results.

### Using Machine Learning

- **In the GUI**: Press the 'L' key to toggle the learning system on/off
- **In the CLI**: Use the following commands:
  - `learn on`: Enable the learning system
  - `learn off`: Disable the learning system
  - `learn status`: Show learning statistics
  - `result [1/0.5/0]`: Record a game result (1=white win, 0.5=draw, 0=black win)
  - `learn`: Process recorded positions and learn from the game

The learning system records positions during play and adjusts their evaluations based on game outcomes. Over time, the engine learns which positions lead to favorable results and improves its play accordingly. The system automatically saves learning data between sessions.

## 📊 Positional Understanding

The chess AI uses advanced positional evaluation to make stronger moves beyond simple material counting.

### Using Positional Evaluation

- **In the GUI**: Press the 'P' key to toggle positional evaluation on/off
- **In the CLI**: Use the following commands:
  - `positional on`: Enable advanced positional evaluation
  - `positional off`: Disable advanced positional evaluation
  - `positional status`: Show positional evaluation status

When positional evaluation is enabled, the engine considers several important chess concepts:

- **Pawn Structure**: Evaluates isolated, doubled, backward, and passed pawns
- **King Safety**: Analyzes pawn shields and piece attacks near the king
- **Piece Mobility**: Counts the number of legal moves for each piece
- **Piece Coordination**: Evaluates bishop pairs, knights on outposts, and rooks on open files

These factors combine to give the engine a deeper understanding of chess positions, leading to stronger play.

## 📚 Opening Repertoire

The chess AI features a sophisticated opening repertoire system with different playing styles and opening traps.

### Opening Styles

You can choose from four different opening styles:

- **Solid**: Conservative, defensive openings that prioritize safety and structure
- **Aggressive**: Attacking openings that seek tactical opportunities and piece activity
- **Tricky**: Surprising openings with potential traps to catch opponents off-guard
- **Balanced**: Standard, well-rounded openings suitable for all situations

### Using Opening Styles

- **In the GUI**: Press Ctrl+1 through Ctrl+4 to select a style (1=Solid, 2=Aggressive, 3=Tricky, 4=Balanced)
- **In the CLI**: Use the following commands:
  - `style solid`: Use solid, defensive opening repertoire
  - `style aggressive`: Use aggressive, attacking opening repertoire
  - `style tricky`: Use tricky, surprising opening repertoire with traps
  - `style balanced`: Use balanced, standard opening repertoire
  - `opening stats`: Show opening repertoire statistics

### Opening Traps

When using the 'tricky' style, the engine may employ opening traps like the Stafford Gambit, Fried Liver Attack, or Budapest Gambit to surprise opponents. These traps are also occasionally used in other styles.

### Adaptive Repertoire

The opening repertoire system learns from game results, gradually adjusting its preferences based on success rates. Openings that lead to wins are played more frequently, while unsuccessful lines are avoided.

## ⚙️ Customization

You can modify the following aspects of the game:

- **Board Size and Appearance**: Edit the constants in `chess_ai/config/settings.py`
- **Default Difficulty Level**: Change the `DEFAULT_DIFFICULTY` value in `chess_ai/config/settings.py`
- **AI Behavior**: Modify the evaluation functions in `chess_ai/engine/sunfish_wrapper.py`
- **Text Interface**: Customize the text display in `chess_ai/cli/text_interface.py`

## 🗺️ Development Roadmap

This project follows a structured development plan:

- **Main Project Roadmap**: See [RoadMaps/ROADMAP.md](RoadMaps/ROADMAP.md) for the overall project plan
- **AI Bot Development**: See [RoadMaps/AI_BOT_ROADMAP.md](RoadMaps/AI_BOT_ROADMAP.md) for the detailed AI enhancement plan

These roadmaps outline the current progress and future development goals for the project.

## 🧪 Testing

### Installation Verification

To verify that your installation is working correctly, run the test script:

```bash
python test_installation.py
```

This script will check:
- If all required dependencies are installed
- If all necessary files are present
- If the chess engine can be initialized

### Comprehensive Testing

For more thorough testing of all components, run the test suite:

```bash
python run_tests.py
```

This will run all unit tests and integration tests, including:
- Chess engine functionality tests
- Game logic and rules tests
- Text interface tests
- Main application tests
- Installation script tests

### Manual Testing

Once the automated tests pass, you can run the game and test it manually:

```bash
# Run the graphical interface
python main.py

# Or run the text-based interface
python text_chess.py

# Try making moves and using keyboard controls
# Test different difficulty levels
```

## ❓ Troubleshooting

### Common Issues

1. **Game doesn't start**:
   - Ensure Python 3.7+ is installed
   - Verify all dependencies are installed with `pip list`
   - Check console for error messages

2. **Graphics issues**:
   - Update your graphics drivers
   - Try running in a window rather than fullscreen

3. **Engine errors**:
   - Make sure `chess_ai/engine/sunfish.py` exists
   - Check that the file permissions allow execution
   - Try using the fallback engine by setting `engine = FallbackEngine()` in your code

## 🧠 About Sunfish

Sunfish is a simple yet powerful chess engine written in Python. It's designed to be minimalistic yet effective, making it perfect for educational purposes and lightweight applications. The original Sunfish was created by Thomas Dybdahl Ahle and is available at [github.com/thomasahle/sunfish](https://github.com/thomasahle/sunfish).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Sunfish Chess Engine](https://github.com/thomasahle/sunfish) by Thomas Dybdahl Ahle
- [python-chess](https://python-chess.readthedocs.io/) library
- [Pygame](https://www.pygame.org/) library

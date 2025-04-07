# Chess AI with Sunfish

![Chess Game](https://img.shields.io/badge/Chess-Game-brightgreen)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

A modern, customizable chess application with an integrated AI opponent powered by the Sunfish chess engine. This project features a clean graphical interface built with Pygame and leverages the python-chess library for game logic and move validation.

## 🎮 Features

- **Intelligent AI Opponent**: Play against the Sunfish chess engine with adjustable difficulty levels
- **Interactive GUI**: Clean, minimalist interface with black and gray board design
- **Customizable Experience**: Adjust difficulty, switch sides, and toggle analysis features
- **Real-time Analysis**: View the engine's evaluation and thinking process
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
```

### Option 2: Download ZIP

1. Download the ZIP file from the GitHub repository
2. Extract the contents to a folder of your choice
3. Open a command prompt or terminal in that folder
4. Follow the dependency installation steps above

## 🚀 How to Play

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

3. The game automatically detects checkmate, stalemate, and other game-ending conditions.

## 🔍 Analysis Panel

The analysis panel shows:
- Current position evaluation
- Top moves considered by the engine
- Thinking time

Toggle it on/off with the 'A' key during gameplay.

## ⚙️ Customization

You can modify the following aspects of the game:

- **Board Size and Appearance**: Edit the constants at the top of `main.py`
- **Default Difficulty Level**: Change the `engine.set_difficulty()` value in `main.py`
- **AI Behavior**: Modify the evaluation functions in `sunfish_wrapper.py`

## 🧪 Testing

To verify that your installation is working correctly, run the test script:

```bash
python test_installation.py
```

This script will check:
- If all required dependencies are installed
- If all necessary files are present
- If the chess engine can be initialized

Once the test passes, you can run the game and test it manually:

```bash
# Run the game
python main.py

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
   - Make sure `sunfish.py` is in the project directory
   - Check that the file permissions allow execution

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

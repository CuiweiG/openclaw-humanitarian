# Recording the Demo GIF

## Option 1: asciinema + svg-term (recommended)

```bash
# Install
pip install asciinema
npm install -g svg-term-cli

# Record
asciinema rec demo.cast -c "python src/demo.py"

# Convert to SVG (better than GIF, smaller file)
svg-term --in demo.cast --out docs/demo.svg --window --width 80 --height 30

# Or convert to GIF
# npm install -g asciicast2gif
# asciicast2gif demo.cast docs/demo.gif
```

## Option 2: terminalizer

```bash
npm install -g terminalizer
terminalizer record demo --command "python src/demo.py"
terminalizer render demo -o docs/demo.gif
```

## Embedding in README

After recording, uncomment this line in README.md:

```markdown
![Demo](docs/demo.svg)
```

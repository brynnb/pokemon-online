# Pokémon Online

![pokeonline](https://github.com/user-attachments/assets/e4602729-29bb-4ee4-94f6-446c90dd2a89)

This project extracts game data and graphics from the original Pokemon Red/Blue GameBoy game, recreates and reimagines the original game engine, and makes it online, dynamic, and multiplayer. The general concept is to have the game world and NPCs as true to the original as possible while also adding new player-owned areas of land (effectively filling in the massive gaps the original game world had), reimagining some of the more antiquated game mechanics (the original combat mechanic is a little old and boring 30 years later), and making it online and social.

This project uses extensive python scripts, node.js for the server, and [Phaser](https://phaser.io/) for the browser-based game engine.

This project does not meaningfully distribute any copywritten material. It pulls in the disassembled code and data from the [pokered](https://github.com/pret/pokered) repo and builds database and sprites and graphics from that. If this project gains traction, I would have people load this client-side so this game server is not distributing any copywritten material.

This project relies heavily on my other project, which is dedicated to the data and graphics extraction process: [pokemon-database-exporter](https://github.com/brynnb/pokemon-database-exporter). This is currently a little tangled into this project and I've not yet fully separated it, but it will happen eventually.

## Installation

### Cloning the Repository

```bash
# Clone with submodules (recommended)
git clone https://github.com/brynnb/pokemon-online.git --recurse-submodules

# OR clone normally and then initialize submodules
git clone https://github.com/brynnb/pokemon-online.git
cd pokemon-online
git submodule update --init --recursive
```

### Installing Dependencies

```bash
npm install
npm run export
```

## Usage

### Running the Client (Vite Development Server)

```bash
cd pokemon-phaser
npm install
npm run dev
```

This will start the Vite development server for the client on port 8080.

### Building the Client (Production)

If you want to build the client for production:

```bash
cd pokemon-phaser
npm run build
```

This will create a `dist` directory in the pokemon-phaser folder with the compiled assets.

### Running the Server (Node.js)

In a separate terminal, run the server:

```bash
# From the project root
npm run dev
```

This will start the Node.js server on port 3000.

### Running Both with a Single Command

Alternatively, you can run both the client and server with a single command:

```bash
npm run start:all
```

### Troubleshooting

If you encounter a "webfontloader" dependency error when building the client:

```bash
cd pokemon-phaser
npm install webfontloader
npm run build
```

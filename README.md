# Pokémon Online

![pokeonline](https://github.com/user-attachments/assets/e4602729-29bb-4ee4-94f6-446c90dd2a89)

This project extracts game data and graphics from the original Pokemon Red/Blue GameBoy game, recreates and reimagines the original game engine, and makes it online, dynamic, and multiplayer. The general concept is to have the game world and NPCs as true to the original as possible while also adding new player-owned areas of land (effectively filling in the massive gaps the original game world had), reimagining some of the more antiquated game mechanics (the original combat mechanic is a little old and boring 30 years later), and making it online and social. 

This project uses extensive python scripts, node.js for the server, and [Phaser](https://phaser.io/) for the browser-based game engine. 

This project does not meaningfully distribute any copywritten material. It pulls in the disassembled code and data from the [pokered](https://github.com/pret/pokered) repo and builds database and sprites and graphics from that. If this project gains traction, I would have people load this client-side so this game server is not distributing any copywritten material.

This project relies heavily on my other project, which is dedicated to the data and graphics extraction process: [pokemon-database-exporter](https://github.com/brynnb/pokemon-database-exporter)

## Installation


   ```bash
   npm install
   npm run export
   ```

## Usage

   ```bash
   cd pokemon-phaser
   npm run dev
   ```

   ```bash
   node pokemon-phaser/server.js
   ```

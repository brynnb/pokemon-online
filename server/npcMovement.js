const WebSocket = require("ws");

// Constants for movement directions (based on the original Game Boy constants)
const DIRECTIONS = {
  UP: "UP",
  DOWN: "DOWN",
  LEFT: "LEFT",
  RIGHT: "RIGHT",
};

// Constants for movement types
const MOVEMENT_TYPES = {
  UP_DOWN: "UP_DOWN",
  LEFT_RIGHT: "LEFT_RIGHT",
  ANY_DIR: "ANY_DIR",
};

// Constants for sprite frames
const SPRITE_FRAMES = {
  DOWN: 0, // 0th frame for facing down
  UP: 1, // 1st frame for facing up
  LEFT: 2, // 2nd frame for facing left
  RIGHT: 2, // 2nd frame for facing right (mirrored)
  WALK_DOWN: 3, // 3rd frame for walking down
  WALK_UP: 4, // 4th frame for walking up
  WALK_LEFT: 5, // 5th frame for walking left
  WALK_RIGHT: 5, // 5th frame for walking right (mirrored)
};

// Class to manage walking NPCs
class NPCMovementManager {
  constructor(db, wss) {
    this.db = db;
    this.wss = wss;
    this.walkingNPCs = []; // Array to store all walking NPCs
    this.npcStates = new Map(); // Map to store state for each NPC by ID
    this.walkInterval = null;
    this.animationInterval = null;
  }

  // Initialize by finding all walking NPCs
  async initialize() {
    try {
      // Get all walking NPCs from the database
      this.walkingNPCs = await this.getAllWalkingNPCs();

      if (this.walkingNPCs.length > 0) {
        console.log(`Found ${this.walkingNPCs.length} walking NPCs`);

        // Initialize state for each NPC
        this.walkingNPCs.forEach((npc) => {
          this.initializeNPCState(npc);
        });

        // Start the movement and animation loops
        this.startMovementLoop();
        this.startAnimationLoop();
      } else {
        console.log("No walking NPCs found");
      }
    } catch (err) {
      console.error("Error initializing NPC movement manager:", err);
      throw err;
    }
  }

  // Initialize the state for a single NPC
  initializeNPCState(npc) {
    // Default to DOWN direction if not specified
    const direction = npc.action_direction || DIRECTIONS.DOWN;

    // Create a state object for this NPC
    const state = {
      id: npc.id,
      x: npc.x,
      y: npc.y,
      map_id: npc.map_id,
      direction,
      frame: this.updateInitialFrameForDirection(npc, direction),
      movementType: MOVEMENT_TYPES.ANY_DIR, // Default to any direction
      originalX: npc.x, // Store original position for reset
      originalY: npc.y,
      originalDirection: direction,
      lastMoveTime: Date.now(),
      isMoving: false,
    };

    // Store the state in the map
    this.npcStates.set(npc.id, state);
  }

  // Get all NPCs with action_type = 'WALK' from the database
  async getAllWalkingNPCs() {
    try {
      return await this.db.getWalkingNPCs();
    } catch (err) {
      console.error("Error getting walking NPCs:", err);
      return [];
    }
  }

  // Start the movement loop
  startMovementLoop() {
    // Clear any existing interval
    if (this.walkInterval) {
      clearInterval(this.walkInterval);
    }

    // Set up a new interval to move NPCs every 2 seconds
    this.walkInterval = setInterval(() => {
      this.updateAllNPCMovements();
    }, 2000);
  }

  // Start the animation loop
  startAnimationLoop() {
    // Clear any existing interval
    if (this.animationInterval) {
      clearInterval(this.animationInterval);
    }

    // Set up a new interval to update animations every 200ms
    this.animationInterval = setInterval(() => {
      this.updateAllNPCAnimations();
    }, 200);
  }

  // Update animations for all NPCs
  updateAllNPCAnimations() {
    this.walkingNPCs.forEach((npc) => {
      const state = this.npcStates.get(npc.id);
      if (state) {
        this.updateNPCAnimation(npc, state);
      }
    });
  }

  // Update the animation frame for a single NPC
  updateNPCAnimation(npc, state) {
    // Only animate if the NPC is currently moving
    if (state.isMoving) {
      // Toggle between standing and walking frames based on the direction
      switch (state.direction) {
        case DIRECTIONS.DOWN:
          state.frame =
            state.frame === SPRITE_FRAMES.DOWN
              ? SPRITE_FRAMES.WALK_DOWN
              : SPRITE_FRAMES.DOWN;
          break;
        case DIRECTIONS.UP:
          state.frame =
            state.frame === SPRITE_FRAMES.UP
              ? SPRITE_FRAMES.WALK_UP
              : SPRITE_FRAMES.UP;
          break;
        case DIRECTIONS.LEFT:
          state.frame =
            state.frame === SPRITE_FRAMES.LEFT
              ? SPRITE_FRAMES.WALK_LEFT
              : SPRITE_FRAMES.LEFT;
          break;
        case DIRECTIONS.RIGHT:
          state.frame =
            state.frame === SPRITE_FRAMES.RIGHT
              ? SPRITE_FRAMES.WALK_RIGHT
              : SPRITE_FRAMES.RIGHT;
          break;
      }

      // Broadcast the updated frame
      this.broadcastNPCUpdate(npc);
    }
  }

  // Update movements for all NPCs
  updateAllNPCMovements() {
    this.walkingNPCs.forEach((npc) => {
      this.updateSingleNPCMovement(npc);
    });
  }

  // Update the movement for a single NPC
  async updateSingleNPCMovement(npc) {
    try {
      const state = this.npcStates.get(npc.id);
      if (!state) return;

      // Only move if enough time has passed since the last move
      const now = Date.now();
      if (now - state.lastMoveTime < 1000) {
        return;
      }

      // Determine which direction to move
      const direction = this.determineMovementDirection(npc);
      if (!direction) {
        // If no direction is available, just update the standing frame
        this.updateStandingFrame(npc, state.direction);
        return;
      }

      // Check if the NPC can move in this direction
      const canMove = await this.canMoveInDirection(npc, direction);
      if (canMove) {
        // Set the NPC as moving
        state.isMoving = true;

        // Move the NPC
        this.moveNPC(npc, direction);

        // Update the last move time
        state.lastMoveTime = now;

        // After a short delay, set the NPC as not moving
        setTimeout(() => {
          const currentState = this.npcStates.get(npc.id);
          if (currentState) {
            currentState.isMoving = false;
            this.updateStandingFrame(npc, direction);
          }
        }, 500);
      } else {
        // If the NPC can't move, just update the standing frame
        this.updateStandingFrame(npc, direction);
      }
    } catch (err) {
      console.error(`Error updating NPC ${npc.id} movement:`, err);
    }
  }

  // Update the standing frame for an NPC
  updateStandingFrame(npc, direction) {
    const state = this.npcStates.get(npc.id);
    if (!state) return;

    // Update the direction
    state.direction = direction;

    // Set the appropriate standing frame
    switch (direction) {
      case DIRECTIONS.DOWN:
        state.frame = SPRITE_FRAMES.DOWN;
        break;
      case DIRECTIONS.UP:
        state.frame = SPRITE_FRAMES.UP;
        break;
      case DIRECTIONS.LEFT:
        state.frame = SPRITE_FRAMES.LEFT;
        break;
      case DIRECTIONS.RIGHT:
        state.frame = SPRITE_FRAMES.RIGHT;
        break;
    }

    // Broadcast the update
    this.broadcastNPCUpdate(npc);
  }

  // Update the initial frame based on the direction
  updateInitialFrameForDirection(npc, direction) {
    switch (direction) {
      case DIRECTIONS.DOWN:
        return SPRITE_FRAMES.DOWN;
      case DIRECTIONS.UP:
        return SPRITE_FRAMES.UP;
      case DIRECTIONS.LEFT:
        return SPRITE_FRAMES.LEFT;
      case DIRECTIONS.RIGHT:
        return SPRITE_FRAMES.RIGHT;
      default:
        return SPRITE_FRAMES.DOWN; // Default to down
    }
  }

  // Determine which direction the NPC should move
  determineMovementDirection(npc) {
    const state = this.npcStates.get(npc.id);
    if (!state) return null;

    // For now, just pick a random direction
    const directions = Object.values(DIRECTIONS);
    const randomIndex = Math.floor(Math.random() * directions.length);
    const newDirection = directions[randomIndex];

    // Update the state with the new direction
    state.direction = newDirection;

    return newDirection;
  }

  // Check if the NPC can move in a specific direction
  async canMoveInDirection(npc, direction) {
    const state = this.npcStates.get(npc.id);
    if (!state) return false;

    // Calculate the new position
    let newX = state.x;
    let newY = state.y;

    switch (direction) {
      case DIRECTIONS.UP:
        newY--;
        break;
      case DIRECTIONS.DOWN:
        newY++;
        break;
      case DIRECTIONS.LEFT:
        newX--;
        break;
      case DIRECTIONS.RIGHT:
        newX++;
        break;
    }

    try {
      // Check if there's a tile at the new position
      const tile = await this.getTileAt(newX, newY, state.map_id);
      if (!tile) {
        return false;
      }

      // Check if there's a collision at the new position
      const collision = await this.checkCollision(
        newX,
        newY,
        state.map_id,
        npc.id
      );
      if (collision) {
        return false;
      }

      return true;
    } catch (err) {
      console.error(
        `Error checking if NPC ${npc.id} can move to (${newX}, ${newY}):`,
        err
      );
      return false;
    }
  }

  // Get the tile at a specific position
  async getTileAt(x, y, mapId) {
    try {
      return await this.db.getTileAt(x, y, mapId);
    } catch (err) {
      console.error(`Error getting tile at (${x}, ${y}) on map ${mapId}:`, err);
      return null;
    }
  }

  // Check if there's a collision at a specific position
  async checkCollision(x, y, mapId, npcId) {
    try {
      return await this.db.checkCollision(x, y, mapId, npcId);
    } catch (err) {
      console.error(
        `Error checking collision at (${x}, ${y}) on map ${mapId}:`,
        err
      );
      return true; // Assume collision on error
    }
  }

  // Move the NPC in a specific direction
  moveNPC(npc, direction) {
    const state = this.npcStates.get(npc.id);
    if (!state) return;

    // Update the position based on the direction
    switch (direction) {
      case DIRECTIONS.UP:
        state.y--;
        break;
      case DIRECTIONS.DOWN:
        state.y++;
        break;
      case DIRECTIONS.LEFT:
        state.x--;
        break;
      case DIRECTIONS.RIGHT:
        state.x++;
        break;
    }

    // Update the NPC object with the new position
    npc.x = state.x;
    npc.y = state.y;

    // Broadcast the update
    this.broadcastNPCUpdate(npc);
  }

  // Broadcast an NPC update to all connected clients
  broadcastNPCUpdate(npc) {
    const state = this.npcStates.get(npc.id);
    if (!state || !this.wss) return;

    // Determine if the sprite should be flipped horizontally
    // For RIGHT direction, we need to flip the sprite
    const flipX = state.direction === DIRECTIONS.RIGHT;

    // Create the update message
    const updateMessage = {
      type: "npcUpdate",
      npc: {
        id: npc.id,
        x: state.x,
        y: state.y,
        map_id: state.map_id,
        sprite_name: npc.sprite_name,
        name: npc.name,
        direction: state.direction,
        frame: state.frame,
        isMoving: state.isMoving,
        flipX: flipX,
      },
    };

    // Broadcast to all connected clients
    this.wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(updateMessage));
      }
    });
  }

  // Reset all NPCs to their original positions
  resetToOriginalPosition() {
    this.walkingNPCs.forEach((npc) => {
      const state = this.npcStates.get(npc.id);
      if (state) {
        // Reset the position and direction
        state.x = state.originalX;
        state.y = state.originalY;
        state.direction = state.originalDirection;
        state.frame = this.updateInitialFrameForDirection(
          npc,
          state.originalDirection
        );
        state.isMoving = false;

        // Update the NPC object
        npc.x = state.x;
        npc.y = state.y;

        // Broadcast the update
        this.broadcastNPCUpdate(npc);
      }
    });
  }

  // Reset a specific NPC to its original position
  resetNPCToOriginalPosition(npcId) {
    const npc = this.walkingNPCs.find((n) => n.id === npcId);
    const state = this.npcStates.get(npcId);

    if (npc && state) {
      // Reset the position and direction
      state.x = state.originalX;
      state.y = state.originalY;
      state.direction = state.originalDirection;
      state.frame = this.updateInitialFrameForDirection(
        npc,
        state.originalDirection
      );
      state.isMoving = false;

      // Update the NPC object
      npc.x = state.x;
      npc.y = state.y;

      // Broadcast the update
      this.broadcastNPCUpdate(npc);
      return true;
    }

    return false;
  }

  // Stop the movement and animation loops
  stopMovementLoop() {
    if (this.walkInterval) {
      clearInterval(this.walkInterval);
      this.walkInterval = null;
    }

    if (this.animationInterval) {
      clearInterval(this.animationInterval);
      this.animationInterval = null;
    }

    console.log("NPC movement loops stopped");
  }

  // Get an NPC by ID
  async getNPCById(npcId) {
    try {
      return await this.db.getNPCById(npcId);
    } catch (err) {
      console.error(`Error getting NPC ${npcId}:`, err);
      return null;
    }
  }

  // Get all NPCs
  getAllNPCs() {
    return this.walkingNPCs;
  }

  // Get a specific NPC by ID
  getNPC(npcId) {
    return this.walkingNPCs.find((npc) => npc.id === npcId);
  }
}

module.exports = NPCMovementManager;

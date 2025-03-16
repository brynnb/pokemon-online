const { spawn } = require("child_process");
const path = require("path");

// Start the client (Vite development server)
const clientProcess = spawn("npm", ["run", "client"], {
  stdio: "inherit",
  shell: true,
});

// Start the API server with nodemon for auto-restarting
const serverProcess = spawn("npm", ["run", "dev"], {
  stdio: "inherit",
  shell: true,
});

// Handle process termination
process.on("SIGINT", () => {
  console.log("Shutting down development servers...");
  clientProcess.kill();
  serverProcess.kill();
  process.exit(0);
});

console.log("Development servers started with auto-reloading:");
console.log("- Client (Vite server): http://localhost:8080");
console.log(
  "- API server: http://localhost:3000 (auto-reloads on changes in server/)"
);
console.log("Press Ctrl+C to stop both servers.");

# PopcornBot

A Discord bot that manages Popcorn Initiative for tabletop role-playing games (TTRPGs). Popcorn Initiative allows for dynamic turn management where players pass the turn to each other, creating a more fluid and engaging gameplay experience.

## Features

- **Guild and Channel Isolation**: Run separate initiatives in different guilds and channels simultaneously
- **Player Pool Management**: Maintain persistent player pools that GMs can manage
- **Dynamic Turn Passing**: Players pass turns to each other, with automatic initiative cycling
- **Role-Based Permissions**: GM and Popcorn Manager roles control initiative management
- **Comprehensive Validation**: All user inputs are validated to ensure security and reliability

## Discord Bot Permissions Required

The bot needs the following Discord permissions to function properly:

- **Use Application Commands** (Required): Needed for slash commands to work
- **Send Messages** (Required): Bot must be able to send messages to respond to commands
- **View Channels** (Required): Bot must be able to see and interact in channels
- **Embed Links** (Optional): Recommended for better formatted status messages
- **Read Message History** (Optional): May be useful for context
- **Use External Emojis** (Optional): For enhanced status displays

### Minimum Permissions Integer
The minimum permissions integer for this bot is: `274878024704`

## Server Role Setup

Before using the bot, server administrators need to create the following roles:

1. **GM Role**: Create a role named exactly "GM" for Game Masters
2. **Popcorn Manager Role**: Create a role named exactly "Popcorn Manager" for managers

These roles should be assigned to users who need to manage player pools and control initiatives. Users without these roles can only use `/popcorn next` when it's their turn.

## Installation

### Prerequisites

- Python 3.9 or higher
- A Discord bot application and token (get one from [Discord Developer Portal](https://discord.com/developers/applications))
- Discord server where you have administrator permissions

### Setup Steps

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd PopcornBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `.env.example` to `.env` (if it exists, or create it)
   - Add your Discord bot token and client ID:
     ```
     DISCORD_BOT_TOKEN=your_bot_token_here
     DISCORD_CLIENT_ID=your_client_id_here
     ```

4. **Invite the bot to your server**
   - Go to the Discord Developer Portal
   - Select your application
   - Go to OAuth2 > URL Generator
   - Select scopes: `bot`, `applications.commands`
   - Select bot permissions (see "Discord Bot Permissions Required" above)
   - Copy the generated URL and open it in your browser
   - Select your server and authorize

5. **Run the bot**
   ```bash
   python bot.py
   ```

## Docker Deployment

PopcornBot is designed to run in a fully isolated Docker container. All bot management is done through Discord slash commands - no file system dependencies required.

### Prerequisites for Docker

- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher (optional, for easier deployment)

### Building the Docker Image

```bash
docker build -t popcornbot .
```

### Running with Docker

1. **Create a `.env` file** (in the same directory as your Dockerfile):
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   DISCORD_CLIENT_ID=your_client_id_here
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     --name popcornbot \
     --restart unless-stopped \
     --env-file .env \
     popcornbot
   ```

3. **View logs**:
   ```bash
   docker logs -f popcornbot
   ```

4. **Stop the bot**:
   ```bash
   docker stop popcornbot
   ```

5. **Start the bot again**:
   ```bash
   docker start popcornbot
   ```

6. **Remove the container**:
   ```bash
   docker stop popcornbot
   docker rm popcornbot
   ```

### Running with Docker Compose (Recommended)

Docker Compose provides easier management and automatic restarts.

1. **Create a `.env` file**:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   DISCORD_CLIENT_ID=your_client_id_here
   ```

2. **Start the bot**:
   ```bash
   docker-compose up -d
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

4. **Stop the bot**:
   ```bash
   docker-compose down
   ```

5. **Restart the bot**:
   ```bash
   docker-compose restart
   ```

### Docker Container Isolation

The PopcornBot container is fully isolated:
- Runs as non-root user for security
- No file system dependencies - all state is in-memory
- All management done via Discord slash commands
- Logs go to stdout/stderr (visible via `docker logs`)
- Container restart clears all initiative state (by design)
- No persistent volumes required

### Updating the Bot

To update the bot with new code:

1. **Pull latest code**:
   ```bash
   git pull
   ```

2. **Rebuild the image**:
   ```bash
   docker-compose build
   # or
   docker build -t popcornbot .
   ```

3. **Restart the container**:
   ```bash
   docker-compose up -d --force-recreate
   # or
   docker stop popcornbot && docker rm popcornbot
   docker run -d --name popcornbot --restart unless-stopped --env-file .env popcornbot
   ```

## Command Reference

### Player Pool Management Commands (GM/Popcorn Manager only)

#### `/popcorn pool add <user>`
Adds a user to the persistent player pool.

- **Required Role**: GM or Popcorn Manager
- **Parameters**:
  - `user`: The Discord user to add to the pool

#### `/popcorn pool remove <user>`
Removes a user from the player pool.

- **Required Role**: GM or Popcorn Manager
- **Parameters**:
  - `user`: The Discord user to remove from the pool

#### `/popcorn pool list`
Lists all players currently in the player pool.

- **Required Role**: GM or Popcorn Manager

#### `/popcorn pool clear`
Clears the entire player pool.

- **Required Role**: GM or Popcorn Manager

### Initiative Management Commands

#### `/popcorn add <user>`
Adds a user to both the player pool and the current initiative (if running).

- **Required Role**: GM or Popcorn Manager
- **Parameters**:
  - `user`: The Discord user to add

#### `/popcorn start [user]`
Starts the Popcorn Initiative.

- **Required Role**: GM or Popcorn Manager
- **Parameters**:
  - `user` (optional): The user to start with. If not provided, randomly selects from the pool.
- **Behavior**: All players in the pool become participants. The specified user (or a random player) goes first.

#### `/popcorn next [user]`
Passes the turn to the next player.

- **Available to**: Current player OR GM/Popcorn Manager
- **Parameters**:
  - `user` (optional): The specific user to pass to
- **Behavior**:
  - If current player uses without `user`: Randomly selects from remaining participants
  - If current player uses with `user`: Passes to that specific player
  - If GM/Popcorn Manager uses with `user`: Can override and select the next player
  - If last player passes to specific user: Starts a new random initiative with that user going first
  - If pool exhausted: Ends the initiative automatically

#### `/popcorn end`
Manually ends the current initiative.

- **Required Role**: GM or Popcorn Manager

#### `/popcorn clear`
Clears the initiative brackets (resets to empty state).

- **Required Role**: GM or Popcorn Manager

#### `/popcorn status`
Shows the current initiative status including pool, current player, participants, and history.

- **Available to**: Everyone

## How Popcorn Initiative Works

1. **Starting Initiative**: When `/popcorn start` is used, a random player (or specified player) is selected to go first. All players in the pool become participants.

2. **Turn Passing**: The current player uses `/popcorn next` to pass the turn:
   - Without specifying a user: Turn passes randomly to a remaining participant
   - With a specific user: Turn passes to that user if they're in the participants

3. **Initiative Cycling**: When all participants have had their turn, if the last player passes to a specific user, a new initiative automatically starts with that user going first.

4. **Auto-Ending**: If the pool is exhausted and no specific pass is made, the initiative ends automatically.

5. **Guild/Channel Isolation**: Each guild and channel combination maintains its own separate player pool and initiative state.

## Troubleshooting

### Bot doesn't respond to commands
- Check that the bot has "Use Application Commands" permission
- Verify the bot token is correct in your `.env` file
- Make sure commands are synced (check bot logs)

### Permission errors
- Verify you have the "GM" or "Popcorn Manager" role (exact names, case-sensitive)
- Check that the roles exist in your server

### Commands not appearing
- Wait a few minutes for Discord to sync commands globally
- Try restarting the bot
- Check bot logs for sync errors

## Development

### Project Structure

```
PopcornBot/
├── bot.py                 # Main bot entry point
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── commands/
│   ├── __init__.py
│   └── popcorn.py        # Command implementations
├── models/
│   ├── __init__.py
│   └── initiative.py     # Data models
└── helpers/
    ├── __init__.py
    └── validation.py     # Validation helpers
```

### Running in Development

```bash
# Install in development mode
pip install -r requirements.txt

# Run the bot
python bot.py
```

## License

This project is open source. See LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or pull request for any improvements.

## Support

For issues, questions, or feature requests, please open an issue on the repository.

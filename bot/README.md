# Market Bot (C)

A C program that generates simulated market data and sends it via TCP socket.

## Data Format

The bot sends market data in the following format:
```
symbol:price:balance:volume:timestamp
```

Example:
```
AAPL:102.34:10500.50:5678:1714321234
```

## Build & Run

```bash
# Build the bot
make

# Run the bot
./market_bot
```

The bot will:
1. Listen on port 8080 for TCP connections
2. Wait for Python server to connect
3. Generate market data every 1 second
4. Send data to connected client

## Clean

```bash
make clean
```

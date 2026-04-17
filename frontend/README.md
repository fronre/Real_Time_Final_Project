# Trading Dashboard Frontend

A modern, responsive web dashboard that displays real-time trading data via WebSocket connection.

## Features

- **Real-time Updates**: Live market data via WebSocket
- **Price Tracking**: Current price with change indicators
- **Account Balance**: Real-time balance display
- **Volume Monitoring**: Trading volume information
- **Connection Status**: Visual connection indicator
- **Recent Updates List**: Scrollable history of recent trades
- **Responsive Design**: Works on desktop and mobile
- **Animations**: Smooth transitions and price change indicators

## How to Use

1. Open `index.html` in a web browser
2. The dashboard will automatically connect to `ws://localhost:8000/ws`
3. Real-time data will appear once the Python server and C bot are running

## Data Display

- **Price Card**: Shows current price, symbol, and price change
- **Balance Card**: Displays account balance in green
- **Volume Card**: Shows trading volume in blue
- **Recent Updates**: Scrollable list with timestamp, price, and volume

## Visual Indicators

- 🟢 Green: Connected / Price increased
- 🔴 Red: Disconnected / Price decreased
- ⚠️ Yellow: Connection error
- 📊 Blue: Volume information

## Technical Details

- Uses Tailwind CSS for styling
- Vanilla JavaScript with WebSocket API
- Automatic reconnection on connection loss
- Keeps last 50 updates in memory
- Responsive grid layout

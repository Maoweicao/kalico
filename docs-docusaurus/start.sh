#!/bin/bash

echo "Starting Kalico Documentation Site..."
echo ""
echo "Available commands:"
echo "  npm run start      - Start English version"
echo "  npm run start:zh   - Start Chinese version"
echo "  npm run build      - Build for production"
echo ""

cd "$(dirname "$0")"

if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    echo ""
fi

echo "Starting Docusaurus development server..."
echo "Open http://localhost:3000 in your browser"
echo ""
npm run start

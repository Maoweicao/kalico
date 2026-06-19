#!/bin/bash

echo "Building Kalico Documentation Site for production..."
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

echo "Building..."
npm run build
if [ $? -ne 0 ]; then
    echo "Build failed!"
    exit 1
fi

echo ""
echo "Starting production server..."
echo "Open http://localhost:3000 in your browser"
echo "Press Ctrl+C to stop"
echo ""
npm run serve

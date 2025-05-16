# Fake News Detector Frontend

This is the frontend application for the Fake News Detector project.

## Technologies Used

This project is built with:
- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## Running the Application

### Option 1: Using Docker (Recommended)

#### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

#### Starting the Frontend
1. Navigate to the frontend directory:
   ```
   cd fake-news-detector/news-trust-visualizer
   ```

2. Build and start the frontend container:
   ```
   docker-compose up
   ```

3. The frontend will be available at http://localhost:5173

#### Stopping the Frontend
Press `Ctrl+C` in the terminal where the frontend is running, or run:
```
docker-compose down
```

#### Rebuilding the Frontend
If you make changes to the code or dependencies, rebuild the container:
```
docker-compose up --build
```

### Option 2: Manual Setup

#### Prerequisites
- Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

#### Steps
1. Navigate to the frontend directory:
   ```
   cd fake-news-detector/news-trust-visualizer
   ```

2. Install the necessary dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```

4. The frontend will be available at http://localhost:5173

## Connecting to the Backend

By default, the frontend expects the backend API to be running at http://localhost:8000. Make sure the backend is running before using the frontend.

## Development

The Docker setup mounts the current directory into the container, so any changes you make to the source code will be reflected immediately in the running application thanks to Vite's hot module replacement.

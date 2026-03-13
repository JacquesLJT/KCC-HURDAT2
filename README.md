

# KCC HURDAT2 Hurricane Explorer

This project analyzes the **HURDAT2 Atlantic hurricane dataset** and visualizes hurricanes that made **landfall in Florida since 1900**. The application consists of a Python backend responsible for data processing and a modern frontend for interactive visualization.

## Architecture

The project is split into two main components:

### Backend (Python / Flask)

The backend contains the business logic and exposes a small REST API used by the frontend.

On application startup, the API performs the following steps:

1. Loads the **HURDAT2 dataset** from the `data/` directory.
2. Parses the dataset into Python objects.
3. Determines which storms qualify as hurricanes.
4. Determines which hurricanes made landfall in Florida.

Two dataclasses are used to model the storm data:

- **Storm** – represents a full storm system and contains metadata and best track entries.
- **BestTrackEntry** – represents a single observation in the storm track (location, wind speed, pressure, timestamp, etc).

### Landfall Detection

To determine whether a hurricane made landfall in Florida:

1. The **TIGER/Line shapefiles** from the **U.S. Census Bureau** are used for U.S. state boundaries.
2. The shapefile is loaded into **GeoPandas**.
3. The geometry is filtered to only include **Florida**.
4. For each hurricane:
   - Each pair of consecutive best track points is converted into a **line segment**.
   - GeoPandas is used to test whether the segment **intersects the Florida boundary**.
5. The first intersecting segment determines the **date of landfall**.

Once processing is complete, the backend exposes the data through a set of API endpoints.

## API Endpoints

The Flask API provides four endpoints:

### `GET /storms`
Returns all storms in the dataset.

Used by the frontend to display summary statistics in the top dashboard cards.

---

### `GET /hurricanes`
Returns storms that reached **hurricane status**.

Used for additional summary metrics displayed in the UI.

---

### `GET /hurricanes/landfall`
Returns hurricanes that **made landfall in Florida since 1900**.

This endpoint populates the hurricane **selection dropdown** in the UI.

---

### `GET /shape/<state>`
Returns the **GeoJSON geometry** for a given U.S. state.

Currently used to fetch the geometry for **Florida** so it can be rendered on the map.

Example:

```
/shape/florida
```

## Frontend (Astro + React)

The frontend is built using **Astro** with **React components** and **Leaflet** for mapping.

The interface allows users to:

- Select a hurricane that made landfall in Florida
- View the hurricane track on an interactive map
- See an **animated storm path**
- View:
  - Maximum wind speed
  - Date of landfall

Each best track point on the map contains additional metadata including:

- Date & time
- Wind speed
- Atmospheric pressure

## Running the Project

The easiest way to run the project is with Docker.

### 1. Clone the repository

```
git clone <repository-url>
cd KCC-HURDAT2
```

**Important:** Ensure there's a .env file in the root of /frontend with ```API_BASE_URL="http://backend:8080"``` as the only item

### 2. Start the application

From the root directory:

```
docker compose up
```

This will start:

- The **Flask API container**
- The **Astro frontend container**

### 3. Open the application

Navigate to:

```
http://localhost:4321
```

## Data Sources

- **HURDAT2 Dataset** – NOAA Atlantic Hurricane Database
- **TIGER/Line Shapefiles** – U.S. Census Bureau

## Technologies Used

Backend:

- Python
- Flask
- GeoPandas
- Shapely

Frontend:

- Astro
- React
- Leaflet

Infrastructure:

- Docker
- Docker Compose

## Summary

This project demonstrates how geospatial analysis can be used to analyze historical hurricane data and determine landfall events. By combining **HURDAT2 storm tracks**, **Census boundary data**, and **GeoPandas spatial operations**, the backend identifies hurricanes that impacted Florida and exposes that information through a simple API for interactive visualization.
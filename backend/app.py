from flask import Flask, jsonify, Response

from helpers.helpers import load_storm_data

def create_app():
    """
    On Flask initialization, this function calls load_storm_data() to load the required data from the
    data/ directory and stores the results in memory.
    """
    
    app = Flask(__name__)
    app.config.from_mapping(
        HURDAT_FILE="data/hurdat2-1851-2025.txt",
        STATES_SHP_FILE="data/tl_2025_us_state/tl_2025_us_state.shp"
    )

    storms, hurricanes, landfall_hurricanes, state_geometry = load_storm_data(app.config["HURDAT_FILE"], app.config["STATES_SHP_FILE"])
    app.config["STORMS"] = storms
    app.config["HURRICANES"] = hurricanes
    app.config["LANDFALL_HURRICANES"] = landfall_hurricanes
    app.config["STATE_GEOMETRY"] = state_geometry

    # print(f"Loaded {len(storms)} storms, {len(hurricanes)} hurricanes since 1900, and {len(landfall_hurricanes)} hurricanes that made landfall in Florida.")
    print("Ready")

    @app.route("/", methods=["GET"])
    def home():
        return "Hello, World!"

    @app.route("/storms", methods=["GET"])
    def fetch_storms():
        """
        Returns all the storms from the dataset
        """
        return jsonify([storm.__dict__ for storm in app.config["STORMS"]])

    @app.route("/hurricanes", methods=["GET"])
    def fetch_hurricanes():
        """
        Returns all the hurricanes from the dataset
        """
        return jsonify([hurricane.__dict__ for hurricane in app.config["HURRICANES"]])

    @app.route("/hurricanes/landfall", methods=["GET"])
    def fetch_landfall_hurricanes():
        """
        Returns all the hurricanes that made landfall in Florida from the dataset
        """
        return jsonify([hurricane.__dict__ for hurricane in app.config["LANDFALL_HURRICANES"]])
    
    @app.route("/shape/<string:state>", methods=["GET"])
    def shape(state):
        """
        Returns the requested state geometry
        """
        if not state:
            return jsonify({
                "error": "State parameter not passed"
            }), 400
        
        state_geom = app.config["STATE_GEOMETRY"]
        state_feature = state_geom[state_geom["NAME"].str.lower() == state.lower()]

        if state_feature.empty:
            return jsonify({
                "error": f"{state} not found in the shapefile."
            }), 404
        
        return Response(
            state_feature.to_json(),
            mimetype="application/geo+json"
        )

    return app

app = create_app()
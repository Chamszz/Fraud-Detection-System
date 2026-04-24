# Fraud System Detection

A simple fraud detection project with simulation, model training, and frontend/backend components.

## How to run

1. Delete the `user_profiles.db` file if it exists.(not mandatory)
2. Run the simulation file:
   - `python run_simulation.py` (generates simulation data for the fraud detection workflow)
3. After the simulation is done, run the training file:
   - `python notebooks/train.py` (trains the fraud detection model)
4. Run the frontend:
   - `streamlit run frontend/app.py`
5. Run the backend:
   - `uvicorn backend.main:app --reload`

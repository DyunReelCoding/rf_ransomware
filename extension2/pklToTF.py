import joblib
import json

# Load the trained Random Forest model
model = joblib.load('rf_ransomware.pkl')

# Extract the relevant parts of the model
model_params = {
    "n_estimators": model.n_estimators,
    "max_depth": model.max_depth,
    "feature_importances": model.feature_importances_.tolist(),
    "trees": []
}

# Loop through each tree in the forest and extract the decision tree parameters
for tree in model.estimators_:
    tree_params = {
        "feature": tree.tree_.feature.tolist(),
        "threshold": tree.tree_.threshold.tolist(),
        "left_children": tree.tree_.children_left.tolist(),
        "right_children": tree.tree_.children_right.tolist(),
        "values": tree.tree_.value.tolist(),
    }
    model_params["trees"].append(tree_params)

# Save the parameters to a JSON file
with open("rf_ransomware_model.json", "w") as json_file:
    json.dump(model_params, json_file, indent=4)

print("Model saved as JSON.")

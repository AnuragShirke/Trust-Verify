#!/usr/bin/env python
"""
Generate sample model files for the Fake News Detector API.
This script creates simple placeholder models for testing purposes.
"""

import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# Create model directory if it doesn't exist
os.makedirs("model", exist_ok=True)

print("Generating sample model files...")

# Create a simple TF-IDF vectorizer
tfidf = TfidfVectorizer(max_features=1000)
# Fit on some sample data
sample_texts = [
    "This is a real news article about politics.",
    "Breaking news: major event happened today.",
    "Scientists discover new species in the Amazon.",
    "Fake news: aliens have landed on Earth.",
    "Conspiracy theory about government control."
]
tfidf.fit(sample_texts)

# Save the vectorizer
with open("model/tfidf_vectorizer.pkl", "wb") as f:
    pickle.dump(tfidf, f)
print("✓ Created TF-IDF vectorizer")

# Create a simple logistic regression model
X = tfidf.transform(sample_texts)
y = np.array([1, 1, 1, 0, 0])  # 1 for real, 0 for fake
logreg = LogisticRegression(random_state=42)
logreg.fit(X, y)

# Save the model as classifier.pkl (the name the API is looking for)
with open("model/classifier.pkl", "wb") as f:
    pickle.dump(logreg, f)
print("✓ Created classifier model")

# Create a simple random forest model
rf = RandomForestClassifier(n_estimators=10, random_state=42)
rf.fit(X, y)

# Save the model as an alternative
with open("model/random_forest_model.pkl", "wb") as f:
    pickle.dump(rf, f)
print("✓ Created random forest model")

# Create symbolic links in the parent directory
print("Creating symbolic links in parent directory...")
try:
    # Create parent model directory if it doesn't exist
    parent_model_dir = os.path.join("..", "model")
    os.makedirs(parent_model_dir, exist_ok=True)

    # Copy files to parent directory
    import shutil
    shutil.copy("model/tfidf_vectorizer.pkl", os.path.join(parent_model_dir, "tfidf_vectorizer.pkl"))
    shutil.copy("model/classifier.pkl", os.path.join(parent_model_dir, "classifier.pkl"))
    print("✓ Created model files in parent directory")
except Exception as e:
    print(f"Warning: Could not create files in parent directory: {e}")
    print("Will try to modify the API code instead.")

print("All sample models generated successfully!")

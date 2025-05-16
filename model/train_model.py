import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib
import os

# Load and combine data
fake = pd.read_csv(r"C:\Users\anura\OneDrive\Desktop\new\fake-news-detector\data\raw\Fake.csv")
real = pd.read_csv(r"C:\Users\anura\OneDrive\Desktop\new\fake-news-detector\data\raw\True.csv")  # File is named True.csv, not Real.csv

fake["label"] = 0  # 0 = FAKE
real["label"] = 1  # 1 = REAL

df = pd.concat([fake, real]).sample(frac=1).reset_index(drop=True)
df["text"] = df["title"] + " " + df["text"]

# Split
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["label"], test_size=0.2, random_state=42)

# Vectorizer
tfidf = TfidfVectorizer(stop_words="english", max_df=0.7)
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# Model
clf = LogisticRegression()
clf.fit(X_train_tfidf, y_train)

# Evaluate
print(classification_report(y_test, clf.predict(X_test_tfidf)))

# Save
os.makedirs("model", exist_ok=True)
joblib.dump(tfidf, "model/tfidf_vectorizer.pkl")
joblib.dump(clf, "model/classifier.pkl")

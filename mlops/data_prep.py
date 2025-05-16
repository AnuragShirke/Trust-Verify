"""
Data preparation utilities for the fake news detector model.
"""
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from mlops.config import (
    FAKE_NEWS_PATH,
    REAL_NEWS_PATH,
    PROCESSED_DATA_DIR,
    TEST_SIZE,
    RANDOM_STATE,
    FEEDBACK_PATH
)

def load_raw_data():
    """Load raw data from CSV files."""
    try:
        fake = pd.read_csv(FAKE_NEWS_PATH)
        real = pd.read_csv(REAL_NEWS_PATH)
        
        # Add labels
        fake["label"] = 0  # 0 = FAKE
        real["label"] = 1  # 1 = REAL
        
        # Combine datasets
        df = pd.concat([fake, real]).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
        
        # Combine title and text
        df["text"] = df["title"] + " " + df["text"]
        
        return df
    except Exception as e:
        print(f"Error loading raw data: {e}")
        return None

def load_feedback_data():
    """Load user feedback data if available."""
    if os.path.exists(FEEDBACK_PATH):
        try:
            feedback_df = pd.read_csv(FEEDBACK_PATH)
            return feedback_df
        except Exception as e:
            print(f"Error loading feedback data: {e}")
    return None

def combine_with_feedback(df):
    """Combine raw data with feedback data if available."""
    feedback_df = load_feedback_data()
    if feedback_df is not None and not feedback_df.empty:
        # Ensure feedback data has the same structure
        if "text" in feedback_df.columns and "label" in feedback_df.columns:
            # Combine with original data
            combined_df = pd.concat([df, feedback_df]).reset_index(drop=True)
            return combined_df
    return df

def prepare_data(include_feedback=True):
    """Prepare data for model training."""
    # Load raw data
    df = load_raw_data()
    if df is None:
        return None, None, None, None
    
    # Combine with feedback if requested
    if include_feedback:
        df = combine_with_feedback(df)
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], 
        df["label"], 
        test_size=TEST_SIZE, 
        random_state=RANDOM_STATE,
        stratify=df["label"]
    )
    
    # Save processed data
    train_df = pd.DataFrame({"text": X_train, "label": y_train})
    test_df = pd.DataFrame({"text": X_test, "label": y_test})
    
    train_path = os.path.join(PROCESSED_DATA_DIR, "train.csv")
    test_path = os.path.join(PROCESSED_DATA_DIR, "test.csv")
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    return X_train, X_test, y_train, y_test

def save_feedback(text, predicted_label, corrected_label, source=None):
    """Save user feedback for model improvement."""
    feedback_data = {
        "text": [text],
        "predicted_label": [predicted_label],
        "label": [corrected_label],
        "source": [source if source else "user_feedback"]
    }
    
    feedback_df = pd.DataFrame(feedback_data)
    
    # Create or append to feedback file
    if os.path.exists(FEEDBACK_PATH):
        existing_df = pd.read_csv(FEEDBACK_PATH)
        updated_df = pd.concat([existing_df, feedback_df]).reset_index(drop=True)
        updated_df.to_csv(FEEDBACK_PATH, index=False)
    else:
        os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
        feedback_df.to_csv(FEEDBACK_PATH, index=False)
    
    return True

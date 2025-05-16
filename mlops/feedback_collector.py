"""
Feedback collection module for the fake news detector.
"""
import os
import pandas as pd
from datetime import datetime
from mlops.data_prep import save_feedback
from mlops.config import FEEDBACK_PATH

class FeedbackCollector:
    """
    Collects and manages user feedback for model improvement.
    
    This class provides methods to:
    1. Submit feedback for misclassified articles
    2. Retrieve feedback statistics
    3. Export feedback data for analysis
    """
    
    def __init__(self):
        """Initialize the feedback collector."""
        self.feedback_path = FEEDBACK_PATH
    
    def submit_feedback(self, text, predicted_label, corrected_label, source=None):
        """
        Submit feedback for a misclassified article.
        
        Args:
            text: The article text
            predicted_label: The label predicted by the model (0=FAKE, 1=REAL)
            corrected_label: The corrected label provided by the user
            source: Source of the feedback (e.g., 'user', 'expert', 'api')
            
        Returns:
            bool: True if feedback was saved successfully
        """
        return save_feedback(text, predicted_label, corrected_label, source)
    
    def get_feedback_stats(self):
        """
        Get statistics about collected feedback.
        
        Returns:
            dict: Statistics about the feedback data
        """
        if not os.path.exists(self.feedback_path):
            return {
                "total_feedback": 0,
                "fake_to_real": 0,
                "real_to_fake": 0,
                "sources": {}
            }
        
        try:
            df = pd.read_csv(self.feedback_path)
            
            # Calculate statistics
            total = len(df)
            fake_to_real = len(df[(df["predicted_label"] == 0) & (df["label"] == 1)])
            real_to_fake = len(df[(df["predicted_label"] == 1) & (df["label"] == 0)])
            
            # Count by source
            source_counts = df["source"].value_counts().to_dict()
            
            return {
                "total_feedback": total,
                "fake_to_real": fake_to_real,
                "real_to_fake": real_to_fake,
                "sources": source_counts
            }
        except Exception as e:
            print(f"Error getting feedback stats: {e}")
            return {
                "total_feedback": 0,
                "fake_to_real": 0,
                "real_to_fake": 0,
                "sources": {},
                "error": str(e)
            }
    
    def export_feedback(self, output_path=None):
        """
        Export feedback data to a CSV file.
        
        Args:
            output_path: Path to save the exported data (default: timestamped file)
            
        Returns:
            str: Path to the exported file, or None if export failed
        """
        if not os.path.exists(self.feedback_path):
            print("No feedback data available to export")
            return None
        
        try:
            df = pd.read_csv(self.feedback_path)
            
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = os.path.dirname(self.feedback_path)
                output_path = os.path.join(output_dir, f"feedback_export_{timestamp}.csv")
            
            df.to_csv(output_path, index=False)
            print(f"Feedback data exported to {output_path}")
            return output_path
        except Exception as e:
            print(f"Error exporting feedback data: {e}")
            return None
    
    def clear_feedback(self, backup=True):
        """
        Clear all feedback data (with optional backup).
        
        Args:
            backup: Whether to create a backup before clearing
            
        Returns:
            bool: True if feedback was cleared successfully
        """
        if not os.path.exists(self.feedback_path):
            print("No feedback data to clear")
            return True
        
        try:
            if backup:
                self.export_feedback()
            
            os.remove(self.feedback_path)
            print("Feedback data cleared")
            return True
        except Exception as e:
            print(f"Error clearing feedback data: {e}")
            return False

# Example usage
if __name__ == "__main__":
    collector = FeedbackCollector()
    
    # Submit sample feedback
    collector.submit_feedback(
        "This is a test article that was misclassified.",
        predicted_label=0,  # Predicted as FAKE
        corrected_label=1,  # Actually REAL
        source="test"
    )
    
    # Print statistics
    stats = collector.get_feedback_stats()
    print("Feedback Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

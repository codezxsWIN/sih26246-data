import shap
import numpy as np
from typing import Dict, Any, List, Optional
from engine.ml.shortage_classifier import ShortageRiskClassifier

class ModelExplainer:
    def __init__(self, classifier: Optional[ShortageRiskClassifier] = None):
        self.classifier = classifier or ShortageRiskClassifier()
        if not self.classifier.is_fitted:
            self.classifier.fit()
        self.explainer = shap.TreeExplainer(self.classifier.model)
        self.feature_names = [
            "Demand Score",
            "Scaled Supply Estimate",
            "Job Posting Growth %",
            "Active Employer Count"
        ]

    def explain_prediction(self, feature_vector: List[float]) -> Dict[str, Any]:
        X_in = np.array([feature_vector])
        shap_values = self.explainer.shap_values(X_in)
        
        # Format SHAP values for output
        if isinstance(shap_values, list):
            sv = shap_values[0][0]  # First class
        elif shap_values.ndim == 3:
            sv = shap_values[0, :, 0]
        else:
            sv = shap_values[0]

        impacts = {}
        for idx, name in enumerate(self.feature_names):
            val = float(sv[idx]) if idx < len(sv) else 0.0
            impacts[name] = round(val, 4)

        return {
            "feature_impacts": impacts,
            "top_driver": max(impacts.items(), key=lambda x: abs(x[1]))[0],
            "base_value": float(self.explainer.expected_value[0]) if hasattr(self.explainer.expected_value, '__getitem__') else float(self.explainer.expected_value)
        }

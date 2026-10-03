import numpy as np
from typing import Dict, Any, List, Optional
from engine.ml.shortage_classifier import ShortageRiskClassifier

try:
    import shap
except Exception:
    shap = None

class ModelExplainer:
    def __init__(self, classifier: Optional[ShortageRiskClassifier] = None):
        self.classifier = classifier or ShortageRiskClassifier()
        if not self.classifier.is_fitted:
            self.classifier.fit()
        self.explainer = shap.TreeExplainer(self.classifier.model) if shap is not None and self.classifier.model is not None else None
        self.feature_names = [
            "Demand Score",
            "Scaled Supply Estimate",
            "Job Posting Growth %",
            "Active Employer Count"
        ]

    def explain_prediction(self, feature_vector: List[float]) -> Dict[str, Any]:
        X_in = np.array([feature_vector])
        if self.explainer is None:
            demand, supply, posting_growth, employer_count = feature_vector
            impacts = {
                "Demand Score": round(float(demand - 50.0) / 10.0, 4),
                "Scaled Supply Estimate": round(float(50.0 - supply) / 10.0, 4),
                "Job Posting Growth %": round(float(posting_growth) / 10.0, 4),
                "Active Employer Count": round(float(employer_count) / 100.0, 4),
            }
            return {
                "feature_impacts": impacts,
                "top_driver": max(impacts.items(), key=lambda x: abs(x[1]))[0],
                "base_value": 0.0,
            }
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

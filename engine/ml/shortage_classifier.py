import numpy as np
from typing import Tuple, List, Dict, Any

try:
    import xgboost as xgb
except Exception:
    xgb = None

class ShortageRiskClassifier:
    def __init__(self):
        self.model = None
        if xgb is not None:
            self.model = xgb.XGBClassifier(
                max_depth=4,
                n_estimators=100,
                learning_rate=0.05,
                random_state=42
            )
        self.classes = ["Oversupply", "Balanced", "Moderate Shortage", "Critical Shortage"]
        self.is_fitted = False

    def _generate_synthetic_training_data(self) -> Tuple[np.ndarray, np.ndarray]:
        np.random.seed(42)
        N = 200
        # Features: [demand_score, supply_estimate_scaled, posting_growth, employer_count]
        X = np.random.uniform(20.0, 95.0, (N, 4))
        y = []
        for row in X:
            d_score, s_scaled, p_growth, emp_cnt = row
            gap = d_score - s_scaled
            if gap > 25.0:
                y.append(3) # Critical Shortage
            elif gap > 10.0:
                y.append(2) # Moderate Shortage
            elif gap > -10.0:
                y.append(1) # Balanced
            else:
                y.append(0) # Oversupply
        return X, np.array(y)

    def fit(self) -> None:
        if self.model is None:
            self.is_fitted = True
            return
        X, y = self._generate_synthetic_training_data()
        self.model.fit(X, y)
        self.is_fitted = True

    def predict(self, feature_vector: List[float]) -> Dict[str, Any]:
        if not self.is_fitted:
            self.fit()
        X_in = np.array([feature_vector])
        if self.model is None:
            demand, supply, posting_growth, employer_count = feature_vector
            gap = demand - supply
            pred_idx = 3 if gap > 25 else 2 if gap > 10 else 1 if gap >= -10 else 0
            distances = np.array([abs(gap + 20), abs(gap), abs(gap - 15), abs(gap - 35)], dtype=float)
            probs = np.exp(-distances / 10.0)
            probs /= probs.sum()
            return {
                "predicted_category": self.classes[pred_idx],
                "class_probabilities": {self.classes[i]: float(probs[i]) for i in range(len(self.classes))}
            }
        pred_idx = self.model.predict(X_in)[0]
        probs = self.model.predict_proba(X_in)[0]
        
        return {
            "predicted_category": self.classes[pred_idx],
            "class_probabilities": {
                self.classes[i]: float(probs[i]) for i in range(len(self.classes))
            }
        }

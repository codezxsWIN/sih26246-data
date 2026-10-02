import unittest
from pathlib import Path
from engine.config import settings
from engine.db import init_db, DemandRepository, SupplyRepository, GapRepository, ForecastRepository, PolicyRepository
from engine.ingest import BaseDataLoader, ExternalDataLoader
from engine.analytics import DemandEngine, SupplyEngine, GapEngine
from engine.ml import DemandForecaster, ShortageRiskClassifier, ModelExplainer
from engine.policy import PolicyRulesEngine
from engine.rag import PolicyCopilot

class EngineIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = init_db()
        BaseDataLoader(cls.conn).run_all()
        ExternalDataLoader(cls.conn).run_all()

    def test_01_config_and_settings(self):
        self.assertEqual(settings.PROJECT_NAME, "AI-Powered Labour Market Intelligence Engine")
        weights = settings.get_weights()
        self.assertIn("demand_score_weights", weights)
        self.assertEqual(weights["demand_score_weights"]["job_posting_growth"], 0.30)

    def test_02_database_connection_and_repositories(self):
        cursor = self.conn.cursor()
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        table_names = [t["name"] for t in tables]
        self.assertIn("raw_job_postings", table_names)
        self.assertIn("demand_scores", table_names)
        self.assertIn("supply_estimates", table_names)
        self.assertIn("demand_supply_gaps", table_names)

    def test_03_demand_engine_calculation(self):
        d_eng = DemandEngine(self.conn)
        res = d_eng.calculate_score_for_entity("Software Developer", "occupation", "All India")
        self.assertGreaterEqual(res["demand_score"], 0.0)
        self.assertLessEqual(res["demand_score"], 100.0)
        self.assertIn("confidence_interval_lower", res)

    def test_04_supply_engine_calculation(self):
        s_eng = SupplyEngine(self.conn)
        res = s_eng.calculate_supply_for_entity("Data Analyst / Scientist", "occupation", "Maharashtra")
        self.assertGreater(res["estimated_supply"], 0)
        self.assertIn("lower_bound", res)
        self.assertIn("upper_bound", res)

    def test_05_gap_engine_classification(self):
        g_eng = GapEngine(self.conn)
        res = g_eng.calculate_gap("Software Developer", "occupation", "All India")
        self.assertIn(res["shortage_risk_category"], ["Critical Shortage", "Moderate Shortage", "Balanced", "Oversupply"])
        self.assertIn("shap_drivers_json", res)

    def test_06_ml_forecasting(self):
        forecaster = DemandForecaster(self.conn)
        forecasts = forecaster.forecast_for_entity("Software Developer", "All India")
        self.assertEqual(len(forecasts), 3) # 3, 6, 12 months
        self.assertEqual(forecasts[0]["forecast_horizon_months"], 3)
        self.assertEqual(forecasts[1]["forecast_horizon_months"], 6)
        self.assertEqual(forecasts[2]["forecast_horizon_months"], 12)

    def test_07_policy_rules_engine(self):
        policy_eng = PolicyRulesEngine(self.conn)
        interventions = policy_eng.run_policy_engine()
        self.assertGreater(len(interventions), 0)
        self.assertIn(interventions[0]["priority_level"], ["HIGH", "MEDIUM", "LOW"])

    def test_08_policy_copilot_rag(self):
        copilot = PolicyCopilot(self.conn)
        ans = copilot.answer_policy_query("How can Maharashtra address skill shortages?")
        self.assertIn("answer", ans)
        self.assertIn("grounding_facts", ans)
        self.assertTrue(len(ans["grounding_facts"]) > 0)

if __name__ == "__main__":
    unittest.main()

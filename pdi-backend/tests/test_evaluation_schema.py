import unittest

from app.schemas.evaluation.evaluation import EvaluationCreate


class EvaluationSchemaTest(unittest.TestCase):
    def test_evaluation_create_allows_null_target_position(self):
        payload = {
            "user_id": 1,
            "evaluator_id": 1,
            "target_position_id": None,
            "enterprise_id": 1,
            "type": "SELF",
            "cycle": "2026",
        }

        evaluation = EvaluationCreate.model_validate(payload)

        self.assertIsNone(evaluation.target_position_id)


if __name__ == "__main__":
    unittest.main()

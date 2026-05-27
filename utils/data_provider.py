import csv
from typing import List, Optional
import logging
from models import SearchScenario

logger = logging.getLogger(__name__)


class DataProvider:
    """Provides test data from CSV file"""

    @staticmethod
    def load_csv(filepath: str) -> List[dict]:
        """Load data from CSV file"""
        try:
            data = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            logger.info(f"Loaded CSV data from {filepath}")
            return data
        except FileNotFoundError:
            logger.error(f"CSV file not found: {filepath}")
            raise

    @staticmethod
    def get_search_scenarios(filepath: str = "data/scenarios.csv") -> List[SearchScenario]:
        """Get all test scenarios as typed SearchScenario objects"""
        rows = DataProvider.load_csv(filepath)
        return [
            SearchScenario(
                scenario_id=row["scenario_id"],
                description=row.get("name", ""),
                query=row["search_query"],
                max_price=float(row["max_price"]),
                limit=int(row["expected_items_count"])
            )
            for row in rows
        ]

    @staticmethod
    def get_search_scenario_by_id(scenario_id: str, filepath: str = "data/scenarios.csv") -> Optional[SearchScenario]:
        """Get specific test scenario by ID as a typed SearchScenario object"""
        scenarios = DataProvider.get_search_scenarios(filepath)
        for scenario in scenarios:
            if scenario.scenario_id == scenario_id:
                return scenario
        logger.warning(f"Search scenario {scenario_id} not found")
        return None
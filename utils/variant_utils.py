from typing import List, Optional, Dict, Any
import random
import logging

logger = logging.getLogger(__name__)


class VariantSelector:
    """Utility for selecting product variants"""

    @staticmethod
    def select_random_from_list(items: List[str]) -> Optional[str]:
        """Select random item from list"""
        if not items:
            logger.warning("Empty list provided for random selection")
            return None

        selected = random.choice(items)
        logger.info(f"Randomly selected from {len(items)} items: {selected}")
        return selected

    @staticmethod
    def select_multiple_random(items: List[str], count: int) -> List[str]:
        """Select multiple random items from list"""
        if not items or count <= 0:
            logger.warning(f"Cannot select {count} items from {len(items) if items else 0} items")
            return []

        count = min(count, len(items))
        selected = random.sample(items, count)
        logger.info(f"Selected {count} random items from {len(items)}: {selected}")
        return selected

    @staticmethod
    def select_first(items: List[str]) -> Optional[str]:
        """Select first item from list"""
        if not items:
            logger.warning("Cannot select from empty list")
            return None

        selected = items[0]
        logger.info(f"Selected first item: {selected}")
        return selected

    @staticmethod
    def select_last(items: List[str]) -> Optional[str]:
        """Select last item from list"""
        if not items:
            logger.warning("Cannot select from empty list")
            return None

        selected = items[-1]
        logger.info(f"Selected last item: {selected}")
        return selected

    @staticmethod
    def select_by_pattern(items: List[str], pattern: str) -> Optional[str]:
        """Select item matching pattern"""
        for item in items:
            if pattern.lower() in item.lower():
                logger.info(f"Selected item matching pattern '{pattern}': {item}")
                return item

        logger.warning(f"No item found matching pattern: {pattern}")
        return None

    @staticmethod
    def exclude_variant(items: List[str], exclude: str) -> List[str]:
        """Get list excluding specific variant"""
        filtered = [item for item in items if item != exclude]
        logger.info(f"Filtered out '{exclude}': {len(items)} -> {len(filtered)} items")
        return filtered

    @staticmethod
    def filter_by_keywords(items: List[str], keywords: List[str]) -> List[str]:
        """Filter items containing any of the keywords"""
        filtered = [
            item for item in items
            if any(kw.lower() in item.lower() for kw in keywords)
        ]
        logger.info(f"Filtered by keywords {keywords}: {len(items)} -> {len(filtered)} items")
        return filtered

    @staticmethod
    def build_variant_combinations(
        sizes: List[str],
        colors: List[str],
        quantities: List[int] = None
    ) -> List[Dict[str, Any]]:
        """Build all combinations of variants"""
        if quantities is None:
            quantities = [1]

        combinations = []
        for size in sizes:
            for color in colors:
                for quantity in quantities:
                    combinations.append({
                        "size": size,
                        "color": color,
                        "quantity": quantity
                    })

        logger.info(f"Built {len(combinations)} variant combinations")
        return combinations

    @staticmethod
    def select_random_combination(
        sizes: List[str],
        colors: List[str],
        quantities: List[int] = None
    ) -> Dict[str, Any]:
        """Select random combination of variants"""
        if quantities is None:
            quantities = [1]

        combination = {
            "size": VariantSelector.select_random_from_list(sizes),
            "color": VariantSelector.select_random_from_list(colors),
            "quantity": random.choice(quantities)
        }

        logger.info(f"Selected random variant combination: {combination}")
        return combination

    @staticmethod
    def get_variant_weights(items: List[str], weights: List[float]) -> str:
        """Select item based on weights (weighted random)"""
        if len(items) != len(weights):
            logger.error("Items and weights lists must be same length")
            raise ValueError("Items and weights must have same length")

        selected = random.choices(items, weights=weights, k=1)[0]
        logger.info(f"Weighted selection: {selected}")
        return selected

    @staticmethod
    def validate_variant_availability(
        size: str,
        color: str,
        available_sizes: List[str],
        available_colors: List[str]
    ) -> bool:
        """Validate if variant combination is available"""
        is_available = size in available_sizes and color in available_colors
        logger.info(f"Variant availability (size={size}, color={color}): {is_available}")
        return is_available
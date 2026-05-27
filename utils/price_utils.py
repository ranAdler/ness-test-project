import re
from typing import Union, Tuple
import logging

logger = logging.getLogger(__name__)


class PriceParser:
    """Utility for parsing and formatting prices"""

    CURRENCY_SYMBOLS = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
        "¥": "JPY",
        "₹": "INR",
        "₪": "ILS",
    }

    @staticmethod
    def parse_price(price_text: str) -> float:
        """
        Parse price from text, handling currency symbols and formatting.

        Examples:
        - "$99.99" -> 99.99
        - "€150,50" -> 150.50
        - "Price: $200.00 USD" -> 200.00
        """
        try:
            # Remove whitespace
            price_text = price_text.strip()

            # Remove common text patterns
            price_text = re.sub(r'(Price|Total|Cost|Amount):\s*', '', price_text, flags=re.IGNORECASE)

            # Detect currency and normalize decimal separator
            # Handle both comma and period as decimal separator
            if ',' in price_text and '.' in price_text:
                # Determine which is decimal separator (appears last)
                last_comma = price_text.rfind(',')
                last_period = price_text.rfind('.')
                if last_comma > last_period:
                    # European format: 1.234,56
                    price_text = price_text.replace('.', '').replace(',', '.')
                else:
                    # US format: 1,234.56
                    price_text = price_text.replace(',', '')
            elif ',' in price_text:
                # Only comma present - check if it's thousands separator or decimal
                parts = price_text.split(',')
                if len(parts[-1]) == 2:
                    # European format with comma as decimal
                    price_text = price_text.replace('.', '').replace(',', '.')
                else:
                    # Thousands separator
                    price_text = price_text.replace(',', '')

            # Extract only digits and decimal point
            clean_price = ''.join(c for c in price_text if c.isdigit() or c == '.')

            # Remove multiple decimal points
            if clean_price.count('.') > 1:
                parts = clean_price.rsplit('.', 1)
                clean_price = parts[0].replace('.', '') + '.' + parts[1]

            price = float(clean_price) if clean_price else 0.0
            logger.debug(f"Parsed price from '{price_text}' -> ${price:.2f}")
            return price
        except (ValueError, AttributeError) as e:
            logger.error(f"Failed to parse price from '{price_text}': {e}")
            return 0.0

    @staticmethod
    def format_price(price: float, currency: str = "$", decimals: int = 2) -> str:
        """
        Format price with currency symbol.

        Examples:
        - format_price(99.5) -> "$99.50"
        - format_price(1000, "€", 2) -> "€1000.00"
        """
        formatted = f"{currency}{price:,.{decimals}f}"
        logger.debug(f"Formatted price: {price} -> {formatted}")
        return formatted

    @staticmethod
    def get_currency_from_text(price_text: str) -> Tuple[str, str]:
        """
        Extract currency symbol and code from price text.
        Returns (symbol, code) tuple.

        Example:
        - "$99.99" -> ("$", "USD")
        """
        for symbol, code in PriceParser.CURRENCY_SYMBOLS.items():
            if symbol in price_text:
                logger.debug(f"Detected currency: {symbol} ({code})")
                return (symbol, code)
        return ("$", "USD")  # Default to USD

    @staticmethod
    def validate_price(price: float, min_price: float = 0.0, max_price: float = float('inf')) -> bool:
        """
        Validate if price is within range.

        Example:
        - validate_price(99.99, min_price=10, max_price=200) -> True
        """
        is_valid = min_price <= price <= max_price
        logger.debug(f"Price validation: ${price:.2f} in range [${min_price:.2f}, ${max_price:.2f}] -> {is_valid}")
        return is_valid

    @staticmethod
    def calculate_total(prices: list) -> float:
        """Calculate total from list of prices"""
        total = sum(prices)
        logger.debug(f"Calculated total from {len(prices)} prices: ${total:.2f}")
        return total

    @staticmethod
    def apply_discount(price: float, discount_percent: float) -> float:
        """Apply percentage discount to price"""
        discounted = price * (1 - discount_percent / 100)
        logger.debug(f"Applied {discount_percent}% discount to ${price:.2f} -> ${discounted:.2f}")
        return discounted

    @staticmethod
    def add_tax(price: float, tax_percent: float) -> float:
        """Add tax to price"""
        with_tax = price * (1 + tax_percent / 100)
        logger.debug(f"Added {tax_percent}% tax to ${price:.2f} -> ${with_tax:.2f}")
        return with_tax

    @staticmethod
    def calculate_price_per_unit(total_price: float, quantity: int) -> float:
        """Calculate unit price from total and quantity"""
        unit_price = total_price / quantity if quantity > 0 else 0.0
        logger.debug(f"Unit price: ${total_price:.2f} / {quantity} = ${unit_price:.2f}")
        return unit_price
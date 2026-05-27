from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class SearchScenario:
    """Search test scenario with clear field names"""
    query: str
    max_price: float
    limit: int
    scenario_id: Optional[str] = None
    description: Optional[str] = None

    def __repr__(self) -> str:
        return f"SearchScenario(id={self.scenario_id}, query='{self.query}', max_price=${self.max_price}, limit={self.limit})"


@dataclass
class Variant:
    """Represents product variants (size, color, quantity options)"""
    size: List[str]
    color: List[str]
    quantity: List[int]


@dataclass
class Product:
    """Represents a product with minimum required fields"""
    id: str
    name: str
    title: str
    price: float
    url: str
    variants: Variant
    in_stock: bool = True

    def __repr__(self) -> str:
        return f"Product(id={self.id}, name={self.name}, price={self.price}, in_stock={self.in_stock})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "price": self.price,
            "url": self.url,
            "in_stock": self.in_stock,
            "variants": {
                "size": self.variants.size,
                "color": self.variants.color,
                "quantity": self.variants.quantity,
            }
        }
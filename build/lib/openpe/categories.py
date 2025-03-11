# categories.py
from typing import Set, Dict, Optional

class Categories:
    """Categories from datosabiertos.gob.pe as constants, with support for extension."""
    # Built-in categories as class attributes
    GOBERNABILIDAD = "gobernabilidad-24"
    ECONOMIA_Y_FINANZAS = "economía-y-finanzas-29"
    DESARROLLO_SOCIAL = "desarrollo-social-338"
    EXPRESATE_PERU = "exprésate-perú-con-datos-1466"
    TRANSPORTE = "transporte-25"
    MEDIO_AMBIENTE = "medio-ambiente-y-recursos-naturales-30"
    SALUD = "salud-27"
    EDUCACION = "educación-28"
    DESARROLLO_URBANO = "desarrollo-urbano-339"
    AGUA_Y_SANEAMIENTO = "agua-y-saneamiento-26"
    COVID = "covid-19-917"
    ENERGIA = "energía-340"
    CIENCIA_Y_TECNOLOGIA = "ciencia-y-tecnología-1136"
    ALIMENTACION_Y_NUTRICION = "alimentación-y-nutrición-32"
    MODELO_DE_GESTION_DOCUMENTAL = "modelo-de-gestión-documental-1479"

    # Storage for custom categories
    _custom_categories: Dict[str, str] = {}

    @classmethod
    def register_category(cls, name: str, value: str) -> None:
        """Register a new category dynamically."""
        if not isinstance(name, str) or not name.isidentifier():
            raise ValueError("Category name must be a valid Python identifier (e.g., 'EDUCACION')")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Category value must be a non-empty string")
        if name in cls._custom_categories or hasattr(cls, name):
            raise ValueError(f"Category '{name}' already exists")
        cls._custom_categories[name] = value
        # Optionally, set it as a class attribute for dot-notation access
        setattr(cls, name, value)

    @classmethod
    def all_categories(cls) -> Set[str]:
        """Return a set of all category values (built-in + custom)."""
        built_in = {attr for attr in dir(cls) if attr.isupper() and not attr.startswith('_')}
        built_in_values = {getattr(cls, attr) for attr in built_in}
        custom_values = set(cls._custom_categories.values())
        return built_in_values | custom_values

    @classmethod
    def is_valid_category(cls, category: str) -> bool:
        """Check if a category value is valid (built-in or custom)."""
        return category in cls.all_categories()

    @classmethod
    def get_category_name(cls, value: str) -> Optional[str]:
        """Return the category name for a given value, if it exists."""
        for attr in dir(cls):
            if attr.isupper() and not attr.startswith('_') and getattr(cls, attr) == value:
                return attr
        for name, val in cls._custom_categories.items():
            if val == value:
                return name
        return None
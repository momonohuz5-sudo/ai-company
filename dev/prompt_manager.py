"""
Prompt Management System for SFW Image Generation
AI Company - Development Department
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from enum import Enum


class PromptCategory(Enum):
    """SFW prompt categories"""
    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    PRODUCT = "product"
    ILLUSTRATION = "illustration"
    ARCHITECTURE = "architecture"
    FOOD = "food"
    NATURE = "nature"
    TECHNOLOGY = "technology"
    ART = "art"
    ABSTRACT = "abstract"


class PromptTemplate:
    """Template for generating prompts"""

    def __init__(
        self,
        name: str,
        category: PromptCategory,
        base_prompt: str,
        variables: List[str],
        tags: List[str]
    ):
        self.name = name
        self.category = category
        self.base_prompt = base_prompt
        self.variables = variables
        self.tags = tags
        self.created_at = datetime.now()

    def generate(self, **kwargs) -> str:
        """Generate prompt from template with variables"""
        prompt = self.base_prompt
        for var in self.variables:
            if var in kwargs:
                prompt = prompt.replace(f"{{{var}}}", str(kwargs[var]))
        return prompt

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'category': self.category.value,
            'base_prompt': self.base_prompt,
            'variables': self.variables,
            'tags': self.tags,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        return cls(
            name=data['name'],
            category=PromptCategory(data['category']),
            base_prompt=data['base_prompt'],
            variables=data['variables'],
            tags=data['tags']
        )


class PromptManager:
    """Manage prompt templates and generation history"""

    def __init__(self, data_dir: str = './prompts'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.templates_file = self.data_dir / 'templates.json'
        self.history_file = self.data_dir / 'history.json'
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_templates()

    def add_template(self, template: PromptTemplate) -> None:
        """Add a new prompt template"""
        self.templates[template.name] = template
        self._save_templates()

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get template by name"""
        return self.templates.get(name)

    def list_templates(
        self,
        category: Optional[PromptCategory] = None
    ) -> List[PromptTemplate]:
        """List all templates, optionally filtered by category"""
        if category:
            return [t for t in self.templates.values() if t.category == category]
        return list(self.templates.values())

    def search_templates(self, query: str) -> List[PromptTemplate]:
        """Search templates by tags or name"""
        query_lower = query.lower()
        results = []
        for template in self.templates.values():
            if (query_lower in template.name.lower() or
                any(query_lower in tag.lower() for tag in template.tags)):
                results.append(template)
        return results

    def generate_prompt(self, template_name: str, **kwargs) -> Optional[str]:
        """Generate prompt from template"""
        template = self.get_template(template_name)
        if not template:
            return None
        return template.generate(**kwargs)

    def save_to_history(
        self,
        prompt: str,
        template_name: Optional[str],
        parameters: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """Save prompt generation to history"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'prompt': prompt,
            'template_name': template_name,
            'parameters': parameters,
            'result': result
        }

        history = self._load_history()
        history.append(history_entry)

        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def get_history(
        self,
        limit: Optional[int] = None,
        template_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get generation history"""
        history = self._load_history()

        if template_name:
            history = [h for h in history if h.get('template_name') == template_name]

        if limit:
            history = history[-limit:]

        return history

    def _load_templates(self) -> None:
        """Load templates from file"""
        if not self.templates_file.exists():
            self._create_default_templates()
            return

        with open(self.templates_file, 'r') as f:
            data = json.load(f)
            self.templates = {
                name: PromptTemplate.from_dict(tmpl_data)
                for name, tmpl_data in data.items()
            }

    def _save_templates(self) -> None:
        """Save templates to file"""
        data = {name: tmpl.to_dict() for name, tmpl in self.templates.items()}
        with open(self.templates_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load history from file"""
        if not self.history_file.exists():
            return []

        with open(self.history_file, 'r') as f:
            return json.load(f)

    def _create_default_templates(self) -> None:
        """Create default SFW prompt templates"""
        default_templates = [
            PromptTemplate(
                name="scenic_landscape",
                category=PromptCategory.LANDSCAPE,
                base_prompt="beautiful {location} landscape, {time_of_day}, {weather}, professional photography, high quality, detailed",
                variables=["location", "time_of_day", "weather"],
                tags=["landscape", "nature", "scenery", "photography"]
            ),
            PromptTemplate(
                name="product_showcase",
                category=PromptCategory.PRODUCT,
                base_prompt="professional product photography of {product}, {background}, studio lighting, commercial, high resolution, clean",
                variables=["product", "background"],
                tags=["product", "commercial", "marketing", "studio"]
            ),
            PromptTemplate(
                name="artistic_illustration",
                category=PromptCategory.ILLUSTRATION,
                base_prompt="{subject} illustration, {style} art style, {color_scheme} colors, detailed, high quality artwork",
                variables=["subject", "style", "color_scheme"],
                tags=["illustration", "art", "digital art", "concept"]
            ),
            PromptTemplate(
                name="modern_architecture",
                category=PromptCategory.ARCHITECTURE,
                base_prompt="{building_type} building, modern architecture, {material}, {environment}, professional architectural visualization",
                variables=["building_type", "material", "environment"],
                tags=["architecture", "building", "design", "modern"]
            ),
            PromptTemplate(
                name="food_photography",
                category=PromptCategory.FOOD,
                base_prompt="{dish} food photography, appetizing, professional culinary photo, {presentation}, delicious, high quality",
                variables=["dish", "presentation"],
                tags=["food", "culinary", "photography", "restaurant"]
            ),
            PromptTemplate(
                name="tech_visualization",
                category=PromptCategory.TECHNOLOGY,
                base_prompt="{technology} visualization, futuristic, clean design, {color_theme}, professional tech illustration",
                variables=["technology", "color_theme"],
                tags=["technology", "tech", "futuristic", "digital"]
            ),
            PromptTemplate(
                name="abstract_art",
                category=PromptCategory.ABSTRACT,
                base_prompt="abstract art, {pattern} patterns, {color_palette} color palette, {mood} mood, artistic, contemporary",
                variables=["pattern", "color_palette", "mood"],
                tags=["abstract", "art", "modern", "creative"]
            )
        ]

        for template in default_templates:
            self.add_template(template)


if __name__ == '__main__':
    print("Prompt Management System")
    manager = PromptManager()

    print(f"\nLoaded {len(manager.templates)} templates:")
    for template in manager.templates.values():
        print(f"  - {template.name} ({template.category.value})")

    print("\nExample prompt generation:")
    prompt = manager.generate_prompt(
        'scenic_landscape',
        location='mountain valley',
        time_of_day='sunset',
        weather='clear sky'
    )
    print(f"  {prompt}")

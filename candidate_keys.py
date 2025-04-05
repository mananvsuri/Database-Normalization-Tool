from typing import List
from dataclasses import dataclass

@dataclass
class AttributeCategories:
    left: List[str]
    right: List[str]
    neither: List[str]
    both: List[str]

class FunctionalDependency:
    def __init__(self, dependency_str: str):
        if "->" in dependency_str:
            arrow_idx = dependency_str.index("->")
            self.determinant = dependency_str[:arrow_idx]
            self.dependent = dependency_str[arrow_idx + 2:]
        else:
            self.determinant = dependency_str[0]
            self.dependent = dependency_str[1] + dependency_str[0]

    def __str__(self) -> str:
        return f"{self.determinant}->{self.dependent}"

class RelationAnalyzer:
    def __init__(self, attributes: List[str], dependencies: List[str]):
        self.attributes = attributes
        self.dependencies = [FunctionalDependency(dep.strip()) for dep in dependencies]
        self.categories = self._categorize_attributes()

    def _remove_duplicates(self, text: str) -> str:
        return ''.join(dict.fromkeys(text))

    def _remove_similar_elements(self, elements: List[str]) -> List[str]:
        """Removes elements that are permutations of each other."""
        sorted_elements = [''.join(sorted(e)) for e in elements]
        return list(dict.fromkeys(sorted_elements))

    def _categorize_attributes(self) -> AttributeCategories:
        """Categorizes attributes based on their appearance in dependencies."""
        temp_left = []
        temp_right = []

        # Collect attributes from dependencies
        for dep in self.dependencies:
            for attr in dep.determinant:
                temp_left.append(attr)
            for attr in dep.dependent:
                temp_right.append(attr)

        # Categorize attributes
        left = [attr for attr in temp_left if attr not in temp_right]
        right = [attr for attr in temp_right if attr not in temp_left]
        both = [attr for attr in temp_left if attr in temp_right]
        neither = [
            attr.strip() 
            for attr in self.attributes 
            if attr.strip() not in ''.join(left + right + both)
        ]

        return AttributeCategories(
            left=self._remove_similar_elements(left),
            right=self._remove_similar_elements(right),
            neither=self._remove_similar_elements(neither),
            both=self._remove_similar_elements(both)
        )

    def compute_closure(self, attributes: str) -> str:
        """Computes the attribute closure."""
        closure = set(attributes)
        changed = True
        
        while changed:
            changed = False
            for dep in self.dependencies:
                if set(dep.determinant).issubset(closure):
                    new_attrs = set(dep.dependent) - closure
                    if new_attrs:
                        closure.update(new_attrs)
                        changed = True
        
        return ''.join(sorted(closure))

    def find_candidate_keys(self) -> List[str]:
        """Finds all candidate keys for the relation."""
        # Initialize with attributes that must be in every key
        initial_key = (
            self.categories.both if not (self.categories.neither + self.categories.left)
            else [''.join(self.categories.neither + self.categories.left)]
        )

        keys = []
        attr_count = len(self.attributes)

        # Check initial candidates
        for key in initial_key:
            closure = self.compute_closure(key)
            if len(closure) == attr_count:
                keys.append(key)

        # Try combinations with attributes that appear on both sides
        if not keys:
            for attr in self.categories.both:
                for key in initial_key:
                    combined = attr + key
                    closure = self.compute_closure(combined)
                    if len(closure) == attr_count:
                        keys.append(combined)

        return self._remove_similar_elements(keys)


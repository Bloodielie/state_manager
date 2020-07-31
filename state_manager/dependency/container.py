from typing import Iterator

from state_manager.dependency.models import DependencyWrapper


class ExternalDependenciesContainer:
    external_dependencies = {}

    def bind(self, annotation, implementation) -> None:
        self.external_dependencies[annotation] = implementation

    def __iter__(self) -> Iterator[DependencyWrapper]:
        for key, value in self.external_dependencies.items():
            yield DependencyWrapper(type_=key, implementation=value)

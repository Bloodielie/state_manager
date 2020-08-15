from typing import Any

from state_manager.dependency.signature import get_signature_to_implementation


def _check_annotation(annotation: Any, dependency: Any) -> bool:
    try:
        if issubclass(annotation, dependency):
            return True
    except TypeError:
        if annotation == dependency:
            return True
    return False


def _is_context_in_implementation_attr(implementation: Any, context: Any) -> bool:
    signatures = get_signature_to_implementation(implementation)
    if signatures is None:
        return False
    else:
        for parameter in signatures.parameters.values():
            if _check_annotation(parameter.annotation, context):
                return True
        return False

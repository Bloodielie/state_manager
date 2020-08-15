import inspect
from typing import Callable, Dict, Any, Optional
from pydantic.typing import ForwardRef, evaluate_forwardref


def get_typed_signature(call: Callable) -> inspect.Signature:
    """Get the signatures of the callable object"""
    signature = inspect.signature(call)
    globalns = getattr(call, "__globals__", {})
    typed_params = [
        inspect.Parameter(
            name=param.name, kind=param.kind, default=param.default, annotation=get_typed_annotation(param, globalns),
        )
        for param in signature.parameters.values()
        if param.name != "self"
    ]
    typed_signature = inspect.Signature(typed_params)
    return typed_signature


def get_typed_annotation(param: inspect.Parameter, globalns: Dict[str, Any]) -> Any:
    annotation = param.annotation
    if isinstance(annotation, str):
        try:
            annotation = ForwardRef(annotation)  # type: ignore
            annotation = evaluate_forwardref(annotation, globalns, globalns)
        except (TypeError, NameError):
            annotation = param.annotation
    return annotation


def get_signature_to_implementation(implementation: Any) -> Optional[inspect.Signature]:
    if inspect.isclass(implementation):
        return get_typed_signature(implementation.__init__)
    elif inspect.isfunction(implementation) or inspect.ismethod(implementation):
        return get_typed_signature(implementation)
    elif hasattr(implementation, "__call__"):
        return get_typed_signature(implementation.__call__)

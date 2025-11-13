from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping, Optional

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@dataclass(slots=True)
class PresenterResult:
    """
    Wrapper object that carries either a direct ``HttpResponse`` or the data
    required to render a template.
    """

    template_name: Optional[str] = None
    context: Optional[Mapping[str, Any]] = None
    response: Optional[HttpResponse] = None


class BasePresenter:
    """
    Base class for presenter layer components.

    Presenters orchestrate data gathering from models/selectors/services and
    prepare a template context that views can render.  Views should be thin,
    delegating orchestration to presenters to align with the MVP approach.
    """

    template_name: str = ''

    def __init__(self, request: HttpRequest) -> None:
        self.request = request

    # --------------------------------------------------------------------- API
    def get_context_data(self) -> MutableMapping[str, Any]:
        """
        Build the context dictionary that will be passed to the template.
        Subclasses should override this method.
        """
        return {}

    def build(self) -> PresenterResult:
        """
        Produce a :class:`PresenterResult` instance.  Subclasses can override
        this method when they need to return a redirect or a completely custom
        response.  The default implementation falls back to rendering the
        template defined on the presenter.
        """
        context = self.get_context_data()
        return PresenterResult(template_name=self.template_name, context=context)

    def render(self) -> HttpResponse:
        """
        Execute the presenter and return an :class:`HttpResponse`.
        """
        result = self.build()
        if result.response is not None:
            return result.response
        template_name = result.template_name or self.template_name
        if not template_name:
            raise ValueError(f'{self.__class__.__name__} requires a template name.')
        context = dict(result.context or {})
        return render(self.request, template_name, context)


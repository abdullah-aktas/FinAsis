from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import PlanningScenario
from ..forms import PlanningScenarioForm


def scenario_list(request: HttpRequest) -> HttpResponse:
    scenarios = PlanningScenario.objects.all().order_by("-created_at")
    return render(request, "accounting/scenario_list.html", {"scenarios": scenarios})


def scenario_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PlanningScenarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounting:scenario_list")
    else:
        form = PlanningScenarioForm()
    return render(request, "accounting/scenario_form.html", {"form": form})


def scenario_detail(request: HttpRequest, pk: int) -> HttpResponse:
    scenario = get_object_or_404(PlanningScenario, pk=pk)
    return render(request, "accounting/scenario_detail.html", {"scenario": scenario})


def scenario_update(request: HttpRequest, pk: int) -> HttpResponse:
    scenario = get_object_or_404(PlanningScenario, pk=pk)
    if request.method == "POST":
        form = PlanningScenarioForm(request.POST, instance=scenario)
        if form.is_valid():
            form.save()
            return redirect("accounting:scenario_detail", pk=scenario.pk)
    else:
        form = PlanningScenarioForm(instance=scenario)
    return render(
        request, "accounting/scenario_form.html", {"form": form, "scenario": scenario}
    )


def scenario_delete(request: HttpRequest, pk: int) -> HttpResponse:
    scenario = get_object_or_404(PlanningScenario, pk=pk)
    if request.method == "POST":
        scenario.delete()
        return redirect("accounting:scenario_list")
    return render(
        request, "accounting/scenario_confirm_delete.html", {"scenario": scenario}
    )

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import Expense
from ..forms import ExpenseForm


def expense_list(request: HttpRequest) -> HttpResponse:
    expenses = Expense.objects.filter(is_active=True)
    return render(request, "accounting/expense_list.html", {"expenses": expenses})


def expense_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounting:expense_list")
    else:
        form = ExpenseForm()
    return render(request, "accounting/expense_form.html", {"form": form})


def expense_detail(request: HttpRequest, pk: int) -> HttpResponse:
    expense = get_object_or_404(Expense, pk=pk)
    return render(request, "accounting/expense_detail.html", {"expense": expense})


def expense_update(request: HttpRequest, pk: int) -> HttpResponse:
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect("accounting:expense_detail", pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense)
    return render(
        request, "accounting/expense_form.html", {"form": form, "expense": expense}
    )


def expense_delete(request: HttpRequest, pk: int) -> HttpResponse:
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        expense.delete()
        return redirect("accounting:expense_list")
    return render(
        request, "accounting/expense_confirm_delete.html", {"expense": expense}
    )

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import BankTransaction
from ..forms import BankTransactionForm


def banktransaction_list(request: HttpRequest) -> HttpResponse:
    banktransactions = BankTransaction.objects.filter(is_active=True)
    return render(
        request,
        "accounting/banktransaction_list.html",
        {"banktransactions": banktransactions},
    )


def banktransaction_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = BankTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounting:banktransaction_list")
    else:
        form = BankTransactionForm()
    return render(request, "accounting/banktransaction_form.html", {"form": form})


def banktransaction_detail(request: HttpRequest, pk: int) -> HttpResponse:
    banktransaction = get_object_or_404(BankTransaction, pk=pk)
    return render(
        request,
        "accounting/banktransaction_detail.html",
        {"banktransaction": banktransaction},
    )


def banktransaction_update(request: HttpRequest, pk: int) -> HttpResponse:
    banktransaction = get_object_or_404(BankTransaction, pk=pk)
    if request.method == "POST":
        form = BankTransactionForm(request.POST, instance=banktransaction)
        if form.is_valid():
            form.save()
            return redirect("accounting:banktransaction_detail", pk=banktransaction.pk)
    else:
        form = BankTransactionForm(instance=banktransaction)
    return render(
        request,
        "accounting/banktransaction_form.html",
        {"form": form, "banktransaction": banktransaction},
    )


def banktransaction_delete(request: HttpRequest, pk: int) -> HttpResponse:
    banktransaction = get_object_or_404(BankTransaction, pk=pk)
    if request.method == "POST":
        banktransaction.delete()
        return redirect("accounting:banktransaction_list")
    return render(
        request,
        "accounting/banktransaction_confirm_delete.html",
        {"banktransaction": banktransaction},
    )

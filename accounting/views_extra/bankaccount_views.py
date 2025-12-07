from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse
from ..models import BankAccount
from ..forms import BankAccountForm


def bankaccount_list(request: HttpRequest) -> HttpResponse:
    bankaccounts = BankAccount.objects.filter(is_active=True)
    return render(
        request, "accounting/bankaccount_list.html", {"bankaccounts": bankaccounts}
    )


def bankaccount_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = BankAccountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounting:bankaccount_list")
    else:
        form = BankAccountForm()
    return render(request, "accounting/bankaccount_form.html", {"form": form})


def bankaccount_detail(request: HttpRequest, pk: int) -> HttpResponse:
    bankaccount = get_object_or_404(BankAccount, pk=pk)
    return render(
        request, "accounting/bankaccount_detail.html", {"bankaccount": bankaccount}
    )


def bankaccount_update(request: HttpRequest, pk: int) -> HttpResponse:
    bankaccount = get_object_or_404(BankAccount, pk=pk)
    if request.method == "POST":
        form = BankAccountForm(request.POST, instance=bankaccount)
        if form.is_valid():
            form.save()
            return redirect("accounting:bankaccount_detail", pk=bankaccount.pk)
    else:
        form = BankAccountForm(instance=bankaccount)
    return render(
        request,
        "accounting/bankaccount_form.html",
        {"form": form, "bankaccount": bankaccount},
    )


def bankaccount_delete(request: HttpRequest, pk: int) -> HttpResponse:
    bankaccount = get_object_or_404(BankAccount, pk=pk)
    if request.method == "POST":
        bankaccount.delete()
        return redirect("accounting:bankaccount_list")
    return render(
        request,
        "accounting/bankaccount_confirm_delete.html",
        {"bankaccount": bankaccount},
    )

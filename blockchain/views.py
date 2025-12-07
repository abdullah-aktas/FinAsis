from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    ChainRecord,
    Block,
    Transaction,
    SmartContract,
    DigitalAsset,
    AssetBalance,
)
from .services import (
    BlockchainManager,
    TransactionManager,
    SmartContractManager,
    AssetManager,
)
import hashlib
import re
import json


# ============================================================================
# ANA DASHBOARD VE HOME
# ============================================================================


@login_required
def home(request):
    """Blockchain ana sayfası - dashboard"""
    # İstatistikler
    total_blocks = Block.objects.count()
    total_transactions = Transaction.objects.count()
    pending_transactions = Transaction.objects.filter(status="pending").count()
    total_contracts = SmartContract.objects.filter(is_active=True).count()
    total_assets = DigitalAsset.objects.count()

    # Son bloklar
    latest_blocks = Block.objects.select_related("mined_by").order_by("-block_number")[
        :5
    ]

    # Son transaction'lar
    latest_transactions = Transaction.objects.select_related(
        "block", "created_by"
    ).order_by("-timestamp")[:10]

    # Zincir sağlığı
    chain_valid, errors = BlockchainManager.verify_chain()

    # Son 7 günlük transaction grafiği
    last_7_days = []
    tx_counts = []
    for i in range(6, -1, -1):
        date = (timezone.now() - timedelta(days=i)).date()
        last_7_days.append(date.strftime("%d.%m"))
        count = Transaction.objects.filter(timestamp__date=date).count()
        tx_counts.append(count)

    context = {
        "total_blocks": total_blocks,
        "total_transactions": total_transactions,
        "pending_transactions": pending_transactions,
        "total_contracts": total_contracts,
        "total_assets": total_assets,
        "latest_blocks": latest_blocks,
        "latest_transactions": latest_transactions,
        "chain_valid": chain_valid,
        "chain_errors": errors if not chain_valid else [],
        "chart_labels": json.dumps(last_7_days),
        "chart_data": json.dumps(tx_counts),
    }

    return render(request, "blockchain/home.html", context)


# ============================================================================
# BLOCK YÖNETİMİ
# ============================================================================


@login_required
def block_list(request):
    """Blok listesi - blockchain explorer"""
    blocks = Block.objects.select_related("mined_by").order_by("-block_number")[:100]

    # Arama
    search_query = request.GET.get("q", "").strip()
    if search_query:
        if search_query.isdigit():
            blocks = blocks.filter(block_number=int(search_query))
        else:
            blocks = blocks.filter(block_hash__icontains=search_query)

    return render(
        request,
        "blockchain/block_list.html",
        {"blocks": blocks, "search_query": search_query},
    )


@login_required
def block_detail(request, block_number):
    """Blok detay sayfası"""
    block = get_object_or_404(Block, block_number=block_number)
    transactions = block.transactions.all()

    # Blok doğrulama
    calculated_hash = block.calculate_hash()
    is_valid = calculated_hash == block.block_hash

    return render(
        request,
        "blockchain/block_detail.html",
        {
            "block": block,
            "transactions": transactions,
            "is_valid": is_valid,
            "calculated_hash": calculated_hash,
        },
    )


@login_required
@require_POST
def create_new_block(request):
    """Yeni blok oluştur (mine)"""
    try:
        difficulty = int(request.POST.get("difficulty", 4))
        block = BlockchainManager.create_new_block(
            mined_by=request.user, difficulty=difficulty
        )

        return JsonResponse(
            {
                "success": True,
                "block_number": block.block_number,
                "block_hash": block.block_hash,
                "transactions_count": block.transactions_count,
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


# ============================================================================
# TRANSACTION YÖNETİMİ
# ============================================================================


@login_required
def transaction_list(request):
    """Transaction listesi"""
    transactions = Transaction.objects.select_related("block", "created_by").order_by(
        "-timestamp"
    )

    # Filtreleme
    tx_type = request.GET.get("type")
    status = request.GET.get("status")
    search_query = request.GET.get("q", "").strip()

    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)
    if status:
        transactions = transactions.filter(status=status)
    if search_query:
        transactions = transactions.filter(
            Q(transaction_id__icontains=search_query)
            | Q(from_address__icontains=search_query)
            | Q(to_address__icontains=search_query)
        )

    # Pagination
    transactions = transactions[:200]

    return render(
        request,
        "blockchain/transaction_list.html",
        {
            "transactions": transactions,
            "tx_types": Transaction.TRANSACTION_TYPES,
            "statuses": Transaction.STATUS_CHOICES,
            "selected_type": tx_type,
            "selected_status": status,
            "search_query": search_query,
        },
    )


@login_required
def transaction_detail(request, transaction_id):
    """Transaction detay sayfası"""
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)

    # Doğrulama
    is_valid, message = TransactionManager.verify_transaction(transaction_id)

    return render(
        request,
        "blockchain/transaction_detail.html",
        {
            "transaction": transaction,
            "is_valid": is_valid,
            "verification_message": message,
        },
    )


@login_required
def transaction_create(request):
    """Yeni transaction oluştur"""
    if request.method == "POST":
        try:
            tx = TransactionManager.create_transaction(
                transaction_type=request.POST.get("transaction_type"),
                from_address=request.POST.get("from_address"),
                to_address=request.POST.get("to_address"),
                amount=float(request.POST.get("amount", 0)),
                payload=json.loads(request.POST.get("payload", "{}")),
                created_by=request.user,
            )

            return redirect(
                "blockchain:transaction_detail", transaction_id=tx.transaction_id
            )
        except Exception as e:
            return render(
                request,
                "blockchain/transaction_create.html",
                {"error": str(e), "tx_types": Transaction.TRANSACTION_TYPES},
            )

    return render(
        request,
        "blockchain/transaction_create.html",
        {"tx_types": Transaction.TRANSACTION_TYPES},
    )


# ============================================================================
# SMART CONTRACT YÖNETİMİ
# ============================================================================


@login_required
def contract_list(request):
    """Akıllı sözleşme listesi"""
    contracts = SmartContract.objects.select_related("deployed_by").order_by(
        "-deployed_at"
    )

    # Filtreleme
    contract_type = request.GET.get("type")
    if contract_type:
        contracts = contracts.filter(contract_type=contract_type)

    return render(
        request,
        "blockchain/contract_list.html",
        {
            "contracts": contracts,
            "contract_types": SmartContract.CONTRACT_TYPES,
            "selected_type": contract_type,
        },
    )


@login_required
def contract_detail(request, contract_address):
    """Akıllı sözleşme detay"""
    contract = get_object_or_404(SmartContract, contract_address=contract_address)

    return render(request, "blockchain/contract_detail.html", {"contract": contract})


@login_required
def contract_deploy(request):
    """Yeni akıllı sözleşme deploy et"""
    if request.method == "POST":
        try:
            contract = SmartContractManager.deploy_contract(
                contract_name=request.POST.get("contract_name"),
                contract_type=request.POST.get("contract_type"),
                code=request.POST.get("code"),
                deployed_by=request.user,
                parameters=json.loads(request.POST.get("parameters", "{}")),
            )

            return redirect(
                "blockchain:contract_detail", contract_address=contract.contract_address
            )
        except Exception as e:
            return render(
                request,
                "blockchain/contract_deploy.html",
                {"error": str(e), "contract_types": SmartContract.CONTRACT_TYPES},
            )

    return render(
        request,
        "blockchain/contract_deploy.html",
        {"contract_types": SmartContract.CONTRACT_TYPES},
    )


@login_required
@require_POST
def contract_execute(request, contract_address):
    """Akıllı sözleşme çalıştır"""
    try:
        params = json.loads(request.POST.get("parameters", "{}"))
        result = SmartContractManager.execute_contract(contract_address, params)

        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


# ============================================================================
# DİJİTAL VARLIK YÖNETİMİ
# ============================================================================


@login_required
def asset_list(request):
    """Dijital varlık listesi"""
    assets = DigitalAsset.objects.select_related("owner").order_by("-created_at")

    # Filtreleme
    asset_type = request.GET.get("type")
    if asset_type:
        assets = assets.filter(asset_type=asset_type)

    return render(
        request,
        "blockchain/asset_list.html",
        {
            "assets": assets,
            "asset_types": DigitalAsset.ASSET_TYPES,
            "selected_type": asset_type,
        },
    )


@login_required
def asset_detail(request, asset_id):
    """Dijital varlık detay"""
    asset = get_object_or_404(DigitalAsset, asset_id=asset_id)

    # Kullanıcının bakiyesi
    user_balance = AssetBalance.objects.filter(user=request.user, asset=asset).first()

    # Top holders
    top_holders = (
        AssetBalance.objects.filter(asset=asset)
        .select_related("user")
        .order_by("-balance")[:10]
    )

    return render(
        request,
        "blockchain/asset_detail.html",
        {"asset": asset, "user_balance": user_balance, "top_holders": top_holders},
    )


@login_required
def asset_create(request):
    """Yeni dijital varlık oluştur"""
    if request.method == "POST":
        try:
            asset = AssetManager.create_asset(
                asset_name=request.POST.get("asset_name"),
                asset_symbol=request.POST.get("asset_symbol"),
                asset_type=request.POST.get("asset_type"),
                total_supply=float(request.POST.get("total_supply")),
                owner=request.user,
                metadata=json.loads(request.POST.get("metadata", "{}")),
            )

            return redirect("blockchain:asset_detail", asset_id=asset.asset_id)
        except Exception as e:
            return render(
                request,
                "blockchain/asset_create.html",
                {"error": str(e), "asset_types": DigitalAsset.ASSET_TYPES},
            )

    return render(
        request,
        "blockchain/asset_create.html",
        {"asset_types": DigitalAsset.ASSET_TYPES},
    )


@login_required
def my_assets(request):
    """Kullanıcının varlıkları"""
    balances = (
        AssetBalance.objects.filter(user=request.user)
        .select_related("asset")
        .order_by("-balance")
    )

    return render(request, "blockchain/my_assets.html", {"balances": balances})


# ============================================================================
# LEGACY VIEWS (Geriye Uyumluluk)
# ============================================================================


@require_POST
def api_verify(request):
    """Legacy verify API"""
    reference = request.POST.get("reference")
    payload = request.POST.get("payload")
    if not reference or not payload:
        return HttpResponseBadRequest("reference and payload required")
    hash_hex = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    exists = ChainRecord.objects.filter(reference=reference, hash_hex=hash_hex).exists()
    return JsonResponse(
        {"reference": reference, "hash_hex": hash_hex, "verified": exists}
    )


def record_list(request):
    """Legacy record list"""
    q = request.GET.get("q", "").strip()
    qs = ChainRecord.objects.all()
    if q:
        qs = qs.filter(reference__icontains=q)
    records = qs[:200]
    return render(request, "blockchain/record_list.html", {"records": records, "q": q})


def record_export_csv(request):
    """Legacy CSV export"""
    q = request.GET.get("q", "").strip()
    qs = ChainRecord.objects.all()
    if q:
        qs = qs.filter(reference__icontains=q)
    rows = [["reference", "hash_hex", "status", "created_at"]]
    for r in qs.iterator():
        rows.append([r.reference, r.hash_hex, r.status, r.created_at.isoformat()])
    content = "\n".join(
        [
            ",".join([str(c).replace("\n", " ").replace("\r", " ") for c in row])
            for row in rows
        ]
    )
    resp = HttpResponse(content, content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="chain_records.csv"'
    return resp


def record_create(request):
    """Legacy record create"""
    if request.method == "POST":
        from django.urls import reverse

        reference = request.POST.get("reference")
        payload = request.POST.get("payload")
        status = request.POST.get("status") or "pending"
        if not reference or not payload:
            return HttpResponseBadRequest("reference and payload required")
        hash_hex = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        ChainRecord.objects.create(
            reference=reference,
            hash_hex=hash_hex,
            payload_preview=payload[:500],
            status=status,
        )
        return redirect(reverse("blockchain:record_list"))
    return render(request, "blockchain/record_create.html")


# Placeholder views
def transactions_list(request):
    return redirect("blockchain:transaction_list")


def contracts_list(request):
    return redirect("blockchain:contract_list")


def assets_list(request):
    return redirect("blockchain:asset_list")


def reports(request):
    return render(request, "blockchain/reports.html")


def anchor_wizard(request):
    return render(request, "blockchain/anchor_wizard.html")


def verify_wizard(request):
    return render(request, "blockchain/verify_wizard.html")


@require_POST
def api_anchor(request):
    """Legacy anchor API"""
    reference = (request.POST.get("reference") or "").strip()
    hash_hex = (request.POST.get("hash_hex") or "").strip().lower()
    status = (request.POST.get("status") or "anchored").strip()
    if not reference or not hash_hex:
        return HttpResponseBadRequest("reference and hash_hex required")
    if not re.fullmatch(r"[0-9a-f]{64}", hash_hex):
        return HttpResponseBadRequest("hash_hex must be 64 hex chars")
    rec = ChainRecord.objects.create(
        reference=reference,
        hash_hex=hash_hex,
        payload_preview="",
        status=status or "anchored",
    )
    return JsonResponse(
        {
            "created": True,
            "reference": rec.reference,
            "hash_hex": rec.hash_hex,
            "status": rec.status,
        }
    )


@require_POST
def api_verify_hash(request):
    """Legacy verify hash API"""
    reference = (request.POST.get("reference") or "").strip()
    hash_hex = (request.POST.get("hash_hex") or "").strip().lower()
    if not hash_hex:
        return HttpResponseBadRequest("hash_hex required")
    if not re.fullmatch(r"[0-9a-f]{64}", hash_hex):
        return HttpResponseBadRequest("hash_hex must be 64 hex chars")
    qs = ChainRecord.objects.filter(hash_hex=hash_hex)
    if reference:
        qs = qs.filter(reference=reference)
    exists = qs.exists()
    return JsonResponse(
        {
            "reference": reference,
            "hash_hex": hash_hex,
            "verified": exists,
            "count": qs.count(),
        }
    )

from decimal import Decimal

from FinAsis.src.apps.finance.accounting.inventory_avg import AvgState, receive, issue


def test_moving_average_cost():
    st = AvgState()
    receive(st, Decimal("10"), Decimal("5.00"))
    assert st.avg_cost == Decimal("5.0000")
    receive(st, Decimal("10"), Decimal("7.00"))
    # new average should be 6.0000
    assert st.avg_cost == Decimal("6.0000")
    cogs = issue(st, Decimal("5"))
    assert cogs == Decimal("30.00")
    assert st.qty == Decimal("15")
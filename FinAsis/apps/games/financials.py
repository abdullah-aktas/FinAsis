from typing import Dict

class FinancialRatios:
    @staticmethod
    def calculate_current_ratio(assets: float, liabilities: float) -> float:
        return assets / liabilities if liabilities else 0

    @staticmethod
    def calculate_debt_to_equity(liabilities: float, equity: float) -> float:
        return liabilities / equity if equity else 0

    @staticmethod
    def calculate_profit_margin(net_income: float, revenue: float) -> float:
        return (net_income / revenue) * 100 if revenue else 0

    @staticmethod
    def calculate_return_on_assets(net_income: float, assets: float) -> float:
        return net_income / assets if assets else 0

    @staticmethod
    def calculate_return_on_equity(net_income: float, equity: float) -> float:
        return net_income / equity if equity else 0

class FinancialReportManager:
    @staticmethod
    def generate_balance_sheet(accounts: Dict) -> Dict:
        balance_sheet = {
            "assets": {},
            "liabilities": {},
            "equity": {}
        }
        for acc in accounts.values():
            if hasattr(acc, 'type') and hasattr(acc, 'balance'):
                if acc.type.name == "ASSET":
                    balance_sheet["assets"][acc.id] = acc.balance
                elif acc.type.name == "LIABILITY":
                    balance_sheet["liabilities"][acc.id] = acc.balance
                elif acc.type.name == "EQUITY":
                    balance_sheet["equity"][acc.id] = acc.balance
        return balance_sheet

    @staticmethod
    def generate_income_statement(accounts: Dict) -> Dict:
        income_statement = {
            "revenues": {},
            "expenses": {},
            "net_income": 0.0
        }
        for acc in accounts.values():
            if hasattr(acc, 'type') and hasattr(acc, 'balance'):
                if acc.type.name == "REVENUE":
                    income_statement["revenues"][acc.id] = acc.balance
                elif acc.type.name == "EXPENSE":
                    income_statement["expenses"][acc.id] = acc.balance
        total_revenue = sum(income_statement["revenues"].values())
        total_expense = sum(income_statement["expenses"].values())
        income_statement["net_income"] = total_revenue - total_expense
        return income_statement 
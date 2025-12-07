from django.shortcuts import redirect
from django.urls import reverse


class AutoOnboardingMiddleware:
    """
    Giriş yapmış kullanıcılar için bir kez onboarding tetikler.
    Oturumda 'trade_sim_onboarded' yoksa ve istek HTML sayfalarına ise
    onboarding endpoint'ine yönlendirir, tamamlanınca flag set edilir.
    API çağrılarını gereksiz yönlendirmemek için sadece GET ve HTML sayfalarında çalışır.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            if request.method == "GET" and request.user.is_authenticated:
                if not request.session.get("trade_sim_onboarded", False):
                    path = request.path
                    if (
                        not path.startswith("/admin")
                        and not path.startswith("/api")
                        and "trade-sim" not in path
                    ):
                        request.session["trade_sim_onboarded"] = True
                        return redirect(reverse("trade_sim:onboarding"))
        except Exception:
            # Sessiz geç; oyunu bloklamayalım
            pass
        response = self.get_response(request)
        return response

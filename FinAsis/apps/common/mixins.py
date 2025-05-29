class TimestampMixin:
    """
    Modelin oluşturulma ve güncellenme zamanını otomatik olarak tutar.
    """
    created_at = None
    updated_at = None
    # Django modelinde kullanmak için abstract base class olarak genişletilebilir. 
"""
Özel doğrulayıcılar.
Bu modül, proje genelinde kullanılacak özel doğrulayıcıları içerir.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_tc_kimlik_no(value):
    """
    TC Kimlik Numarası doğrulayıcı.
    """
    if not value.isdigit() or len(value) != 11:
        raise ValidationError(
            _('Geçersiz TC Kimlik Numarası formatı.'),
            code='invalid_tc_kimlik'
        )
    
    # TC Kimlik Numarası algoritması
    digits = [int(d) for d in value]
    
    if digits[0] == 0:
        raise ValidationError(
            _('TC Kimlik Numarası 0 ile başlayamaz.'),
            code='invalid_tc_kimlik'
        )
    
    if not ((sum(digits[:10]) % 10) == digits[10]):
        raise ValidationError(
            _('Geçersiz TC Kimlik Numarası.'),
            code='invalid_tc_kimlik'
        )
    
    if not (((7 * sum(digits[:9][-1::-2]) - sum(digits[:9][-2::-2])) % 10) == digits[9]):
        raise ValidationError(
            _('Geçersiz TC Kimlik Numarası.'),
            code='invalid_tc_kimlik'
        )

def validate_iban(value):
    """
    IBAN doğrulayıcı.
    """
    value = value.replace(' ', '').upper()
    
    if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$', value):
        raise ValidationError(
            _('Geçersiz IBAN formatı.'),
            code='invalid_iban'
        )
    
    # IBAN doğrulama algoritması
    country_code = value[:2]
    check_digits = value[2:4]
    bban = value[4:]
    
    # Türkiye için özel kontrol
    if country_code == 'TR':
        if not re.match(r'^[0-9]{5}[A-Z0-9]{17}$', bban):
            raise ValidationError(
                _('Geçersiz Türk IBAN formatı.'),
                code='invalid_iban'
            )

def validate_phone_number(value):
    """
    Telefon numarası doğrulayıcı.
    """
    if not re.match(r'^\+?[0-9]{10,15}$', value):
        raise ValidationError(
            _('Geçersiz telefon numarası formatı.'),
            code='invalid_phone'
        )

def validate_tax_number(value):
    """
    Vergi numarası doğrulayıcı.
    """
    if not value.isdigit() or len(value) != 10:
        raise ValidationError(
            _('Geçersiz vergi numarası formatı.'),
            code='invalid_tax_number'
        )
    
    # Vergi numarası algoritması
    digits = [int(d) for d in value]
    last_digit = digits[-1]
    
    sum_digits = sum(digits[:-1])
    calculated_last_digit = (sum_digits % 10)
    
    if calculated_last_digit != last_digit:
        raise ValidationError(
            _('Geçersiz vergi numarası.'),
            code='invalid_tax_number'
        )

def validate_credit_card(value):
    """
    Kredi kartı numarası doğrulayıcı.
    """
    value = value.replace(' ', '')
    
    if not value.isdigit() or len(value) < 13 or len(value) > 19:
        raise ValidationError(
            _('Geçersiz kredi kartı numarası formatı.'),
            code='invalid_credit_card'
        )
    
    # Luhn algoritması
    digits = [int(d) for d in value]
    checksum = 0
    
    for i, digit in enumerate(digits[-2::-1]):
        if i % 2 == 0:
            doubled = digit * 2
            checksum += doubled if doubled < 10 else doubled - 9
        else:
            checksum += digit
    
    if (checksum * 9) % 10 != digits[-1]:
        raise ValidationError(
            _('Geçersiz kredi kartı numarası.'),
            code='invalid_credit_card'
        )

def validate_password(value):
    """
    Şifre doğrulayıcı.
    """
    if len(value) < 8:
        raise ValidationError(
            _('Şifre en az 8 karakter uzunluğunda olmalıdır.'),
            code='password_too_short'
        )
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError(
            _('Şifre en az bir büyük harf içermelidir.'),
            code='password_no_upper'
        )
    
    if not re.search(r'[a-z]', value):
        raise ValidationError(
            _('Şifre en az bir küçük harf içermelidir.'),
            code='password_no_lower'
        )
    
    if not re.search(r'[0-9]', value):
        raise ValidationError(
            _('Şifre en az bir rakam içermelidir.'),
            code='password_no_digit'
        )
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError(
            _('Şifre en az bir özel karakter içermelidir.'),
            code='password_no_special'
        ) 
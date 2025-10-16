#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FinAsis Demo Senaryo Verisi Oluşturma
Her kullanıcı tipi için gerçekçi demo verileri oluşturur.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
from random import randint, choice, uniform

# Django setup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from src.apps.accounts.models import CustomUser, UserType, SubscriptionType, Subscription, Achievement
from src.apps.accounting.models import Company, Invoice, Expense, Customer, Product, BankAccount, BankTransaction
from django.contrib.auth.hashers import make_password


class DemoScenarioCreator:
    """Her kullanıcı tipi için demo senaryo verisi oluşturur"""

    def __init__(self):
        self.user_types = {}
        self.subscription_types = {}
        self._load_types()

    def _load_types(self):
        """Kullanıcı ve abonelik tiplerini yükle"""
        print("📥 Tipler yükleniyor...")
        
        # UserType'ları al veya oluştur
        user_type_data = [
            {'code': 'kobi', 'name': 'KOBİ'},
            {'code': 'egitimci', 'name': 'Eğitimci'},
            {'code': 'ogrenci', 'name': 'Öğrenci'},
            {'code': 'oyuncu', 'name': 'Oyuncu'},
        ]
        
        for ut_data in user_type_data:
            ut, created = UserType.objects.get_or_create(
                code=ut_data['code'],
                defaults={'name': ut_data['name']}
            )
            self.user_types[ut_data['code']] = ut
            print(f"  {'✅ Oluşturuldu' if created else '✓ Mevcut'}: {ut.name}")

        # SubscriptionType'ları al veya oluştur
        sub_type_data = [
            {'code': 'basic', 'name': 'Temel'},
            {'code': 'premium', 'name': 'Premium'},
            {'code': 'pro', 'name': 'Pro'},
            {'code': 'edu_student', 'name': 'Eğitim Öğrenci'},
        ]
        
        for st_data in sub_type_data:
            st, created = SubscriptionType.objects.get_or_create(
                code=st_data['code'],
                defaults={'name': st_data['name']}
            )
            self.subscription_types[st_data['code']] = st
            print(f"  {'✅ Oluşturuldu' if created else '✓ Mevcut'}: {st.name}")

    def create_kobi_scenario(self):
        """📊 KOBİ kullanıcı senaryosu"""
        print("\n" + "="*60)
        print("📊 KOBİ Kullanıcı Senaryosu Oluşturuluyor...")
        print("="*60)

        # 1. Kullanıcı oluştur
        username = 'kobi_demo'
        email = 'kobi@demo.finasis.com'
        
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': 'Ahmet',
                'last_name': 'Yılmaz',
                'password': make_password('Demo123!'),
                'role': 'admin',
                'user_type': self.user_types['kobi']
            }
        )
        
        if created:
            print(f"✅ Kullanıcı oluşturuldu: {username}")
        else:
            print(f"✓ Mevcut kullanıcı: {username}")

        # 2. Şirket oluştur
        company, created = Company.objects.get_or_create(
            tax_number='1234567890',
            defaults={
                'name': 'YazılımTech A.Ş.',
                'sector': 'Bilişim',
                'address': 'Teknoloji Vadisi, İstanbul',
                'phone': '+90 212 123 45 67',
                'email': 'info@yazilimtech.com'
            }
        )
        
        user.company = company
        user.save()
        
        if created:
            print(f"✅ Şirket oluşturuldu: {company.name}")
        else:
            print(f"✓ Mevcut şirket: {company.name}")

        # 3. Abonelik oluştur
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'subscription_type': self.subscription_types['premium'],
                'is_active': True,
                'end_date': datetime.now().date() + timedelta(days=30)
            }
        )
        
        if created:
            print(f"✅ Abonelik oluşturuldu: Premium (30 gün)")

        # 4. Müşteriler oluştur
        print("\n📋 Müşteriler oluşturuluyor...")
        customers_data = [
            {'name': 'ABC Ltd. Şti.', 'tax': '1111111111'},
            {'name': 'XYZ Teknoloji A.Ş.', 'tax': '2222222222'},
            {'name': 'Global Yazılım', 'tax': '3333333333'},
            {'name': 'Beta Solutions', 'tax': '4444444444'},
            {'name': 'Mega Corp', 'tax': '5555555555'},
        ]
        
        customers = []
        for cust_data in customers_data:
            cust, created = Customer.objects.get_or_create(
                company=company,
                tax_number=cust_data['tax'],
                defaults={
                    'name': cust_data['name'],
                    'email': f"info@{cust_data['name'].lower().replace(' ', '').replace('.', '')}.com",
                    'phone': f'+90 {randint(200, 599)} {randint(100, 999)} {randint(1000, 9999)}'
                }
            )
            customers.append(cust)
            if created:
                print(f"  ✅ {cust.name}")

        # 5. Ürünler oluştur
        print("\n🛍️ Ürünler oluşturuluyor...")
        products_data = [
            {'name': 'Yazılım Geliştirme Hizmeti', 'price': Decimal('15000.00')},
            {'name': 'Web Tasarım', 'price': Decimal('8000.00')},
            {'name': 'Mobil Uygulama', 'price': Decimal('25000.00')},
            {'name': 'SEO Danışmanlığı', 'price': Decimal('3000.00')},
            {'name': 'Hosting Hizmeti', 'price': Decimal('500.00')},
        ]
        
        products = []
        for prod_data in products_data:
            prod, created = Product.objects.get_or_create(
                company=company,
                name=prod_data['name'],
                defaults={
                    'price': prod_data['price'],
                    'stock': randint(5, 50)
                }
            )
            products.append(prod)
            if created:
                print(f"  ✅ {prod.name} - {prod.price} TL")

        # 6. Faturalar oluştur (son 3 ay)
        print("\n🧾 Faturalar oluşturuluyor...")
        invoice_count = 0
        for month_offset in range(3):
            for week in range(4):
                invoice_date = datetime.now() - timedelta(days=(month_offset * 30 + week * 7))
                
                for _ in range(randint(2, 5)):  # Her hafta 2-5 fatura
                    customer = choice(customers)
                    product = choice(products)
                    quantity = randint(1, 3)
                    amount = product.price * quantity
                    
                    invoice, created = Invoice.objects.get_or_create(
                        company=company,
                        invoice_number=f"2025/{1000 + invoice_count}",
                        defaults={
                            'customer': customer,
                            'date': invoice_date.date(),
                            'amount': amount,
                            'status': choice(['paid', 'paid', 'paid', 'pending'])  # %75 ödendi
                        }
                    )
                    
                    if created:
                        invoice_count += 1

        print(f"  ✅ {invoice_count} fatura oluşturuldu")

        # 7. Giderler oluştur
        print("\n💸 Giderler oluşturuluyor...")
        expense_categories = [
            'Ofis Kirası', 'Elektrik', 'İnternet', 'Maaşlar', 
            'Kırtasiye', 'Ulaşım', 'Yazılım Lisansları', 'Reklam'
        ]
        
        expense_count = 0
        for month_offset in range(3):
            for category in expense_categories:
                expense_date = datetime.now() - timedelta(days=(month_offset * 30 + randint(1, 28)))
                
                expense, created = Expense.objects.get_or_create(
                    company=company,
                    date=expense_date.date(),
                    category=category,
                    defaults={
                        'description': f"{category} - {expense_date.strftime('%B %Y')}",
                        'amount': Decimal(str(randint(500, 15000))),
                    }
                )
                
                if created:
                    expense_count += 1

        print(f"  ✅ {expense_count} gider kaydı oluşturuldu")

        # 8. Banka hesabı ve işlemler
        print("\n🏦 Banka hesabı oluşturuluyor...")
        bank_account, created = BankAccount.objects.get_or_create(
            company=company,
            account_number='TR330006100519786457841326',
            defaults={
                'bank_name': 'İş Bankası',
                'branch': 'Kadıköy Şubesi',
                'balance': Decimal('250000.00')
            }
        )
        
        if created:
            print(f"  ✅ {bank_account.bank_name} - Bakiye: {bank_account.balance} TL")

        # Banka işlemleri
        transaction_types = ['deposit', 'withdrawal', 'transfer']
        transaction_count = 0
        
        for day_offset in range(90):
            for _ in range(randint(1, 3)):
                trans_date = datetime.now() - timedelta(days=day_offset)
                trans_type = choice(transaction_types)
                
                trans, created = BankTransaction.objects.get_or_create(
                    bank_account=bank_account,
                    date=trans_date.date(),
                    transaction_type=trans_type,
                    defaults={
                        'amount': Decimal(str(randint(1000, 50000))),
                        'description': f"{trans_type.title()} - {trans_date.strftime('%d/%m/%Y')}"
                    }
                )
                
                if created:
                    transaction_count += 1

        print(f"  ✅ {transaction_count} banka işlemi oluşturuldu")

        # 9. Başarımlar
        print("\n🏆 Başarımlar ekleniyor...")
        achievements_data = [
            {'title': 'Hızlı Başlangıç', 'description': 'İlk 5 faturayı kestiniz', 'icon': '🚀'},
            {'title': 'Düzenli Kullanıcı', 'description': '30 gün boyunca aktif', 'icon': '⭐'},
            {'title': 'Finansal Analiz', 'description': 'İlk raporunuzu görüntülediniz', 'icon': '📊'},
        ]
        
        for ach_data in achievements_data:
            ach, created = Achievement.objects.get_or_create(
                company=company,
                title=ach_data['title'],
                defaults={
                    'description': ach_data['description'],
                    'icon': ach_data['icon'],
                    'date_earned': datetime.now().date()
                }
            )
            
            if created:
                print(f"  ✅ {ach.icon} {ach.title}")

        print("\n✨ KOBİ senaryosu tamamlandı!")
        print(f"🔑 Giriş Bilgileri:")
        print(f"   Kullanıcı: {username}")
        print(f"   Şifre: Demo123!")
        print(f"   URL: http://127.0.0.1:8000/accounts/login/")

    def create_egitimci_scenario(self):
        """🎓 Eğitimci kullanıcı senaryosu"""
        print("\n" + "="*60)
        print("🎓 Eğitimci Kullanıcı Senaryosu Oluşturuluyor...")
        print("="*60)

        username = 'egitimci_demo'
        email = 'egitimci@demo.finasis.com'
        
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': 'Elif',
                'last_name': 'Arslan',
                'password': make_password('Demo123!'),
                'role': 'staff',
                'user_type': self.user_types['egitimci']
            }
        )
        
        if created:
            print(f"✅ Kullanıcı oluşturuldu: {username}")
            print(f"   Email: {email}")
            print(f"   Rol: Eğitimci")

        # Abonelik
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'subscription_type': self.subscription_types['premium'],
                'is_active': True,
                'end_date': datetime.now().date() + timedelta(days=365)
            }
        )

        print("\n✨ Eğitimci senaryosu tamamlandı!")
        print(f"🔑 Giriş Bilgileri:")
        print(f"   Kullanıcı: {username}")
        print(f"   Şifre: Demo123!")
        print(f"   URL: http://127.0.0.1:8000/accounts/login/")

    def create_ogrenci_scenario(self):
        """📚 Öğrenci kullanıcı senaryosu"""
        print("\n" + "="*60)
        print("📚 Öğrenci Kullanıcı Senaryosu Oluşturuluyor...")
        print("="*60)

        username = 'ogrenci_demo'
        email = 'ogrenci@demo.finasis.com'
        
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': 'Ali',
                'last_name': 'Yıldız',
                'password': make_password('Demo123!'),
                'role': 'viewer',
                'user_type': self.user_types['ogrenci']
            }
        )
        
        if created:
            print(f"✅ Kullanıcı oluşturuldu: {username}")
            print(f"   Email: {email}")
            print(f"   Rol: Öğrenci")

        # Öğrenci aboneliği (indirimli)
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'subscription_type': self.subscription_types.get('edu_student', self.subscription_types['basic']),
                'is_active': True,
                'end_date': datetime.now().date() + timedelta(days=30)
            }
        )

        print("\n✨ Öğrenci senaryosu tamamlandı!")
        print(f"🔑 Giriş Bilgileri:")
        print(f"   Kullanıcı: {username}")
        print(f"   Şifre: Demo123!")
        print(f"   URL: http://127.0.0.1:8000/accounts/login/")

    def create_oyuncu_scenario(self):
        """🎮 Oyuncu kullanıcı senaryosu"""
        print("\n" + "="*60)
        print("🎮 Oyuncu Kullanıcı Senaryosu Oluşturuluyor...")
        print("="*60)

        username = 'oyuncu_demo'
        email = 'oyuncu@demo.finasis.com'
        
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': 'Cem',
                'last_name': 'Yılmaz',
                'password': make_password('Demo123!'),
                'role': 'viewer',
                'user_type': self.user_types['oyuncu']
            }
        )
        
        if created:
            print(f"✅ Kullanıcı oluşturuldu: {username}")
            print(f"   Email: {email}")
            print(f"   Rol: Oyuncu")

        # Freemium başlangıç
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'subscription_type': self.subscription_types['basic'],
                'is_active': True,
                'end_date': None  # Süresiz freemium
            }
        )

        print("\n✨ Oyuncu senaryosu tamamlandı!")
        print(f"🔑 Giriş Bilgileri:")
        print(f"   Kullanıcı: {username}")
        print(f"   Şifre: Demo123!")
        print(f"   URL: http://127.0.0.1:8000/accounts/login/")

    def create_all_scenarios(self):
        """Tüm senaryoları oluştur"""
        print("\n" + "🎬 "*20)
        print("FinAsis Demo Senaryoları Oluşturuluyor".center(80))
        print("🎬 "*20 + "\n")

        self.create_kobi_scenario()
        self.create_egitimci_scenario()
        self.create_ogrenci_scenario()
        self.create_oyuncu_scenario()

        print("\n" + "="*80)
        print("🎉 TÜM SENARYOLAR BAŞARIYLA OLUŞTURULDU!".center(80))
        print("="*80)
        
        print("\n📝 Demo Kullanıcıları:")
        print("   1. KOBİ Demo      → kobi_demo / Demo123!")
        print("   2. Eğitimci Demo  → egitimci_demo / Demo123!")
        print("   3. Öğrenci Demo   → ogrenci_demo / Demo123!")
        print("   4. Oyuncu Demo    → oyuncu_demo / Demo123!")
        
        print("\n🌐 Giriş URL'si:")
        print("   http://127.0.0.1:8000/accounts/login/")
        
        print("\n💡 Sonraki Adımlar:")
        print("   1. Sunucuyu başlatın: python manage.py runserver")
        print("   2. Demo kullanıcılarından biriyle giriş yapın")
        print("   3. İlgili modülleri keşfedin")
        print("   4. Senaryoları test edin")
        
        print("\n📚 Detaylı senaryolar için:")
        print("   docs/kullanici_senaryolari.md")
        print("   docs/kullanici_senaryolari_ozet.md")


def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FinAsis Demo Senaryoları Oluştur')
    parser.add_argument(
        '--type',
        choices=['kobi', 'egitimci', 'ogrenci', 'oyuncu', 'all'],
        default='all',
        help='Oluşturulacak senaryo tipi (varsayılan: all)'
    )
    
    args = parser.parse_args()
    
    creator = DemoScenarioCreator()
    
    if args.type == 'all':
        creator.create_all_scenarios()
    elif args.type == 'kobi':
        creator.create_kobi_scenario()
    elif args.type == 'egitimci':
        creator.create_egitimci_scenario()
    elif args.type == 'ogrenci':
        creator.create_ogrenci_scenario()
    elif args.type == 'oyuncu':
        creator.create_oyuncu_scenario()


if __name__ == '__main__':
    main()

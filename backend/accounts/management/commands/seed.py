from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Wypełnia bazę danych przykładowymi danymi"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Usuń istniejące dane przed dodaniem nowych",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self._clear()

        self._create_users()
        self._create_products()
        self._create_orders()
        self._create_contact_messages()

        self.stdout.write(self.style.SUCCESS("Dane dodane!"))
        self.stdout.write("")
        self.stdout.write("  Konta:")
        self.stdout.write("    admin  / Admin123!  (superuser)")
        self.stdout.write("    jan    / User123!   (klient)")
        self.stdout.write("    anna   / User123!   (klient)")

    def _clear(self):
        from orders.models import Order, OrderItem
        from products.models import Category, Product
        from contact.models import ContactMessage

        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        ContactMessage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING("Wyczyszczono dane."))

    def _create_users(self):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@studio.pl",
                password="Admin123!",
                first_name="Adam",
                last_name="Adminowski",
            )
            self.stdout.write("  Utworzono: admin")

        for data in [
            dict(username="jan", email="jan@example.com", password="User123!",
                 first_name="Jan", last_name="Kowalski",
                 phone="600 100 200", company="JK Design"),
            dict(username="anna", email="anna@example.com", password="User123!",
                 first_name="Anna", last_name="Nowak",
                 phone="700 200 300", company=""),
        ]:
            if not User.objects.filter(username=data["username"]).exists():
                pwd = data.pop("password")
                u = User(**data)
                u.set_password(pwd)
                u.save()
                self.stdout.write(f"  Utworzono: {u.username}")

    def _create_products(self):
        from products.models import Category, Product

        www, _ = Category.objects.get_or_create(name="Strony WWW", defaults={"slug": "strony-www"})
        grafika, _ = Category.objects.get_or_create(name="Grafika", defaults={"slug": "grafika"})
        marketing, _ = Category.objects.get_or_create(name="Marketing", defaults={"slug": "marketing"})

        products = [
            dict(category=www, name="Strona wizytówka", slug="strona-wizytowka",
                 description="Prosta, elegancka strona prezentująca Twoją firmę. "
                              "Responsywna, zoptymalizowana pod SEO, gotowa w 7 dni.",
                 price="1500.00", is_active=True),
            dict(category=www, name="Sklep internetowy", slug="sklep-internetowy",
                 description="Kompletny sklep e-commerce z panelem zarządzania, "
                              "integracją płatności i systemem zamówień.",
                 price="8500.00", is_active=True),
            dict(category=www, name="Aplikacja webowa", slug="aplikacja-webowa",
                 description="Dedykowana aplikacja webowa dopasowana do Twoich procesów biznesowych. "
                              "React + Django REST API.",
                 price="15000.00", is_active=True),
            dict(category=grafika, name="Logo firmowe", slug="logo-firmowe",
                 description="Profesjonalne logo w 3 wariantach kolorystycznych. "
                              "Pliki źródłowe AI/EPS + wersje PNG/SVG.",
                 price="800.00", is_active=True),
            dict(category=grafika, name="Identyfikacja wizualna", slug="identyfikacja-wizualna",
                 description="Kompletna identyfikacja: logo, kolory, typografia, wizytówki, "
                              "papier firmowy, szablon prezentacji.",
                 price="3500.00", is_active=True),
            dict(category=marketing, name="Kampania Google Ads", slug="kampania-google-ads",
                 description="Konfiguracja i prowadzenie kampanii Google Ads przez miesiąc. "
                              "Raport miesięczny i optymalizacja.",
                 price="1200.00", is_active=True),
            dict(category=marketing, name="Social media — pakiet startowy", slug="social-media-pakiet",
                 description="8 postów miesięcznie na 2 platformach. Szablony graficzne + teksty.",
                 price="900.00", is_active=False),
        ]

        for data in products:
            Product.objects.get_or_create(slug=data["slug"], defaults=data)
        self.stdout.write(f"  Produkty: {len(products)} (1 nieaktywny)")

    def _create_orders(self):
        from orders.models import Order, OrderItem
        from products.models import Product

        jan = User.objects.filter(username="jan").first()
        anna = User.objects.filter(username="anna").first()
        if not jan or not anna:
            return

        wizytowka = Product.objects.filter(slug="strona-wizytowka").first()
        logo = Product.objects.filter(slug="logo-firmowe").first()
        identyfikacja = Product.objects.filter(slug="identyfikacja-wizualna").first()
        kampania = Product.objects.filter(slug="kampania-google-ads").first()

        orders_data = [
            dict(user=jan, status="completed", notes="Proszę o jasny motyw kolorystyczny.",
                 items=[(wizytowka, 1), (logo, 1)]),
            dict(user=jan, status="in_progress", notes="",
                 items=[(kampania, 3)]),
            dict(user=anna, status="pending", notes="Termin: koniec miesiąca.",
                 items=[(identyfikacja, 1)]),
        ]

        count = 0
        for data in orders_data:
            items = data.pop("items")
            order = Order.objects.create(**data)
            for product, qty in items:
                if product:
                    OrderItem.objects.create(
                        order=order, product=product,
                        quantity=qty, unit_price=product.price,
                    )
            order.recalculate_total()
            count += 1
        self.stdout.write(f"  Zamowienia: {count}")

    def _create_contact_messages(self):
        from contact.models import ContactMessage

        messages = [
            dict(name="Piotr Zielinski", email="piotr@firma.pl",
                 subject="Zapytanie o strone WWW",
                 message="Dzien dobry, jestem zainteresowany wykonaniem strony dla mojej firmy budowlanej. "
                         "Prosze o kontakt i wycene.",
                 is_read=True),
            dict(name="Katarzyna Wisniewska", email="kasia@startup.io",
                 subject="Identyfikacja wizualna dla startupu",
                 message="Hej, tworzymy nowy startup fintech i potrzebujemy pelnej identyfikacji wizualnej. "
                         "Kiedy mozemy porozmawiac?",
                 is_read=False),
            dict(name="Marek Lewandowski", email="marek@ecom.pl",
                 subject="Sklep internetowy — pytanie o integracje",
                 message="Czy realizujecie integracje z Allegro i BaseLinker? "
                         "Potrzebujemy sklepu z wielokanałową sprzedazą.",
                 is_read=False),
        ]

        for data in messages:
            ContactMessage.objects.get_or_create(
                email=data["email"], subject=data["subject"], defaults=data
            )
        self.stdout.write(f"  Wiadomosci: {len(messages)}")

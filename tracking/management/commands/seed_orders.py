from datetime import date, timedelta
from django.core.management.base import BaseCommand
from tracking.models import Order


class Command(BaseCommand):
    help = "Seeds the database with realistic sample Commercial Kitchen Equipment orders."

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample commercial kitchen equipment orders...")

        sample_orders = [
            {
                'order_id': '#101',
                'customer_name': 'Grand Plaza Hotel & Suites',
                'equipment_model': 'Commercial 4-Burner Gas Range with Heavy Convection Oven',
                'assigned_staff': 'David Chen (Lead Welder)',
                'delivery_date': date.today() + timedelta(days=4),
                'status': Order.STATUS_ON_TRACK,
                'notes': 'Spec: 16-gauge 304 Stainless Steel exterior, 30,000 BTU cast iron burners, thermocouple safety cutoff.',
                'stage_cutting': Order.STAGE_COMPLETED,
                'stage_welding': Order.STAGE_COMPLETED,
                'stage_glass': Order.STAGE_COMPLETED,
                'stage_finishing': Order.STAGE_IN_PROGRESS,
                'stage_qc': Order.STAGE_PENDING,
            },
            {
                'order_id': '#102',
                'customer_name': 'Spice Symphony Catering Co.',
                'equipment_model': '6-Pan Wet/Dry Bain Marie with Sneeze Guard',
                'assigned_staff': 'Alex Rivera (Fabrication)',
                'delivery_date': date.today() + timedelta(days=2),
                'status': Order.STATUS_URGENT,
                'notes': 'Urgent banqueting order! 8mm tempered curved glass sneeze guard, digital thermostatic heat controllers.',
                'stage_cutting': Order.STAGE_COMPLETED,
                'stage_welding': Order.STAGE_COMPLETED,
                'stage_glass': Order.STAGE_IN_PROGRESS,
                'stage_finishing': Order.STAGE_PENDING,
                'stage_qc': Order.STAGE_PENDING,
            },
            {
                'order_id': '#103',
                'customer_name': 'Bella Napoli Wood & Gas Pizzeria',
                'equipment_model': 'Dual-Deck Stone Hearth Pizza Oven',
                'assigned_staff': 'Marcus Thorne (Senior Assembler)',
                'delivery_date': date.today() + timedelta(days=8),
                'status': Order.STATUS_ON_TRACK,
                'notes': 'Cordierite refractory stone baking decks, heat resistant double-glazed inspection glass, dual chamber analog pyrometers.',
                'stage_cutting': Order.STAGE_COMPLETED,
                'stage_welding': Order.STAGE_IN_PROGRESS,
                'stage_glass': Order.STAGE_PENDING,
                'stage_finishing': Order.STAGE_PENDING,
                'stage_qc': Order.STAGE_PENDING,
            },
            {
                'order_id': '#104',
                'customer_name': 'Skyline Rooftop Lounge',
                'equipment_model': '10ft Stainless Steel Island Exhaust Hood with Baffle Filters',
                'assigned_staff': 'Elena Rostova (Sheet Metal)',
                'delivery_date': date.today() - timedelta(days=1),
                'status': Order.STATUS_DELAYED,
                'notes': 'Delayed awaiting delivery of custom centrifugal high-temp exhaust blower. SS 304 seamless welded grease troughs.',
                'stage_cutting': Order.STAGE_COMPLETED,
                'stage_welding': Order.STAGE_IN_PROGRESS,
                'stage_glass': Order.STAGE_COMPLETED,
                'stage_finishing': Order.STAGE_PENDING,
                'stage_qc': Order.STAGE_PENDING,
            },
            {
                'order_id': '#105',
                'customer_name': 'Metro Central Hospital Canteen',
                'equipment_model': 'Prep Island Worktable with Double Sink & Overhead Gantry',
                'assigned_staff': 'Robert Vance (Finishing)',
                'delivery_date': date.today() - timedelta(days=3),
                'status': Order.STATUS_COMPLETED,
                'notes': 'Sanitary food grade finish, welded anti-drip rolled marine edges, sound deadening underlayment.',
                'stage_cutting': Order.STAGE_COMPLETED,
                'stage_welding': Order.STAGE_COMPLETED,
                'stage_glass': Order.STAGE_COMPLETED,
                'stage_finishing': Order.STAGE_COMPLETED,
                'stage_qc': Order.STAGE_COMPLETED,
            },
            {
                'order_id': '#106',
                'customer_name': 'Artisan Bakeries Group',
                'equipment_model': 'Walk-In Proofing & Retarder Cabinet',
                'assigned_staff': 'Kavita Patel (QC & Electrical)',
                'delivery_date': date.today() + timedelta(days=12),
                'status': Order.STATUS_ON_TRACK,
                'notes': 'Polyurethane high-density foam injection panels, heated glass door frames to prevent misting, micro-mist humidity generator.',
                'stage_cutting': Order.STAGE_PENDING,
                'stage_welding': Order.STAGE_PENDING,
                'stage_glass': Order.STAGE_PENDING,
                'stage_finishing': Order.STAGE_PENDING,
                'stage_qc': Order.STAGE_PENDING,
            },
        ]

        count = 0
        for data in sample_orders:
            order, created = Order.objects.update_or_create(
                order_id=data['order_id'],
                defaults=data
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} sample production orders!"))

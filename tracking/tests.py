from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from .models import Order


class OrderTrackTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.order1 = Order.objects.create(
            order_id='#101',
            customer_name='Grand Plaza Hotel',
            equipment_model='4-Burner Gas Range with Oven',
            assigned_staff='David Chen',
            delivery_date=date.today() + timedelta(days=5),
            status=Order.STATUS_ON_TRACK,
            stage_cutting=Order.STAGE_COMPLETED,
            stage_welding=Order.STAGE_COMPLETED,
            stage_glass=Order.STAGE_PENDING,
            stage_finishing=Order.STAGE_PENDING,
            stage_qc=Order.STAGE_PENDING,
        )

    def test_progress_calculation(self):
        """Test progress calculation: 2 stages completed = 40%"""
        self.assertEqual(self.order1.progress_percentage, 40)

        # Update one more stage to IN_PROGRESS (+10%)
        self.order1.stage_glass = Order.STAGE_IN_PROGRESS
        self.order1.save()
        self.assertEqual(self.order1.progress_percentage, 50)

        # Complete all 5 stages => 100% and auto-set status to COMPLETED
        self.order1.stage_glass = Order.STAGE_COMPLETED
        self.order1.stage_finishing = Order.STAGE_COMPLETED
        self.order1.stage_qc = Order.STAGE_COMPLETED
        self.order1.save()
        self.assertEqual(self.order1.progress_percentage, 100)
        self.assertEqual(self.order1.status, Order.STATUS_COMPLETED)

    def test_dashboard_view(self):
        """Dashboard renders with summary metrics and orders"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '#101')
        self.assertContains(response, 'Grand Plaza Hotel')
        self.assertContains(response, 'Total Orders')

    def test_search_and_filter(self):
        """Search by customer name or model"""
        response = self.client.get(reverse('dashboard'), {'q': 'Grand Plaza'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '#101')

        response = self.client.get(reverse('dashboard'), {'q': 'NonExistentModel'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Grand Plaza Hotel')

    def test_create_order(self):
        """Test creating a new order via POST"""
        data = {
            'order_id': '#102',
            'customer_name': 'Spice Villa Cafe',
            'equipment_model': '6-Pan Bain Marie',
            'assigned_staff': 'Alex Rivera',
            'delivery_date': (date.today() + timedelta(days=7)).isoformat(),
            'status': Order.STATUS_URGENT,
            'notes': 'Toughened glass sneeze guard',
            'stage_cutting': Order.STAGE_PENDING,
            'stage_welding': Order.STAGE_PENDING,
            'stage_glass': Order.STAGE_PENDING,
            'stage_finishing': Order.STAGE_PENDING,
            'stage_qc': Order.STAGE_PENDING,
        }
        response = self.client.post(reverse('order_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Order.objects.filter(order_id='#102').exists())

    def test_quick_stage_update_ajax(self):
        """Test cycling stage status via AJAX endpoint"""
        url = reverse('quick_stage_update', args=[self.order1.id])
        # Cutting is currently COMPLETED -> cycling will set it to PENDING
        response = self.client.post(url, {'stage': 'cutting'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['new_status'], Order.STAGE_PENDING)

        # Welding is COMPLETED (20%), others PENDING (0%) -> total progress = 20%
        self.assertEqual(data['progress'], 20)

    def test_delete_order(self):
        """Test deleting an order"""
        url = reverse('order_delete', args=[self.order1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Order.objects.filter(id=self.order1.id).exists())

    def test_pwa_endpoints(self):
        """Test that PWA manifest and service worker are served at root scope"""
        res_sw = self.client.get('/sw.js')
        self.assertEqual(res_sw.status_code, 200)
        self.assertEqual(res_sw['Content-Type'], 'application/javascript')
        self.assertEqual(res_sw['Service-Worker-Allowed'], '/')

        res_manifest = self.client.get('/manifest.json')
        self.assertEqual(res_manifest.status_code, 200)
        self.assertIn('application/manifest+json', res_manifest['Content-Type'])
        self.assertIn('OrderTrack Pro', res_manifest.content.decode())


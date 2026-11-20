import json
import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.contrib import messages
from django.db.models import Q
from .models import Order
from .forms import OrderForm


def dashboard(request):
    """
    Main workshop floor dashboard.
    Displays summary KPI cards, search/filter bar, and orders in Table or Card view.
    """
    # Base queryset
    orders = Order.objects.all()

    # --- Summary Metrics ---
    total_orders = orders.count()
    active_orders = orders.exclude(status=Order.STATUS_COMPLETED).count()
    on_track_orders = orders.filter(status=Order.STATUS_ON_TRACK).count()
    urgent_orders = orders.filter(status=Order.STATUS_URGENT).count()
    completed_orders = orders.filter(status=Order.STATUS_COMPLETED).count()
    delayed_orders = orders.filter(status=Order.STATUS_DELAYED).count()

    summary_stats = {
        'total': total_orders,
        'active': active_orders,
        'on_track': on_track_orders,
        'urgent': urgent_orders,
        'completed': completed_orders,
        'delayed': delayed_orders,
    }

    # --- Search Filter ---
    search_query = request.GET.get('q', '').strip()
    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(customer_name__icontains=search_query) |
            Q(equipment_model__icontains=search_query) |
            Q(assigned_staff__icontains=search_query)
        )

    # --- Status Filter ---
    status_filter = request.GET.get('status', 'all').strip()
    if status_filter == 'active':
        orders = orders.exclude(status=Order.STATUS_COMPLETED)
    elif status_filter in [Order.STATUS_ON_TRACK, Order.STATUS_URGENT, Order.STATUS_DELAYED, Order.STATUS_COMPLETED]:
        orders = orders.filter(status=status_filter)
    else:
        status_filter = 'all'

    # --- View Preference (Table vs Card) ---
    view_mode = request.GET.get('view', 'table').strip().lower()
    if view_mode not in ['table', 'card']:
        view_mode = 'table'

    context = {
        'orders': orders,
        'summary': summary_stats,
        'search_query': search_query,
        'current_status': status_filter,
        'view_mode': view_mode,
    }
    return render(request, 'tracking/dashboard.html', context)


def order_detail(request, pk):
    """
    Detailed view for a single production order.
    Shows complete timeline of the 5 manufacturing stages, specifications, and notes.
    """
    order = get_object_or_404(Order, pk=pk)
    context = {
        'order': order,
        'stages': order.get_stages_info(),
    }
    return render(request, 'tracking/order_detail.html', context)


def order_create(request):
    """
    Create a new production order.
    """
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, f"Order {order.order_id} created successfully!")
            return redirect('dashboard')
    else:
        form = OrderForm()

    return render(request, 'tracking/order_form.html', {
        'form': form,
        'action_title': 'Add New Production Order',
        'is_create': True,
    })


def order_update(request, pk):
    """
    Edit an existing production order.
    """
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            messages.success(request, f"Order {order.order_id} updated successfully!")
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)

    return render(request, 'tracking/order_form.html', {
        'form': form,
        'order': order,
        'action_title': f"Edit Order {order.order_id}",
        'is_create': False,
    })


def order_delete(request, pk):
    """
    Delete a production order with user confirmation.
    """
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order_id = order.order_id
        order.delete()
        messages.warning(request, f"Order {order_id} has been deleted.")
        return redirect('dashboard')

    return render(request, 'tracking/order_confirm_delete.html', {'order': order})


def quick_stage_update(request, pk):
    """
    API & Form action endpoint to update an order's production stage.
    Supports single-click cycle: Pending -> In Progress -> Completed -> Pending.
    Also accepts explicit target status.
    Returns JSON for AJAX requests or redirects back for normal form submissions.
    """
    if request.method != 'POST':
        return HttpResponseBadRequest("POST request required.")

    order = get_object_or_404(Order, pk=pk)
    
    # Read stage and target status from POST body or form-data
    stage_key = request.POST.get('stage')
    target_status = request.POST.get('target_status')

    # If incoming JSON payload
    if not stage_key and request.body:
        try:
            data = json.loads(request.body.decode('utf-8'))
            stage_key = data.get('stage')
            target_status = data.get('target_status')
        except Exception:
            pass

    stage_field_map = {
        'cutting': 'stage_cutting',
        'welding': 'stage_welding',
        'glass': 'stage_glass',
        'finishing': 'stage_finishing',
        'qc': 'stage_qc',
    }

    if stage_key not in stage_field_map:
        return JsonResponse({'success': False, 'error': f"Invalid stage: {stage_key}"}, status=400)

    field_name = stage_field_map[stage_key]
    current_status = getattr(order, field_name)

    # Determine new status
    valid_statuses = [Order.STAGE_PENDING, Order.STAGE_IN_PROGRESS, Order.STAGE_COMPLETED]
    if target_status and target_status in valid_statuses:
        new_status = target_status
    else:
        # Cycle through: Pending -> In Progress -> Completed -> Pending
        if current_status == Order.STAGE_PENDING:
            new_status = Order.STAGE_IN_PROGRESS
        elif current_status == Order.STAGE_IN_PROGRESS:
            new_status = Order.STAGE_COMPLETED
        else:
            new_status = Order.STAGE_PENDING

    # Update and save (save() auto-recalculates progress_percentage)
    setattr(order, field_name, new_status)
    order.save()

    status_labels = dict(Order.STAGE_STATUS_CHOICES)
    new_label = status_labels.get(new_status, new_status)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json' or request.content_type == 'application/json'

    if is_ajax:
        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'stage': stage_key,
            'new_status': new_status,
            'new_label': new_label,
            'progress': order.progress_percentage,
            'order_status': order.status,
            'order_status_label': order.get_status_display(),
            'stages': order.get_stages_info(),
        })

    messages.info(request, f"Updated {order.order_id} - {stage_key.capitalize()} to {new_label}.")
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('dashboard')
    return redirect(next_url)


def service_worker(request):
    """
    Serves the Service Worker file at the root URL /sw.js.
    This gives the service worker root scope '/' for PWA compliance.
    """
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'sw.js')
    with open(sw_path, 'r', encoding='utf-8') as f:
        content = f.read()
    response = HttpResponse(content, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    return response


def manifest_view(request):
    """
    Serves the PWA Web App Manifest at /manifest.json.
    """
    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/manifest+json')


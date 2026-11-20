from django.db import models
from django.utils import timezone
from datetime import date


class Order(models.Model):
    """
    Model representing a Commercial Kitchen Equipment Production Order.
    Tracks customer requirements, assigned personnel, deadlines, and
    the 5 workshop manufacturing stages from cutting to final QC.
    """

    # Overall Order Status Choices
    STATUS_ON_TRACK = 'ON_TRACK'
    STATUS_URGENT = 'URGENT'
    STATUS_DELAYED = 'DELAYED'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (STATUS_ON_TRACK, 'On Track'),
        (STATUS_URGENT, 'Urgent'),
        (STATUS_DELAYED, 'Delayed'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    # Production Stage Status Choices
    STAGE_PENDING = 'PENDING'
    STAGE_IN_PROGRESS = 'IN_PROGRESS'
    STAGE_COMPLETED = 'COMPLETED'

    STAGE_STATUS_CHOICES = [
        (STAGE_PENDING, 'Pending'),
        (STAGE_IN_PROGRESS, 'In Progress'),
        (STAGE_COMPLETED, 'Completed'),
    ]

    # --- Core Order Information ---
    order_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Order ID",
        help_text="Unique identifier (e.g., #101, ORD-2026-05)"
    )
    customer_name = models.CharField(
        max_length=150,
        verbose_name="Customer Name",
        help_text="Restaurant, hotel, or catering client name"
    )
    equipment_model = models.CharField(
        max_length=200,
        verbose_name="Equipment Model",
        help_text="e.g., 4-Burner Gas Range with Oven, Stainless Steel Worktable, Bain Marie"
    )
    assigned_staff = models.CharField(
        max_length=120,
        verbose_name="Assigned Staff / Lead",
        help_text="Name of workshop technician or production supervisor"
    )
    delivery_date = models.DateField(
        verbose_name="Delivery Due Date"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ON_TRACK,
        verbose_name="Order Status"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Technical Notes / Specifications",
        help_text="Metal gauge (e.g., SS 304, 18-gauge), dimensions, custom burners, or glass specs"
    )

    # --- 5 Production Stages ---
    stage_cutting = models.CharField(
        max_length=20,
        choices=STAGE_STATUS_CHOICES,
        default=STAGE_PENDING,
        verbose_name="Stage 1: Cutting"
    )
    stage_welding = models.CharField(
        max_length=20,
        choices=STAGE_STATUS_CHOICES,
        default=STAGE_PENDING,
        verbose_name="Stage 2: Welding"
    )
    stage_glass = models.CharField(
        max_length=20,
        choices=STAGE_STATUS_CHOICES,
        default=STAGE_PENDING,
        verbose_name="Stage 3: Glass"
    )
    stage_finishing = models.CharField(
        max_length=20,
        choices=STAGE_STATUS_CHOICES,
        default=STAGE_PENDING,
        verbose_name="Stage 4: Finishing"
    )
    stage_qc = models.CharField(
        max_length=20,
        choices=STAGE_STATUS_CHOICES,
        default=STAGE_PENDING,
        verbose_name="Stage 5: QC (Quality Check)"
    )

    # Calculated progress percentage (0 - 100)
    progress_percentage = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Progress Percentage"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Production Order"
        verbose_name_plural = "Production Orders"

    def __str__(self):
        return f"{self.order_id} - {self.customer_name} ({self.equipment_model})"

    def calculate_progress(self):
        """
        Calculates production progress based on the 5 stages:
        Cutting (20%), Welding (20%), Glass (20%), Finishing (20%), QC (20%).
        - COMPLETED = 20%
        - IN_PROGRESS = 10%
        - PENDING = 0%
        """
        stages = [
            self.stage_cutting,
            self.stage_welding,
            self.stage_glass,
            self.stage_finishing,
            self.stage_qc,
        ]

        total = 0
        for st in stages:
            if st == self.STAGE_COMPLETED:
                total += 20
            elif st == self.STAGE_IN_PROGRESS:
                total += 10
            # PENDING adds 0
        return min(total, 100)

    def save(self, *args, **kwargs):
        """
        Automatically update progress_percentage prior to saving.
        If all stages are 100% completed, auto-suggest or update status to COMPLETED
        if it was still in active status.
        """
        self.progress_percentage = self.calculate_progress()
        if self.progress_percentage == 100 and self.status != self.STATUS_COMPLETED:
            self.status = self.STATUS_COMPLETED
        elif self.progress_percentage < 100 and self.status == self.STATUS_COMPLETED:
            # If an order was completed but a stage was reopened, revert from completed
            self.status = self.STATUS_ON_TRACK
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """True if the order is currently on the workshop floor (not completed)."""
        return self.status != self.STATUS_COMPLETED

    @property
    def days_remaining(self):
        """Returns the number of days until the delivery due date."""
        if not self.delivery_date:
            return 0
        delta = self.delivery_date - date.today()
        return delta.days

    @property
    def is_overdue(self):
        """True if delivery date has passed and order is not completed."""
        return self.days_remaining < 0 and self.status != self.STATUS_COMPLETED

    @property
    def status_badge_class(self):
        """CSS class for the order status badge."""
        mapping = {
            self.STATUS_ON_TRACK: 'badge-status-on-track',
            self.STATUS_URGENT: 'badge-status-urgent',
            self.STATUS_DELAYED: 'badge-status-delayed',
            self.STATUS_COMPLETED: 'badge-status-completed',
        }
        return mapping.get(self.status, 'badge-secondary')

    @property
    def progress_bar_class(self):
        """Bootstrap color class for the progress bar."""
        if self.status == self.STATUS_COMPLETED or self.progress_percentage == 100:
            return 'bg-success'
        if self.status == self.STATUS_URGENT:
            return 'bg-danger'
        if self.status == self.STATUS_DELAYED:
            return 'bg-warning'
        return 'bg-primary'

    def get_stages_info(self):
        """
        Returns structured metadata for all 5 stages for templating and JSON responses.
        """
        stage_definitions = [
            ('cutting', 'stage_cutting', 'Cutting', 'bi-scissors', 'Cutting & blanking sheet metal'),
            ('welding', 'stage_welding', 'Welding', 'bi-fire', 'TIG/MIG framing & assembly'),
            ('glass', 'stage_glass', 'Glass', 'bi-window', 'Toughened glass & display fitting'),
            ('finishing', 'stage_finishing', 'Finishing', 'bi-brush', 'Buffing, polishing & insulation'),
            ('qc', 'stage_qc', 'QC', 'bi-patch-check', 'Quality control & safety testing'),
        ]

        result = []
        for key, field_name, display_name, icon, desc in stage_definitions:
            current_val = getattr(self, field_name)
            # Cycle to next status on quick toggle: PENDING -> IN_PROGRESS -> COMPLETED -> PENDING
            next_val = (
                self.STAGE_IN_PROGRESS if current_val == self.STAGE_PENDING else
                self.STAGE_COMPLETED if current_val == self.STAGE_IN_PROGRESS else
                self.STAGE_PENDING
            )
            result.append({
                'key': key,
                'field': field_name,
                'name': display_name,
                'status': current_val,
                'status_label': dict(self.STAGE_STATUS_CHOICES).get(current_val, current_val),
                'next_status': next_val,
                'icon': icon,
                'description': desc,
                'is_completed': current_val == self.STAGE_COMPLETED,
                'is_in_progress': current_val == self.STAGE_IN_PROGRESS,
                'is_pending': current_val == self.STAGE_PENDING,
            })
        return result

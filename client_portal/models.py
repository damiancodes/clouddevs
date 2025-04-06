# from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone
# from django.urls import reverse
# from django.apps import apps
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth.models import User
#
# class Client(models.Model):
#     """
#     Client profile extending the User model
#     """
#
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
#     company_name = models.CharField(max_length=100, blank=True)
#     phone = models.CharField(max_length=20, blank=True)
#     address = models.TextField(blank=True)
#     profile_image = models.ImageField(upload_to='clients/', blank=True, null=True)
#
#     # Additional client information
#     industry = models.CharField(max_length=100, blank=True)
#     website = models.URLField(blank=True, null=True)
#     referred_by = models.CharField(max_length=100, blank=True)
#
#     # Account status
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"{self.user.get_full_name() or self.user.username} - {self.company_name}"
#
#     def get_absolute_url(self):
#         return reverse('client_portal:dashboard')
#
#     @property
#     def full_name(self):
#         return self.user.get_full_name() or self.user.username
#
#     @property
#     def active_projects_count(self):
#         return self.projects.filter(status__in=['planning', 'in_progress']).count()
#
#     @property
#     def completed_projects_count(self):
#         return self.projects.filter(status='completed').count()
#
#     @property
#     def total_due(self):
#         return sum(invoice.balance_due for invoice in self.invoices.filter(status__in=['draft', 'sent', 'overdue']))
#
#
# class Project(models.Model):
#     """
#     Client projects
#     """
#     STATUS_CHOICES = (
#         ('planning', 'Planning'),
#         ('in_progress', 'In Progress'),
#         ('on_hold', 'On Hold'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     )
#
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
#
#     start_date = models.DateField()
#     end_date = models.DateField(blank=True, null=True)
#
#     budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"{self.title} - {self.client.user.username}"
#
#     def get_absolute_url(self):
#         return reverse('client_portal:project_detail', args=[self.id])
#
#     @property
#     def completion_percentage(self):
#         completed_tasks = self.tasks.filter(is_completed=True).count()
#         total_tasks = self.tasks.count()
#
#         if total_tasks == 0:
#             return 0
#
#         return int((completed_tasks / total_tasks) * 100)
#
#     @property
#     def days_remaining(self):
#         if not self.end_date:
#             return None
#
#         delta = self.end_date - timezone.now().date()
#         return delta.days
#
#     @property
#     def is_overdue(self):
#         if not self.end_date:
#             return False
#
#         return self.end_date < timezone.now().date() and self.status != 'completed'
#
#
# class ProjectTask(models.Model):
#     """
#     Tasks for projects
#     """
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     is_completed = models.BooleanField(default=False)
#
#     due_date = models.DateField(blank=True, null=True)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['due_date', 'created_at']
#
#     def __str__(self):
#         return f"{self.title} - {self.project.title}"
#
#     @property
#     def is_overdue(self):
#         if not self.due_date:
#             return False
#
#         return self.due_date < timezone.now().date() and not self.is_completed
#
#
# class ProjectUpdate(models.Model):
#     """
#     Updates for projects
#     """
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='updates')
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f"{self.title} - {self.project.title}"
#
#
# class ProjectFile(models.Model):
#     """
#     Files associated with projects
#     """
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
#     title = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     file = models.FileField(upload_to='project_files/')
#
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         ordering = ['-uploaded_at']
#
#     def __str__(self):
#         return f"{self.title} - {self.project.title}"
#
#     @property
#     def file_extension(self):
#         return self.file.name.split('.')[-1].lower()
#
#     @property
#     def is_image(self):
#         return self.file_extension in ['jpg', 'jpeg', 'png', 'gif']
#
#     @property
#     def is_pdf(self):
#         return self.file_extension == 'pdf'
#
#     @property
#     def is_document(self):
#         return self.file_extension in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']
#
#
# class Invoice(models.Model):
#     """
#     Client invoices
#     """
#     STATUS_CHOICES = (
#         ('draft', 'Draft'),
#         ('sent', 'Sent'),
#         ('paid', 'Paid'),
#         ('overdue', 'Overdue'),
#         ('cancelled', 'Cancelled'),
#     )
#
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices', null=True)
#     project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
#
#     invoice_number = models.CharField(max_length=50, unique=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
#
#     issue_date = models.DateField()
#     due_date = models.DateField()
#
#     subtotal = models.DecimalField(max_digits=10, decimal_places=2)
#     tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
#     discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total = models.DecimalField(max_digits=10, decimal_places=2)
#
#     notes = models.TextField(blank=True)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['-issue_date', '-id']
#
#     def __str__(self):
#         return f"Invoice {self.invoice_number} - {self.client.user.username}"
#
#     def get_absolute_url(self):
#         return reverse('client_portal:invoice_detail', args=[self.id])
#
#     @property
#     def amount_paid(self):
#         return sum(payment.amount for payment in self.payments.all())
#
#     @property
#     def balance_due(self):
#         return self.total - self.amount_paid
#
#     @property
#     def is_overdue(self):
#         return self.due_date < timezone.now().date() and self.status != 'paid'
#
#     @property
#     def is_fully_paid(self):
#         return self.balance_due <= 0
#
#     @property
#     def tax_amount(self):
#         return (self.subtotal * self.tax_rate) / 100
#
#     def save(self, *args, **kwargs):
#         # Calculate total
#         tax_amount = (self.subtotal * self.tax_rate) / 100
#         self.total = self.subtotal + tax_amount - self.discount
#
#         # Update status if overdue
#         if self.due_date < timezone.now().date() and self.status not in ['paid', 'cancelled']:
#             self.status = 'overdue'
#
#         super().save(*args, **kwargs)
#
#
# class InvoiceItem(models.Model):
#     """
#     Individual items on an invoice
#     """
#     invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
#     description = models.CharField(max_length=200)
#     quantity = models.DecimalField(max_digits=10, decimal_places=2)
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return f"{self.description} - {self.invoice.invoice_number}"
#
#     def save(self, *args, **kwargs):
#         # Calculate amount
#         self.amount = self.quantity * self.unit_price
#         super().save(*args, **kwargs)
#
#
# class Payment(models.Model):
#     PAYMENT_METHOD_CHOICES = (
#         ('credit_card', 'Credit Card'),
#         ('bank_transfer', 'Bank Transfer'),
#         ('paypal', 'PayPal'),
#         ('mpesa', 'M-Pesa'),
#         ('cash', 'Cash'),
#         ('other', 'Other'),
#     )
#
#
#     invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_date = models.DateField()
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
#
#     transaction_id = models.CharField(max_length=100, blank=True)
#     notes = models.TextField(blank=True)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Payment {self.amount} for {self.invoice.invoice_number}"
#
#
# class Message(models.Model):
#     """
#     Messages between client and staff
#     """
#     client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='messages')
#     subject = models.CharField(max_length=200)
#     content = models.TextField()
#
#     is_from_client = models.BooleanField(default=True)
#     is_read = models.BooleanField(default=False)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         ordering = ['-created_at']
#
#     def __str__(self):
#         direction = "From" if self.is_from_client else "To"
#         return f"{direction} {self.client.user.username}: {self.subject}"









from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver

# Rest of your existing code remains the same

# Add these two methods at the end of the file
@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    """
    Automatically create a client profile for non-staff users
    """
    if created and not instance.is_staff:
        try:
            Client.objects.create(user=instance)
        except Exception as e:
            print(f"Error creating client profile: {e}")

def is_admin_user(user):
    """
    Helper function to check if a user is an admin
    """
    return user.is_staff or user.is_superuser

class Client(models.Model):
    """
    Client profile extending the User model
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    company_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='clients/', blank=True, null=True)

    # Additional client information
    industry = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True, null=True)
    referred_by = models.CharField(max_length=100, blank=True)

    # Account status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.company_name}"

    def get_absolute_url(self):
        return reverse('client_portal:dashboard')

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def active_projects_count(self):
        return self.projects.filter(status__in=['planning', 'in_progress']).count()

    @property
    def completed_projects_count(self):
        return self.projects.filter(status='completed').count()

    @property
    def total_due(self):
        return sum(invoice.balance_due for invoice in self.invoices.filter(status__in=['draft', 'sent', 'overdue']))


class Project(models.Model):
    """
    Client projects
    """
    STATUS_CHOICES = (
        ('planning', 'Planning'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')

    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.client.user.username}"

    def get_absolute_url(self):
        return reverse('client_portal:project_detail', args=[self.id])

    @property
    def completion_percentage(self):
        completed_tasks = self.tasks.filter(is_completed=True).count()
        total_tasks = self.tasks.count()

        if total_tasks == 0:
            return 0

        return int((completed_tasks / total_tasks) * 100)

    @property
    def days_remaining(self):
        if not self.end_date:
            return None

        delta = self.end_date - timezone.now().date()
        return delta.days

    @property
    def is_overdue(self):
        if not self.end_date:
            return False

        return self.end_date < timezone.now().date() and self.status != 'completed'


class ProjectTask(models.Model):
    """
    Tasks for projects
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    due_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'created_at']

    def __str__(self):
        return f"{self.title} - {self.project.title}"

    @property
    def is_overdue(self):
        if not self.due_date:
            return False

        return self.due_date < timezone.now().date() and not self.is_completed


class ProjectUpdate(models.Model):
    """
    Updates for projects
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=200)
    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.project.title}"


class ProjectFile(models.Model):
    """
    Files associated with projects
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='project_files/')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.project.title}"

    @property
    def file_extension(self):
        return self.file.name.split('.')[-1].lower()

    @property
    def is_image(self):
        return self.file_extension in ['jpg', 'jpeg', 'png', 'gif']

    @property
    def is_pdf(self):
        return self.file_extension == 'pdf'

    @property
    def is_document(self):
        return self.file_extension in ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']


class Invoice(models.Model):
    """
    Client invoices
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices', null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')

    invoice_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    issue_date = models.DateField()
    due_date = models.DateField()

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date', '-id']

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.client.user.username}"

    def get_absolute_url(self):
        return reverse('client_portal:invoice_detail', args=[self.id])

    @property
    def amount_paid(self):
        return sum(payment.amount for payment in self.payments.all())

    @property
    def balance_due(self):
        return self.total - self.amount_paid

    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status != 'paid'

    @property
    def is_fully_paid(self):
        return self.balance_due <= 0

    @property
    def tax_amount(self):
        return (self.subtotal * self.tax_rate) / 100

    def save(self, *args, **kwargs):
        # Calculate total
        tax_amount = (self.subtotal * self.tax_rate) / 100
        self.total = self.subtotal + tax_amount - self.discount

        # Update status if overdue
        if self.due_date < timezone.now().date() and self.status not in ['paid', 'cancelled']:
            self.status = 'overdue'

        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """
    Individual items on an invoice
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        # Calculate amount
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    )


    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)

    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.amount} for {self.invoice.invoice_number}"


class Message(models.Model):
    """
    Messages between client and staff
    """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='messages')
    subject = models.CharField(max_length=200)
    content = models.TextField()

    is_from_client = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        direction = "From" if self.is_from_client else "To"
        return f"{direction} {self.client.user.username}: {self.subject}"



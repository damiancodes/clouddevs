from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    """
    Category for projects (Web Development, App Development, POS Systems, etc.)
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Check for existing slugs and modify if needed
        if Category.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{slugify(self.name)}-{Category.objects.count()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:portfolio_category', args=[self.slug])


class Technology(models.Model):
    """
    Technologies used in projects (Python, React, Django, etc.)
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Technology"
        verbose_name_plural = "Technologies"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Check for existing slugs and modify if needed
        if Technology.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{slugify(self.name)}-{Technology.objects.count()}"
        super().save(*args, **kwargs)


class Client(models.Model):
    """
    Clients for whom projects were completed
    """
    name = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='clients/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    """
    Portfolio projects/case studies
    """
    title = models.CharField(max_length=200)
    # slug = models.SlugField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, default="default-slug")


    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='projects')
    technologies = models.ManyToManyField(Technology, related_name='projects')

    featured_image = models.ImageField(upload_to='projects/')
    image_1 = models.ImageField(upload_to='projects/', blank=True, null=True)
    image_2 = models.ImageField(upload_to='projects/', blank=True, null=True)
    image_3 = models.ImageField(upload_to='projects/', blank=True, null=True)

    short_description = models.TextField(max_length=200, blank=True, default="")
    description = models.TextField()
    challenge = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    results = models.TextField(blank=True)

    website_url = models.URLField(blank=True, null=True)
    app_store_url = models.URLField(blank=True, null=True)
    play_store_url = models.URLField(blank=True, null=True)

    completion_date = models.DateField()
    featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-completion_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        # Check for existing slugs and modify if needed
        if Project.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{slugify(self.title)}-{Project.objects.count()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:case_study', args=[self.id])

    @property
    def category_list(self) -> str:
        """Returns a comma-separated list of category names"""
        return ", ".join([category.name for category in self.categories.all()])

    @property
    def technology_list(self) -> str:
        """Returns a comma-separated list of technology names"""
        return ", ".join([tech.name for tech in self.technologies.all()])


class Testimonial(models.Model):
    """
    Client testimonials for projects
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='testimonials')
    client_name = models.CharField(max_length=100)
    client_position = models.CharField(max_length=100)
    client_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    content = models.TextField()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"Testimonial from {self.client_name} for {self.project.title}"





# from django.db import models
# from django.urls import reverse
# from django.utils.text import slugify
#
# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(max_length=100, unique=True)
#     description = models.TextField(blank=True)
#
#     class Meta:
#         verbose_name = "Category"
#         verbose_name_plural = "Categories"
#         ordering = ['name']
#
#     def __str__(self):
#         return self.name
#
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         while Category.objects.filter(slug=self.slug).exists():
#             self.slug = f"{slugify(self.name)}-{Category.objects.count()}"
#         super().save(*args, **kwargs)
#
#     def get_absolute_url(self):
#         return reverse('portfolio:portfolio_category', args=[self.slug])
#
#
# class Technology(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(max_length=100, unique=True)
#
#     class Meta:
#         verbose_name = "Technology"
#         verbose_name_plural = "Technologies"
#         ordering = ['name']
#
#     def __str__(self):
#         return self.name
#
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         while Technology.objects.filter(slug=self.slug).exists():
#             self.slug = f"{slugify(self.name)}-{Technology.objects.count()}"
#         super().save(*args, **kwargs)
#
#
# class Client(models.Model):
#     name = models.CharField(max_length=100)
#     logo = models.ImageField(upload_to='clients/', blank=True, null=True)
#     website = models.URLField(blank=True, null=True)
#     industry = models.CharField(max_length=100, blank=True)
#
#     class Meta:
#         ordering = ['name']
#
#     def __str__(self):
#         return self.name
#
#
# class Project(models.Model):
#     title = models.CharField(max_length=200)
#     slug = models.SlugField(max_length=200, unique=True)
#     client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
#     categories = models.ManyToManyField(Category, related_name='project_categories')
#     technologies = models.ManyToManyField(Technology, related_name='project_technologies')
#
#     featured_image = models.ImageField(upload_to='projects/')
#     image_1 = models.ImageField(upload_to='projects/', blank=True, null=True)
#     image_2 = models.ImageField(upload_to='projects/', blank=True, null=True)
#     image_3 = models.ImageField(upload_to='projects/', blank=True, null=True)
#
#     short_description = models.TextField(max_length=200)
#     description = models.TextField()
#     challenge = models.TextField(blank=True)
#     solution = models.TextField(blank=True)
#     results = models.TextField(blank=True)
#
#     website_url = models.URLField(blank=True, null=True)
#     app_store_url = models.URLField(blank=True, null=True)
#     play_store_url = models.URLField(blank=True, null=True)
#
#     completion_date = models.DateField()
#     featured = models.BooleanField(default=False)
#
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['-completion_date']
#
#     def __str__(self):
#         return self.title
#
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.title)
#         while Project.objects.filter(slug=self.slug).exists():
#             self.slug = f"{slugify(self.title)}-{Project.objects.count()}"
#         super().save(*args, **kwargs)
#
#     def get_absolute_url(self):
#         return reverse('portfolio:case_study', args=[self.id])
#
#     @property
#     def category_list(self):
#         return ", ".join([category.name for category in self.categories.all()])
#
#     @property
#     def technology_list(self):
#         return ", ".join([tech.name for tech in self.technologies.all()])
#
#
# class Testimonial(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='testimonials')
#     client_name = models.CharField(max_length=100)
#     client_position = models.CharField(max_length=100)
#     client_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
#     content = models.TextField()
#
#     class Meta:
#         ordering = ['-id']
#
#     def __str__(self):
#         return f"Testimonial from {self.client_name} for {self.project.title}"

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone
from django.utils.html import strip_tags


class Category(models.Model):
    """
    Blog post categories
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
        if Category.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{slugify(self.name)}-{Category.objects.count()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:blog_category', args=[self.slug])

    @property
    def post_count(self):
        return self.posts.filter(status='published').count()


class Tag(models.Model):
    """
    Blog post tags
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if Tag.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{slugify(self.name)}-{Tag.objects.count()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:blog_tag', args=[self.slug])

    @property
    def post_count(self):
        return self.posts.filter(status='published').count()


class Post(models.Model):
    """
    Blog posts
    """
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )

    content = models.TextField()
    excerpt = models.TextField(blank=True, help_text='A short description of the post (optional)')

    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug from title
        if not self.slug:
            self.slug = slugify(self.title)
        if Post.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{slugify(self.title)}-{Post.objects.count()}"

        # Set publish date when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        # Generate excerpt if not provided
        if not self.excerpt and self.content:
            # Strip HTML tags and limit to ~200 characters
            plain_text = strip_tags(self.content)
            self.excerpt = plain_text[:200] + ('...' if len(plain_text) > 200 else '')

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:blog_detail', args=[self.slug])

    @property
    def category_list(self):
        return ", ".join([category.name for category in self.categories.all()])

    @property
    def tag_list(self):
        return ", ".join([tag.name for tag in self.tags.all()])

    @property
    def reading_time(self):
        """
        Calculate approximate reading time in minutes
        Based on average reading speed of 200 words per minute
        """
        word_count = len(strip_tags(self.content).split())
        minutes = word_count / 200
        return max(1, round(minutes))


class Comment(models.Model):
    """
    Blog post comments
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    content = models.TextField()

    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"
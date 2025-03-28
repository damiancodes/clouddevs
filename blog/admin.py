from django.contrib import admin
from .models import Category, Tag, Post, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('name', 'email', 'website', 'created_at')
    fields = ('name', 'email', 'content', 'is_approved', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_at', 'is_featured', 'view_count')
    list_filter = ('status', 'author', 'is_featured', 'categories', 'published_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    filter_horizontal = ('categories', 'tags')
    readonly_fields = ('created_at', 'updated_at', 'view_count')
    inlines = [CommentInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'status', 'is_featured')
        }),
        ('Content', {
            'fields': ('content', 'excerpt', 'featured_image')
        }),
        ('Categories & Tags', {
            'fields': ('categories', 'tags')
        }),
        ('Dates & Statistics', {
            'fields': ('published_at', 'created_at', 'updated_at', 'view_count'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'email', 'content', 'post__title')
    readonly_fields = ('name', 'email', 'website', 'post', 'parent', 'created_at')
    actions = ['approve_comments', 'unapprove_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    approve_comments.short_description = "Approve selected comments"

    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)

    unapprove_comments.short_description = "Unapprove selected comments"
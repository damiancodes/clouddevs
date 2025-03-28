from django.contrib import admin
from .models import Category, Technology, Client, Project, Testimonial


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'website')
    search_fields = ('name', 'industry')


class TestimonialInline(admin.TabularInline):
    model = Testimonial
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'category_list', 'completion_date', 'featured')
    list_filter = ('categories', 'technologies', 'featured', 'completion_date')
    search_fields = ('title', 'short_description', 'description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'completion_date'
    filter_horizontal = ('categories', 'technologies')
    inlines = [TestimonialInline]

    def category_list(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])

    category_list.short_description = 'Categories'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_position', 'project')
    list_filter = ('project',)
    search_fields = ('client_name', 'content')
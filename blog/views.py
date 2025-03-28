from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Count
from django.contrib import messages
from django.utils.text import slugify

from .models import Post, Category, Tag, Comment
from .forms import CommentForm, SearchForm


class BlogListView(ListView):
    model = Post
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        queryset = Post.objects.filter(status='published')

        # Search filtering
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                title__icontains=search_query
            ) | queryset.filter(
                content__icontains=search_query
            ) | queryset.filter(
                excerpt__icontains=search_query
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['recent_posts'] = Post.objects.filter(status='published').order_by('-published_at')[:5]
        context['popular_posts'] = Post.objects.filter(status='published').order_by('-view_count')[:5]
        context['featured_posts'] = Post.objects.filter(status='published', is_featured=True)[:3]
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
        context['search_form'] = SearchForm(self.request.GET)
        context['active_page'] = 'blog'
        return context


class BlogCategoryView(ListView):
    model = Post
    template_name = 'blog/blog_category.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(categories=self.category, status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        context['recent_posts'] = Post.objects.filter(status='published').order_by('-published_at')[:5]
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
        context['search_form'] = SearchForm()
        context['active_page'] = 'blog'
        return context


class BlogTagView(ListView):
    model = Post
    template_name = 'blog/blog_tag.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.objects.filter(tags=self.tag, status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['categories'] = Category.objects.all()
        context['recent_posts'] = Post.objects.filter(status='published').order_by('-published_at')[:5]
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
        context['search_form'] = SearchForm()
        context['active_page'] = 'blog'
        return context


class BlogDetailView(DetailView):
    model = Post
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Increment view count
        post = self.object
        post.view_count += 1
        post.save()

        # Related posts - same category
        category_ids = post.categories.values_list('id', flat=True)
        related_posts = Post.objects.filter(
            categories__id__in=category_ids,
            status='published'
        ).exclude(id=post.id).distinct()[:3]

        # Comments
        comments = post.comments.filter(parent=None, is_approved=True)

        context['related_posts'] = related_posts
        context['comments'] = comments
        context['comment_form'] = CommentForm()
        context['comment_count'] = post.comments.filter(is_approved=True).count()
        context['categories'] = Category.objects.all()
        context['recent_posts'] = Post.objects.filter(status='published').order_by('-published_at')[:5]
        context['tags'] = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
        context['search_form'] = SearchForm()
        context['active_page'] = 'blog'
        return context


def add_comment(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            # Create new comment object but don't save yet
            comment = form.save(commit=False)
            comment.post = post

            # Check if it's a reply to another comment
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent

            # Save comment
            comment.save()

            messages.success(request, 'Your comment has been submitted and is awaiting approval.')
        else:
            messages.error(request, 'There was an error with your comment. Please check the form.')

    return redirect(post.get_absolute_url())


def search_blog(request):
    form = SearchForm(request.GET)
    results = []

    if form.is_valid() and form.cleaned_data.get('query'):
        query = form.cleaned_data['query']
        results = Post.objects.filter(
            status='published'
        ).filter(
            title__icontains=query
        ) | Post.objects.filter(
            status='published'
        ).filter(
            content__icontains=query
        )

    context = {
        'form': form,
        'results': results,
        'categories': Category.objects.all(),
        'recent_posts': Post.objects.filter(status='published').order_by('-published_at')[:5],
        'tags': Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20],
        'active_page': 'blog'
    }

    return render(request, 'blog/blog_search.html', context)
from django.shortcuts import render, get_object_or_404
from .models import Project, Category


def portfolio_list(request):
    """
    Display all projects in the portfolio
    """
    projects = Project.objects.all()
    categories = Category.objects.all()

    context = {
        'projects': projects,
        'categories': categories,
        'active_page': 'portfolio'
    }

    return render(request, 'portfolio/portfolio.html', context)


def portfolio_category(request, category):
    """
    Display projects filtered by category
    """
    category_obj = get_object_or_404(Category, slug=category)
    projects = Project.objects.filter(categories=category_obj)
    categories = Category.objects.all()

    context = {
        'projects': projects,
        'categories': categories,
        'current_category': category_obj,
        'active_page': 'portfolio'
    }

    return render(request, 'portfolio/portfolio.html', context)


def case_study_detail(request, case_study_id):
    """
    Display detailed information about a specific project
    """
    project = get_object_or_404(Project, id=case_study_id)

    # Get related projects (excluding current project)
    related_projects = Project.objects.filter(
        categories__in=project.categories.all()
    ).exclude(id=project.id).distinct()[:3]

    context = {
        'project': project,
        'related_projects': related_projects,
        'active_page': 'portfolio'
    }

    return render(request, 'portfolio/case_study_detail.html', context)
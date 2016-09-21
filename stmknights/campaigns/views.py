from django.shortcuts import get_object_or_404, redirect, render
from .models import Campaign, Registrant
from .forms import PostForm


def registrant_list(request):
    registrants = Registrant.objects.all()
    return render(request, 'campaigns/registrant_list.html', {'registrants': registrants})


def registrant_detail(request, pk):
    registrant = get_object_or_404(Registrant, pk=pk)
    return render(request, 'campaigns/registrant_detail.html', {'registrant': registrant})


def registrant_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            registrant = form.save(commit=False)
            registrant.name = request.POST['name']
            registrant.email = request.POST['email']
            registrant.campaign = Campaign.objects.get(pk=request.POST['campaign'])
            registrant.save()
            return redirect('registrant_detail', pk=registrant.pk)
    else:
        form = PostForm()
    return render(request, 'campaigns/registrant_edit.html', {'form': form})

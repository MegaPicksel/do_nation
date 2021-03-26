from django.shortcuts import render

from .models import Pledge


def home_view(request):
    """Home page view.

    :param request: The ``GET`` request object.
    :ptype request: class:`django.core.handlers.wsgi.WSGIRequest`.

    :return: HttpResponse object.
    :rtype: class:`django.http.response.HttpResponse`.
    """
    pledges = Pledge.objects.all()

    total_co2_savings = 0
    total_water_savings = 0
    total_waste_savings = 0

    for pledge in pledges:
        total_co2_savings += pledge.co2_saving if pledge.co2_saving else 0
        total_water_savings += pledge.water_saving if pledge.water_saving else 0
        total_waste_savings += pledge.waste_saving if pledge.waste_saving else 0

    context = {
        "amount_of_pledges": len(pledges),
        "total_co2_savings": round(total_co2_savings, 3),
        "total_water_savings": round(total_water_savings, 3),
        "total_waste_savings": round(total_waste_savings, 3),
    }

    return render(request, "home_page.html", context=context)


def search_view(request):
    """Search for specific users.

    :param request: The ``GET`` request object.
    :ptype request: class:`django.core.handlers.wsgi.WSGIRequest`.

    :return: HttpResponse object.
    :rtype: class:`django.http.response.HttpResponse`.
    """
    user = request.GET.get("user")
    pledges = Pledge.objects.filter(user__username=user)

    user_pledges = []

    for pledge in pledges:
        user_data = {
            "username": pledge.user.username,
            "action": pledge.action.action,
            "co2_saving": pledge.co2_saving if pledge.co2_saving else 0,
            "water_saving": pledge.water_saving if pledge.water_saving else 0,
            "waste_saving": pledge.waste_saving if pledge.waste_saving else 0,
        }
        user_pledges.append(user_data)

    return render(request, "search_results.html", context={"pledges": user_pledges})

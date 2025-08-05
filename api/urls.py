from django.urls import path
from . import views

urlpatterns=[
    path('trip',views.TripView.as_view(),name='trip'),
    path('trip-details/<str:id>',views.TripDetailView.as_view(), name='trip-detail'),
    path('category',views.CategoryView.as_view(), name='category'),
    path('category-details/<str:id>',views.CategoryDetailView.as_view(), name='categroy-detail'),
    path('expense',views.ExpenseView.as_view(), name='expenses'),
    path('expense-detail/<str:id>', views.ExpenseDetailView.as_view(), name='expense-details'),
    path('user-balance',views.UserBalance.as_view(), name='user-balance'),
    path('expense-pie-chart',views.CurrentTripMonthlyExpenseView.as_view(), name='expense-pie-chart'),
    path('bill-receipt/<str:id>',views.BillReceiptView.as_view(), name='bill-receipts'),
    path('previous-trips',views.PreviousTripsView.as_view(), name='previous-trips'),
    path('finshed-trip',views.FinishedTrip.as_view(), name = 'finshed-trip'),
    path('trip-summary', views.PreviousTripsSummaryView.as_view(), name='trip-summary'),
    path('expense-pie-chart-view',views.PreviousTripMonthlyExpenseView.as_view(), name='expense-pie-chart-view'),
    path('previous-trips-invoice',views.PreviousTripsInvoicepdf.as_view(), name='previous-trips-invoice')
]
from django.shortcuts import render
from . import serializers,models,validators
from core.response import Response
from core import general, messages
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from core.exceptions import SerializerError
from authentication.models import CURRENCY_SYMBOLS
from django.db.models.functions import Coalesce
from django.db.models import Value,Sum,DecimalField
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from authentication.models import CURRENCY_SYMBOLS
from collections import defaultdict
from django.db.models.functions import TruncMonth
from datetime import datetime
from decimal import Decimal
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
import tempfile

class TripView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'success': 1,
            'message': messages.DATA_FOUND,
            'data': {},
            'total_expense': 0.0  # Add this line for explicit total expense
        }

        try:
            user = request.user

            # Only fetch active and unfinished trip
            trip_obj = models.Trip.objects.filter(
                is_active=True,
                is_finished=False,
                user=user
            ).first()

            if not trip_obj:
                raise Exception('No active and ongoing trips found.')

            # Calculate total expense for the current trip
            total_expense = models.Expense.objects.filter(
                user=user,
                trip=trip_obj,
                is_active=True
            ).aggregate(
                total=Coalesce(Sum('expense'), Value(0, output_field=DecimalField()))
            )['total']

            context['total_expense'] = float(total_expense)  # Set total_expense separately

            serializer = serializers.TripSerializer(trip_obj, context={'request': request})
            context['data'] = serializer.data

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)

# class TripView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         context = {
#             'success': 1,
#             'message': messages.DATA_FOUND,
#             'data': {}
#         }
#         try:
#             user = request.user

#             # Only fetch active and unfinished trip
#             trip_obj = models.Trip.objects.filter(
#                 is_active=True,
#                 is_finished=False,
#                 user=user
#             ).first()

#             if not trip_obj:
#                 raise Exception('No active and ongoing trips found.')
            
            

#             serializer = serializers.TripSerializer(trip_obj, context={'request': request})
#             context['data'] = serializer.data

#         except Exception as e:
#             context['success'] = 0
#             context['message'] = str(e)

#         return Response(context)

    
    def post(self, request):
        context={
            'success':1,
            'message':messages.DATA_SAVED,
            'data':{}
        }
        try:
            user=request.user
            validator=validators.TripValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data=validator.validated_data
            validated_data['user']=user
            trip_obj=models.Trip.objects.create(**validated_data)
            if not trip_obj:
                raise Exception('No trip record found')
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return Response(context)

class TripDetailView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]

    def put(self, request,id):
        context={
            'success':1,
            'message':messages.DATA_UPDATED,
            'data':{}
        }
        try:
            user=request.user
            trip_obj= models.Trip.objects.get(id=id,user=user,is_active=True)
            if not trip_obj:
                raise Exception('No trip found for these user')
            validator=validators.TripValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data=validator.validated_data

            for key,value in validated_data.items():
                setattr(trip_obj, key, value)
            trip_obj.save()
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return Response(context)
    
    def delete(self, request, id):
        context = {
            'success': 1,
            'message': messages.DATA_DELETED,
            'data': {}
        }
        try:
            user=request.user
            trip_obj=models.Trip.objects.get(id=id,user=user,is_active=True)
            if not trip_obj:
                raise Exception('No trip found')
            trip_obj.delete()
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return Response(context)
    
    def get(self, request, id):
        context={
            'success':1,
            'message':messages.DATA_FOUND,
            'data':{}
        }
        try:
            user=request.user
            trip_obj= models.Trip.objects.get(id=id, user=user, is_active=True)
            if not trip_obj:
                raise Exception('No trip found')
            serializer=serializers.TripSerializer(trip_obj)
            context['data']=serializer.data
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return Response(context)
    
class CategoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'success': 1,
            'message': messages.DATA_FOUND,
            'data': {}
        }
        try:
            user = request.user

            # ✅ Fetch categories (user-specific and default) ordered alphabetically
            category_obj = models.Category.objects.filter(
                Q(user=user) | Q(user=None),
                is_active=True
            ).order_by('category_name').distinct()

            if not category_obj.exists():
                raise Exception('No category found')

            serializer = serializers.CategorySerializer(category_obj, many=True)
            context['data'] = serializer.data

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)

    
    def post(self, request):       
        context={
            'success':1,
            'message':messages.DATA_SAVED,
            'data':{}
        }
        try:
            user=request.user
            validator =validators.CategoryValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data=validator.validated_data
            validated_data['user']=user
            category_obj= models.Category.objects.create(**validated_data)
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return Response(context)
    
class CategoryDetailView(APIView)        :
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]

    def put(self, request, id):
        context={
            'success':1,
            'message':messages.DATA_UPDATED,
            'data':{}
        }
        try:
            user=request.user
            category_obj=models.Category.objects.get(id=id, user=user, is_active=True)
            if not category_obj:
                raise Exception('No categroy found')
            validator= validators.CategoryValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data=validator.validated_data
            
            for key,value in validated_data.items():
                setattr(category_obj, key, value)
            category_obj.save()
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return Response(context)
    
    def delete(self, request, id):
        context={
            'success':1,
            'message':messages.DATA_DELETED,
            'data':{}
        }
        try:
            user=request.user
            categroy_obj=models.Category.objects.get(id=id, user=user, is_active=True)
            if not categroy_obj:
                raise Exception('No category found')
            categroy_obj.delete()
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return Response(context)
    
    def get(self, request,id):
        context={
            'success':1,
            'message':messages.DATA_FOUND,
            'data':{}
        }
        try:
            user=request.user
            category_obj= models.Category.objects.get(user=user, id=id, is_active=True)
            if not category_obj:
                raise Exception('No category found')
            serializer=serializers.CategorySerializer(category_obj)
            context['data']=serializer.data
        except Exception as e:
            context['success']=0
            context['message']=str(e)   
        return Response(context)
    
class ExpenseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'success': 1,
            'message': messages.DATA_FOUND,
            'data': {}
        }

        try:
            user = request.user

            # Fetch all active expenses for the user
            expense_obj = models.Expense.objects.filter(user=user, is_active=True)

            if not expense_obj.exists():
                raise Exception("No expenses found.")

            serializer = serializers.ExpenseSerializer(expense_obj, many=True, context={'request': request})
            expense_data = serializer.data

            for item in expense_data:
                item['currency'] = CURRENCY_SYMBOLS[user.currency]

            context['data'] = expense_data

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)
    
    def post(self, request):
        context = {
            'success': 1,
            'message': messages.DATA_SAVED,
            'data': {}
        }

        try:
            user = request.user

            total_budget = models.Trip.objects.filter(user=user).aggregate(
                total=Coalesce(Sum('budget'), Value(0, output_field=DecimalField()))
            )['total']

            total_expense = models.Expense.objects.filter(user=user).aggregate(
                total=Coalesce(Sum('expense'), Value(0, output_field=DecimalField()))
            )['total']

            validator = validators.ExpenseValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data = validator.validated_data

            trip_id = validated_data.get('trip')
            trip_obj = models.Trip.objects.filter(id=trip_id, user=user, is_active=True).first()
            if not trip_obj:
                raise Exception('Invalid trip or trip does not belong to user')

            category_id = validated_data.get('category')
            category_obj = models.Category.objects.filter(id=category_id, is_active=True).first()
            if not category_obj:
                raise Exception('Invalid or inactive category')

            # ✅ Date validation: Ensure expense date is not before trip start date
            # expense_date = validated_data.get('date')
            # if expense_date and expense_date < trip_obj.start_date:
            #     raise Exception("Expense date cannot be before the trip's start date.")

            trip_expense_total = models.Expense.objects.filter(trip=trip_obj, is_active=True).aggregate(
                total=Coalesce(Sum('expense'), Value(0, output_field=DecimalField())))['total']

            trip_remaining_budget = round(trip_obj.budget - trip_expense_total, 2)

            expense_amount = validated_data.get('expense')

            # ✅ Optional: Add a warning instead of blocking
            if expense_amount > trip_remaining_budget:
                context['warning'] = (
                    f"Expense exceeds remaining trip budget. Remaining budget: {round(trip_remaining_budget, 2)}, "
                    f"entered amount: {expense_amount}"
                )

            validated_data['user'] = user
            validated_data['trip'] = trip_obj
            validated_data['category'] = category_obj

            expense_obj = models.Expense.objects.create(**validated_data)

            context['data'] = {
                'id': expense_obj.id,
                'expense': expense_obj.expense,
                'trip': str(expense_obj.trip.id),
                'category': str(expense_obj.category.id),
                'created_at': expense_obj.created_at
            }

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)


class ExpenseDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        context = {
            'success': 1,
            'message': messages.DATA_UPDATED,
            'data': {}
        }

        try:
            user = request.user

            # ✅ Get the existing expense
            expense_obj = models.Expense.objects.get(id=id, user=user, is_active=True)

            # ✅ Validate input data
            validator = validators.ExpenseValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data = validator.validated_data

            # ✅ Validate trip
            trip_id = validated_data.get('trip')
            if trip_id:
                trip_obj = models.Trip.objects.filter(id=trip_id, user=user, is_active=True).first()
                if not trip_obj:
                    raise Exception('Invalid trip or trip does not belong to user')
                validated_data['trip'] = trip_obj
            else:
                trip_obj = expense_obj.trip

            # ✅ Validate category
            category_id = validated_data.get('category')
            if category_id:
                category_obj = models.Category.objects.filter(id=category_id, is_active=True).first()
                if not category_obj:
                    raise Exception('Invalid or inactive category')
                validated_data['category'] = category_obj

            # # ✅ DATE VALIDATION — ensure expense date is not before trip start_date
            # expense_date = validated_data.get('date')
            # if expense_date and expense_date < trip_obj.start_date:
            #     raise Exception("Expense date cannot be before the trip's start date.")

            # ✅ Calculate trip remaining budget excluding this expense
            trip_expense_total = models.Expense.objects.filter(
                trip=trip_obj, is_active=True
            ).exclude(id=expense_obj.id).aggregate(
                total=Coalesce(Sum('expense'), Value(0, output_field=DecimalField()))
            )['total']

            trip_remaining_budget = trip_obj.budget - trip_expense_total
            expense_amount = validated_data.get('expense', expense_obj.expense)

            # ✅ Allow over-budget expenses but return a warning
            if expense_amount > trip_remaining_budget:
                context['warning'] = (
                    f"Expense amount exceeds remaining budget for this trip. "
                    f"Remaining: {round(trip_remaining_budget, 2)}, Entered: {expense_amount}"
                )

            # ✅ Update the expense object
            for key, value in validated_data.items():
                setattr(expense_obj, key, value)
            expense_obj.save()

            # ✅ Add success response
            context['data'] = {
                'id': str(expense_obj.id),
                'expense': expense_obj.expense,
                'trip': str(expense_obj.trip.id),
                'category': str(expense_obj.category.id),
                'date': expense_obj.date,
                'remarks': expense_obj.remarks,
                'bill_receipt': request.build_absolute_uri(expense_obj.bill_receipt.url) if expense_obj.bill_receipt else None,
                'payment_mode': expense_obj.payment_mode,
                'created_at': expense_obj.created_time(),
                'updated_at': expense_obj.last_updated()
            }

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)


    def delete(self, request, id):
        context={
            'success':1,
            'message':messages.DATA_DELETED,
            'data':{}
        }
        try:
            user=request.user
            expense_obj=models.Expense.objects.get(id=id,user=user,is_active=True)
            if not expense_obj:
                raise Exception('No expense found')
            expense_obj.delete()
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return Response(context)
    
    def get(self, request, id):
        context={
            'success':1,
            'message':messages.DATA_FOUND,
            'data':{}
        }
        try:
            user=request.user
            expense_obj=models.Expense.objects.get(id=id,user=user, is_active=True)
            if not expense_obj:
                raise Exception('No expense found')
            serializer = serializers.ExpenseSerializer(expense_obj,context={'request':request})
            context['data']=serializer.data
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return Response(context)

class UserBalance(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]

    def get(self, requset):
        context={
            'success':1,
            'message':messages.DATA_FOUND,
            'data':{}
        }
        try:
            user=requset.user
            total_budget=models.Trip.objects.filter(user=user).aggregate(total=Coalesce(Sum('budget'),Value(0,DecimalField())))['total']
            total_expense=models.Expense.objects.filter(user=user).aggregate(total=Coalesce(Sum('expense'),Value(0,DecimalField())))['total']

            total_balance=total_budget-total_expense

            if total_balance < 0:
                context['message'] = "Warning: You have exceeded your budget!"

            context['data']={
                'total_budget':total_budget,
                'total_expense':total_expense,
                'total_balance':total_balance
            }
        except Exception as e:
            context['success']=0
            context['message']=str(e)
        return Response(context)
    
class BillReceiptView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        context = {
            'success': 1,
            'message': messages.DATA_FOUND,
            'data': {}
        }
        try:
            user = request.user
            bill_obj = models.Expense.objects.get(id=id, user=user, is_active=True)
            serializer = serializers.ExpenseSerializer(bill_obj, context={'request': request})
            context['data'] = {
                'bill_receipt': serializer.data.get('bill_receipt')
            }
        except models.Expense.DoesNotExist:
            context['success'] = 0
            context['message'] = 'No bill receipt found.'
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)
    
class CurrentTripMonthlyExpenseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'success': 1,
            'message': messages.DATA_FOUND,
            'data': {}
        }

        try:
            user = request.user
            trip_id = request.query_params.get('trip_id')

            # Fetch specific trip if trip_id is provided
            if trip_id:
                current_trip = models.Trip.objects.filter(id=trip_id, user=user, is_active=True).first()
                if not current_trip:
                    context['message'] = "Trip with given ID not found or not active."
                    context['data'] = {
                        'total_expense': 0,
                        'expense_data': []
                    }
                    return Response(context)
            else:
                # Get current active trip
                current_trip = models.Trip.objects.filter(user=user, is_active=True).order_by('-created_at').first()
                if not current_trip:
                    context['message'] = "No active trip found."
                    context['data'] = {
                        'total_expense': 0,
                        'expense_data': []
                    }
                    return Response(context)

            # Get all active expenses for this trip
            expenses = models.Expense.objects.filter(
                user=user,
                trip=current_trip,
                is_active=True
            ).select_related('category')

            total_expense = expenses.aggregate(
                total=Coalesce(Sum('expense'), Value(0, output_field=DecimalField()))
            )['total']

            if total_expense == 0:
                context['message'] = "No expenses found for the selected trip."
                context['data'] = {
                    'trip_id': str(current_trip.id),
                    'destination': current_trip.destination,
                    'total_expense': 0,
                    'expense_data': []
                }
                return Response(context)

            expense_data = []
            for expense in expenses:
                cat = expense.category
                expense_data.append({
                    "expense_id": str(expense.id),
                    "category_name": cat.category_name if cat else "Uncategorized",
                    "total_expense": float(expense.expense),
                    "percentage": round((expense.expense / total_expense) * 100, 2),
                    "color_code": cat.color_code if cat and hasattr(cat, 'color_code') else "#808080",
                    "date": expense.date.strftime("%Y-%m-%d") if expense.date else None
                })

            context['data'] = {
                "trip_id": str(current_trip.id),
                "destination": current_trip.destination,
                "total_expense": float(total_expense),
                "expense_data": expense_data
            }

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)

    
# class CurrentTripMonthlyExpenseView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         context = {
#             'success': 1,
#             'message': messages.DATA_FOUND,
#             'data': {}
#         }

#         try:
#             user = request.user

#             # Get current active trip
#             current_trip = models.Trip.objects.filter(user=user, is_active=True).order_by('-created_at').first()
#             if not current_trip:
#                 context['message'] = "No active trip found."
#                 context['data'] = {
#                     'total_expense': 0,
#                     'expense_data': []
#                 }
#                 return Response(context)

#             # Get all active expenses for this trip
#             expenses = models.Expense.objects.filter(
#                 user=user,
#                 trip=current_trip,
#                 is_active=True
#             ).select_related('category')

#             total_expense = expenses.aggregate(
#                 total=Coalesce(Sum('expense'), Value(0, output_field=DecimalField()))
#             )['total']

#             if total_expense == 0:
#                 context['message'] = "No expenses found for the current trip."
#                 context['data'] = {
#                     'total_expense': 0,
#                     'expense_data': []
#                 }
#                 return Response(context)

#             expense_data = []
#             for expense in expenses:
#                 cat = expense.category
#                 expense_data.append({
#                     "expense_id": str(expense.id),
#                     "category_name": cat.category_name if cat else "Uncategorized",
#                     "total_expense": float(expense.expense),
#                     "percentage": round((expense.expense / total_expense) * 100, 2),
#                     "color_code": cat.color_code if cat and hasattr(cat, 'color_code') else "#808080",
#                     "date": expense.date.strftime("%Y-%m-%d") if expense.date else None
#                 })

#             context['data'] = {
#                 "trip_id": str(current_trip.id),
#                 "destination": current_trip.destination,
#                 "total_expense": float(total_expense),
#                 "expense_data": expense_data
#             }

#         except Exception as e:
#             context['success'] = 0
#             context['message'] = str(e)

#         return Response(context)

class PreviousTripsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'success': 1,
            'message': '',
            'data': []
        }

        try:
            user = request.user

            # ✅ Fetch only finished and inactive trips
            previous_trips = models.Trip.objects.filter(
                user=user,
                is_finished=True,
                is_active=False
            )

            trip_list = []
            for trip in previous_trips:
                total_expense = models.Expense.objects.filter(
                    user=user,
                    trip=trip
                ).aggregate(total=Sum('expense'))['total'] or 0

                trip_list.append({
                    "trip_id": str(trip.id),
                    "destination": trip.destination,
                    "start_date": trip.start_date,
                    "budget": float(trip.budget),
                    "total_expense": float(total_expense),
                    "status": "finished"
                })

            context['message'] = "Finished trips fetched successfully."
            context['data'] = trip_list

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)


class FinishedTrip(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        context = {
            'success': 1,
            'message': '',
            'data': {}
        }

        try:
            user = request.user
            is_completed = request.data.get('is_completed', False)

            # Get the current active and unfinished trip
            trip = models.Trip.objects.filter(user=user, is_active=True, is_finished=False).first()
            if not trip:
                raise Exception("❌ No active trip to finish.")

            # Total expenses for the trip
            total_expenses = models.Expense.objects.filter(user=user, trip=trip).aggregate(
                total=Sum('expense')
            )['total'] or Decimal('0.00')

            budget = trip.budget  # Keep as Decimal

            if not is_completed:
                raise Exception("⚠️ Please confirm trip completion by sending 'is_completed=true'.")

            # Generate appropriate message
            if total_expenses > budget:
                difference = total_expenses - budget
                context['message'] = f"🚨 Trip '{trip.destination}' finished! Over budget by {round(difference, 2)}."
            elif total_expenses == budget:
                context['message'] = f"🎯 Trip '{trip.destination}' finished! You used the **exact budget**. Well done!"
            else:
                difference = budget - total_expenses
                context['message'] = f"🎉 Trip '{trip.destination}' finished! You stayed within budget by {round(difference, 2)}."

            # Mark as finished and deactivate
            trip.is_finished = True
            trip.is_active = False  # Important: remove from current trips
            trip.save()

            context['data'] = {
                "trip_id": str(trip.id),
                "destination": trip.destination,
                "budget": str(budget),
                "total_expense": str(total_expenses),
                "status": "finished"
            }

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)
    
class PreviousTripsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'success': 1,
            'message': '',
            'data': {}
        }

        try:
            user = request.user

            previous_trips = models.Trip.objects.filter(user=user, is_finished=True)
            total_previous_trips = previous_trips.count()

            total_expenses = models.Expense.objects.filter(
                user=user,
                trip__in=previous_trips
            ).aggregate(total=Sum('expense'))['total'] or 0.0

            context['message'] = "Fetched previous trips summary successfully."
            context['data'] = {
                "total_previous_trips": total_previous_trips,
                "total_expenses": float(total_expenses)
            }

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)
    
class MonthlyTripExpenseViews(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'success': 1,
            'message': '',
            'data': {}
        }

        try:
            user = request.user
            trip_id = request.query_params.get('trip_id')

            if not trip_id:
                raise Exception("Trip ID is required.")

            trip = models.Trip.objects.filter(id=trip_id, user=user, is_finished=True).first()
            if not trip:
                raise Exception("Trip not found or not authorized.")

            # Group expenses by month and category
            expenses = (
                models.Expense.objects
                .filter(user=user, trip=trip)
                .annotate(month=TruncMonth('created_at'))
                .values('month', 'category')
                .annotate(total=Sum('expense'))
                .order_by('month')
            )

            # Format for pie chart per month
            result = {}
            for exp in expenses:
                month = exp['month'].strftime('%B %Y')
                category = exp['category']
                amount = float(exp['total'])

                if month not in result:
                    result[month] = {}

                result[month][category] = amount

            context['message'] = "Monthly expenses for selected trip fetched successfully."
            context['data'] = result

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)

# class PreviousTripMonthlyExpenseView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         context = {
#             'success': 1,
#             'message': messages.DATA_FOUND,
#             'data': {}
#         }

#         try:
#             user = request.user
#             trip_id = request.query_params.get('trip_id')

#             # Fetch specific trip (active or inactive) if trip_id is provided
#             if trip_id:
#                 current_trip = models.Trip.objects.filter(id=trip_id, user=user).first()
#                 if not current_trip:
#                     context['message'] = "Trip with given ID not found."
#                     context['data'] = {
#                         'total_expense': 0,
#                         'expense_data': []
#                     }
#                     return Response(context)
#             else:
#                 # Fallback to current active trip
#                 current_trip = models.Trip.objects.filter(user=user, is_active=True).order_by('-created_at').first()
#                 if not current_trip:
#                     context['message'] = "No active trip found."
#                     context['data'] = {
#                         'total_expense': 0,
#                         'expense_data': []
#                     }
#                     return Response(context)

#             # Fetch expenses for this trip
#             expenses = models.Expense.objects.filter(
#                 user=user,
#                 trip=current_trip,
#                 is_active=True
#             ).select_related('category')

#             total_expense = expenses.aggregate(
#                 total=Coalesce(Sum('expense'), Value(0, output_field=DecimalField()))
#             )['total']

#             if total_expense == 0:
#                 context['message'] = "No expenses found for the selected trip."
#                 context['data'] = {
#                     'trip_id': str(current_trip.id),
#                     'destination': current_trip.destination,
#                     'total_expense': 0,
#                     'expense_data': []
#                 }
#                 return Response(context)

#             # Group and format data for pie chart
#             category_totals = {}
#             category_colors = {}
#             for expense in expenses:
#                 cat_name = expense.category.category_name if expense.category else "Uncategorized"
#                 category_totals[cat_name] = category_totals.get(cat_name, 0) + float(expense.expense)
#                 category_colors[cat_name] = expense.category.color_code if expense.category and hasattr(expense.category, 'color_code') else "#808080"

#             pie_data = []
#             for cat_name, total in category_totals.items():
#                 pie_data.append({
#                     "category_name": cat_name,
#                     "total_expense": round(total, 2),
#                     "percentage": round((total / float(total_expense)) * 100, 2),
#                     "color_code": category_colors.get(cat_name, "#808080")
#                 })

#             context['data'] = {
#                 "trip_id": str(current_trip.id),
#                 "destination": current_trip.destination,
#                 "total_expense": float(total_expense),
#                 "expense_data": pie_data
#             }

#         except Exception as e:
#             context['success'] = 0
#             context['message'] = str(e)

#         return Response(context)

# class PreviousTripMonthlyExpenseView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         context = {
#             'success': 1,
#             'message': messages.DATA_FOUND,
#             'data': {}
#         }

#         try:
#             user = request.user
#             trip_id = request.query_params.get('trip_id')

#             # Fetch specific trip (active or inactive) if trip_id is provided
#             if trip_id:
#                 current_trip = models.Trip.objects.filter(id=trip_id, user=user).first()
#                 if not current_trip:
#                     context['message'] = "Trip with given ID not found."
#                     context['data'] = {
#                         'total_expense': 0,
#                         'expense_data': []
#                     }
#                     return Response(context)
#             else:
#                 # Fallback to current active trip
#                 current_trip = models.Trip.objects.filter(user=user, is_active=True).order_by('-created_at').first()
#                 if not current_trip:
#                     context['message'] = "No active trip found."
#                     context['data'] = {
#                         'total_expense': 0,
#                         'expense_data': []
#                     }
#                     return Response(context)

#             # Fetch expenses for this trip
#             expenses = models.Expense.objects.filter(
#                 user=user,
#                 trip=current_trip,
#                 is_active=True
#             ).select_related('category')

#             total_expense = expenses.aggregate(
#                 total=Coalesce(Sum('expense'), Value(0, output_field=DecimalField()))
#             )['total']

#             if total_expense == 0:
#                 context['message'] = "No expenses found for the selected trip."
#                 context['data'] = {
#                     'trip_id': str(current_trip.id),
#                     'destination': current_trip.destination,
#                     'total_expense': 0,
#                     'expense_data': []
#                 }
#                 return Response(context)

#             # Prepare expense data with expense_id and date
#             expense_data = []
#             for expense in expenses:
#                 category = expense.category
#                 cat_name = category.category_name if category else "Uncategorized"
#                 color = category.color_code if category and hasattr(category, 'color_code') else "#808080"
#                 expense_data.append({
#                     "expense_id": str(expense.id),
#                     "category_name": cat_name,
#                     "total_expense": float(expense.expense),
#                     "percentage": round((float(expense.expense) / float(total_expense)) * 100, 2),
#                     "color_code": color,
#                     "date": expense.date.strftime("%Y-%m-%d")
#                 })

#             # Final context data
#             context['data'] = {
#                 "trip_id": str(current_trip.id),
#                 "destination": current_trip.destination,
#                 "total_expense": float(total_expense),
#                 "expense_data": expense_data
#             }

#         except Exception as e:
#             context['success'] = 0
#             context['message'] = str(e)

#         return Response(context)

class PreviousTripMonthlyExpenseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'success': 1,
            'message': messages.DATA_FOUND,
            'data': {}
        }

        try:
            user = request.user
            trip_id = request.query_params.get('trip_id')

            # Fetch specific trip (active or inactive) if trip_id is provided
            if trip_id:
                current_trip = models.Trip.objects.filter(id=trip_id, user=user).first()
                if not current_trip:
                    context['message'] = "Trip with given ID not found."
                    context['data'] = {
                        'total_expense': 0,
                        'expense_data': []
                    }
                    return Response(context)
            else:
                # Fallback to current active trip
                current_trip = models.Trip.objects.filter(user=user, is_active=True).order_by('-created_at').first()
                if not current_trip:
                    context['message'] = "No active trip found."
                    context['data'] = {
                        'total_expense': 0,
                        'expense_data': []
                    }
                    return Response(context)

            # Fetch expenses for this trip
            expenses = models.Expense.objects.filter(
                user=user,
                trip=current_trip,
                is_active=True
            ).select_related('category')

            total_expense = expenses.aggregate(
                total=Coalesce(Sum('expense'), Value(0, output_field=DecimalField()))
            )['total']

            if total_expense == 0:
                context['message'] = "No expenses found for the selected trip."
                context['data'] = {
                    'trip_id': str(current_trip.id),
                    'destination': current_trip.destination,
                    'total_expense': 0,
                    'expense_data': []
                }
                return Response(context)

            # Prepare expense data with expense_id and date
            expense_data = []
            for expense in expenses:
                category = expense.category
                cat_name = category.category_name if category else "Uncategorized"

                data = {
                    "expense_id": str(expense.id),
                    "category_name": cat_name,
                    "total_expense": float(expense.expense),
                    "percentage": round((float(expense.expense) / float(total_expense)) * 100, 2),
                    "date": expense.date.strftime("%Y-%m-%d"),
                    "remarks":expense.remarks,
                    "payment_mode":expense.payment_mode
                }

                if category and category.color_code:
                    data["color_code"] = category.color_code

                expense_data.append(data)

            # Final context data
            context['data'] = {
                "trip_id": str(current_trip.id),
                "destination": current_trip.destination,
                "total_expense": float(total_expense),
                "total_budget": float(current_trip.budget),
                "expense_data": expense_data
            }

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)
    
# class PreviousTripsInvoice(APIView):
#     authentication_classes=[JWTAuthentication]
#     permission_classes=[IsAuthenticated]
    
#     def get(self, request):
#         context={
#             'success':1,
#             'message':messages.DATA_FOUND,
#             'data':{}
#         }
#         try:
#             user=request.user
#             previous_obj = models.Trip.objects.filter(user=user, is_finished=True)
#             if not previous_obj:
#                 raise Exception('No Previous trips found')
            
#             serializer = serializers.PreviousTripSerializer(previous_obj, many=True,context={'request':request})
#             context['data']=serializer.data
#         except Exception as e:
#             context['success']=0
#             context['message']=str(e)

#         return Response(context)
class PreviousTripsInvoicepdf(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            previous_trips = models.Trip.objects.filter(user=user, is_finished=True)

            if not previous_trips.exists():
                raise Exception('No Previous trips found')

            serializer = serializers.PreviousTripSerializer(
                previous_trips, many=True, context={'request': request}
            )

            html_string = render_to_string('api/trip_expense_report.html', {
                'trips': serializer.data
            })

            pdf_file = HTML(string=html_string).write_pdf()

            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=Trip-Invoice.pdf'
            return response

        except Exception as e:
            return Response({
                'success': 0,
                'message': str(e),
                'data': {}
            })




            



            
            
            


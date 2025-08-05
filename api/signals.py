from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Category

# Category-color mapping (hex codes)
DEFAULT_CATEGORIES = {
    "Transportation": "#FF5733",
    "Accommodation": "#33C1FF",
    "Food & Dining": "#33FF57",
    "Sightseeing & Activities": "#9B59B6",
    "Shopping": "#F39C12",
    "Local Transport": "#2980B9",
    "Travel Insurance": "#E74C3C",
    "Visa & Travel Documents": "#1ABC9C",
    "Internet & SIM Cards": "#8E44AD",
    "Tips & Gratuities": "#D35400",
    "Currency Exchange & ATM Fees": "#34495E",
    "Entertainment": "#2ECC71",
    "Health & Medical": "#E67E22",
    "Luggage & Travel Gear": "#16A085",
    "Emergency": "#C0392B",
    "Parking & Tolls": "#7F8C8D",
    "Event Tickets": "#F1C40F",
    "Gifts": "#BDC3C7",
    "Laundry": "#95A5A6",
    "Miscellaneous": "#D5DBDB",
    "Others": "#AAB7B8"  
}

@receiver(post_migrate)
def populate_default_categories(sender, **kwargs):
    # Ensure only runs for 'api' app
    if sender.label != 'api':
        return

    for name, color in DEFAULT_CATEGORIES.items():
        category, created = Category.objects.get_or_create(
            category_name=name,
            user=None,
            defaults={'is_default': True, 'color_code': color}
        )
        if not created:
            # Update existing category's color if it's incorrect
            if category.color_code != color:
                category.color_code = color
                category.save()

from django.db import migrations
from django.utils.text import slugify

def create_categories_and_subcategories(apps, schema_editor):
    Category = apps.get_model('ecomapp', 'Category')
    SubCategory = apps.get_model('ecomapp', 'SubCategory')

    category_data = {
        "appliances": ["Microwave", "Toaster", "Air Fryer", "Refrigerators", "Air Conditioners"],
        "phones": ["Samsung Galaxy", "iPhone", "Infinix", "iPad", "Samsung Tab", "Phone Cases", "Chargers", "Screen Guards"],
        "health": ["Face Wash", "Moisturizers", "Supplements", "First Aid Kits"],
        "fashion": ["T-Shirts", "Jeans", "Dresses", "Handbags"],
        "supermarket": ["Rice", "Canned Food", "Water", "Juice"],
        "computing": ["HP", "Dell", "MacBook", "Mouse", "Keyboards"],
        "gaming": ["PlayStation", "Xbox", "FIFA", "Call of Duty"],
        "music": ["Guitars", "Keyboards", "Stands", "Cables"],
        "books": ["Novels", "Mystery", "Math", "Science"],
        "therapy": ["Flashcards", "Books", "Fidget Spinners", "Visual Timers"],
        "others": ["Paper", "Staplers", "Mugs", "Gift Cards"]
    }

    for slug, subcategories in category_data.items():
        category, created = Category.objects.get_or_create(slug=slug, defaults={
            'name': slug.capitalize()
        })

        for sub in subcategories:
            sub_slug = slugify(f"{category.slug}-{sub}")
            original_sub_slug = sub_slug
            counter = 1

            while SubCategory.objects.filter(slug=sub_slug).exists():
                sub_slug = f"{original_sub_slug}-{counter}"
                counter += 1

            SubCategory.objects.get_or_create(
                category=category,
                name=sub,
                defaults={'slug': sub_slug}
            )

class Migration(migrations.Migration):
    dependencies = [
        ('ecomapp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_categories_and_subcategories),
    ]

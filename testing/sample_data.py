from authentication.models import User
from categories.models import Category
from collects.models import Collect, Item, Image
from django.utils import timezone


def create_sample_data():
    # a few simple instances for testing
    u1 = User()
    u1.save()
    cat1 = Category(category_name='test category 1')
    cat1.save()
    c1 = Collect(collection_name='test collection 1', collection_description='description',
                 collection_creation=timezone.now(), category=cat1, user=u1)
    c1.save()
    i1 = Item(item_name='test item 1', item_description='description', item_creation=timezone.now(), collection=c1)
    i1.save()


def delete_all_data():
    User.objects.all().delete()
    Category.objects.all().delete()
    Collect.objects.all().delete()
    Item.objects.all().delete()
    Image.objects.all().delete()

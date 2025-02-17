from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
MEALS = (
  ('B', 'Breakfast'),
  ('L', 'Lunch'),
  ('D', 'Dinner')
)

# Create your models here.
class Cat(models.Model):
  name = models.CharField(max_length=100)
  breed = models.CharField(max_length=100)
  description = models.TextField(max_length=250)
  age = models.IntegerField()
  # Create a Cat >--< Toy Relationship
  toys = models.ManyToManyField('Toy')
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  
  def __str__(self):
    return f"{self.name} ({self.id})"
  
  def get_absolute_url(self):
    return reverse('cat-detail', kwargs={'cat_id': self.id})
  
  def fed_for_the_day(self):
    return self.feeding_set.filter(date='2025-02-13').count() >= 3

class Feeding(models.Model):
  date = models.DateField('Feeding date')
  meal = models.CharField(
    max_length=1,
    choices=MEALS,
    default=MEALS[0][0]
  )
  '''
  The child in a 1:M relationship must have a 
  ForeignKey that references the parent object's id.
  Because a feeding belongs to a cat, we need to add 
  the ForeignKey to the Feeding model.

  The name 'cat' allows us to access the cat object for any
  feeding object, i.e., the_feeding.cat -> a cat object. This
  allows us to do things such as the_feeding.cat.name to render 
  a feeding's cat's name.

  However, the column name in the feeding table, is named cat_id 
  which holds the id/pk of the cat object that the feeding belongs to.

  What about accessing the feeding for a cat?  By default there will 
  be an attribute added to a cat objected named by default feeding_set which
  is a "related objects manager", thus we will be able to access a cat's
  feedings like this:  cat.feeding_set.all() or cat.feeding_set.filter(date__year=2025), etc.
  If you want to, you can change the name of the related manager by adding a
  related_name kwarg to the ForeignKey, e.g., models.ForeignKey(Cat, on_delete=models.CASCADE, related_name='feedings')
  '''
  cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

  def __str__(self):
    # Nice method for obtaining the friendly value
    # of a Field.choice.
    return f"{self.get_meal_display()} on {self.date}"

  class Meta:
    ordering = ['-date']


class Toy(models.Model):
  name = models.CharField(max_length=50)
  color = models.CharField(max_length=20)

  def __str__(self):
    return self.name
  
  def get_absolute_url(self):
    return reverse('toy-detail', kwargs={'pk': self.id})
  
from django.db import models

# Create your models here.
class product(models.Model):
    product_id=models.AutoField
    product_name=models.CharField(max_length=100)
    category=models.CharField(max_length=60,default="")
    subcategory=models.CharField(max_length=60,default="")
    price=models.IntegerField(default=0)
    highlight=models.CharField(max_length=300,default="")
    description=models.CharField(max_length=500)
    More_info=models.CharField(max_length=200,default="")
    publish_date=models.DateField()
    image=models.ImageField(upload_to="shoppinghub/images", default="")
   
    def __str__(self):
      return self.product_name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80)
    email = models.CharField(max_length=80, default="")
    phone = models.CharField(max_length=80, default="")
    desc = models.CharField(max_length=800, default="")



    def __str__(self):
        return self.name

class Orders(models.Model):
    order_id= models.AutoField(primary_key=True)
    items_json= models.CharField(max_length=6000)
    amount=models.IntegerField(default=0)
    name=models.CharField(max_length=90)
    email=models.CharField(max_length=120)
    address=models.CharField(max_length=120)
    city=models.CharField(max_length=120)
    state=models.CharField(max_length=120)
    zip_code=models.CharField(max_length=120)
    phone=models.CharField(max_length=20,default="")

class OrderUpdate(models.Model):
    update_id=models.AutoField(primary_key=True)
    order_id=models.IntegerField(default="")
    update_des=models.CharField(max_length=4000)
    timestamp=models.DateField(auto_now_add=True)

    def _str_(self):
        return self.update_des[0:10]+"..."
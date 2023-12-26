from django.shortcuts import render
from django.http import HttpResponse
from . models import product,Contact,Orders,OrderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from .PAYTM import Checksum 
MERCHANT_KEY = 'BI&B@DfXxG7OWNBd'#enter valid merchant key
# Create your views here.

def index(request):
    allProds = []
    catprods = product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        produc = product.objects.filter(category=cat)
        n = len(produc)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([produc, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shoppinghub/index.html', params)

def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.highlight.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = product.objects.filter(category=cat)
        produc = [item for item in prodtemp if searchMatch(query, item)]
        n = len(produc)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(produc) != 0:
            allProds.append([produc, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shoppinghub/search.html', params)

def about(request):
    return render(request, 'shoppinghub/about.html')

def contact(request):
    if request.method=="POST":
        name=request.POST.get('name', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone', '')
        desc=request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        return render(request, 'shoppinghub/thank.html')    
    return render(request, 'shoppinghub/contact.html')    

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_des, 'time': item.timestamp})
                    response = json.dumps({"status":"success","updates":updates,"itemsJson":order[0].items_json},default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"Error"}')
    return render(request, 'shoppinghub/tracker.html')

def productView(request, myid):
    # Fetch the product using id
    prod = product.objects.filter(id=myid)
    return render(request, 'shoppinghub/productview.html', {'prod':prod[0]})

def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone,amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_des="The order has been placed now")
        update.save()
        thank = True
        id = order.order_id
       # return render(request, 'shoppinghub/checkout.html', {'thank':thank, 'id': id})
        # Request paytm to transfer the amount to your account after payment by user
        param_dict = {
                'MID': 'qofSlN69628291597132D',#enter valid merchant ID
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shoppinghub/handlerequest/',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shoppinghub/paytm.html', {'param_dict': param_dict})
    return render(request, 'shoppinghub/checkout.html')

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
    if i == 'CHECKSUMHASH':
     checksum = form[i]

     verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
     if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'paymentstatus.html', {'response': response_dict})


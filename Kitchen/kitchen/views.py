from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import time
import random
import json
import threading
from threading import Thread
from operator import itemgetter
from colorama import init
from colorama import Fore, Back, Style
init()
# import thread
simulation_speed = 0.01

foods = [{
"id": 1,
"name": "pizza",
"preparation-time": 20 ,
"complexity": 2 ,
"cooking-apparatus": "oven"
},
 {
"id": 2,
"name": "salad",
"preparation-time": 10 ,
"complexity": 1 ,
"cooking-apparatus": "null"
},
{
"id": 3,
"name": "zeama",
"preparation-time": 7 ,
"complexity": 1 ,
"cooking-apparatus": "stove"
},
{
"id": 4,
"name": "Scallop Sashimi with Meyer Lemon Confit",
"preparation-time": 32 ,
"complexity": 3 ,
"cooking-apparatus": "null"
},
{
"id": 5,
"name": "Island Duck with Mulberry Mustard",
"preparation-time": 35 ,
"complexity": 3 ,
"cooking-apparatus": "oven"
},
{
"id": 6,
"name": "Waffles",
"preparation-time": 10 ,
"complexity": 1 ,
"cooking-apparatus": "stove"
},
{
"id": 7,
"name": "Aubergine",
"preparation-time": 20 ,
"complexity": 2 ,
"cooking-apparatus": "null"
},
{
"id": 8,
"name": "Lasagna",
"preparation-time": 30 ,
"complexity": 2 ,
"cooking-apparatus": "oven"
},
{
"id": 9,
"name": "Burger",
"preparation-time": 15 ,
"complexity": 1 ,
"cooking-apparatus": "oven"
},
{
"id": 10,
"name": "Gyros",
"preparation-time": 15 ,
"complexity": 1 ,
"cooking-apparatus": "null"
}]

cooks = [
{'rank': 1, 'proficiency': 1, 'name': 'Jessie Pinkman', 'catch_phrase': "Yo, yo, yo! 1-4-8-3 to the 3 to the 6 to the 9. representin' the ABQ. What up, Biatch? Leave at the tone."},
{'rank': 2, 'proficiency': 2, 'name': 'Pudge', 'catch_phrase': 'Fresh meat! Fresh meat!'},
{'rank': 3, 'proficiency': 3, 'name': 'The Duke', 'catch_phrase': 'I have been waiting for you, Mister Winters.'},
{'rank': 3, 'proficiency': 4, 'name': 'The Cook', 'catch_phrase': 'Повар спрашивает повара...'}
]


order_list = []

queue_oven = []
queue_stove = []

global ready_id
ready_id = -1

global queue_id
queue_id = 0
@csrf_exempt
def check_priority(order):
    global order_list

    order_list.append(order)

    order_list = sorted(order_list, key=itemgetter('priority'), reverse=True)

@csrf_exempt
def check_cooking_apparatus(dish_id):
    global queue_id
    queue_id += 1
    sign = 0
    for i in range(len(foods)):
        if (foods[i]["id"] == dish_id):
            apparatus = foods[i]["cooking-apparatus"]
            print(dish_id, apparatus)
            if (apparatus == "oven"):
                queue_oven.append(queue_id)
                print(queue_oven)
                while (sign != 1):
                    if (len(queue_oven) == 1):
                        cooking(dish_id)
                        if (queue_id in queue_oven):
                            queue_oven.remove(queue_id)
                        sign = 1
            elif (apparatus == "stove"):
                queue_stove.append(queue_id)
                print(queue_stove)
                while (sign != 1):
                    if (len(queue_stove) <= 2):
                        cooking(dish_id)
                        if (queue_id in queue_stove):
                            queue_stove.remove(queue_id)
                        sign = 1
            else:
                cooking(dish_id)
                pass


@csrf_exempt
def cook(name, rank, proficiency, dishes):
    dishes_in_progress = dishes
    cook_rank = rank
    cook_proficiency = proficiency
    cook_name = name

    if (dishes_in_progress < proficiency):
        dishes_in_progress += 1
        print(str(dishes_in_progress) + cook_name, '\n')
        search_dish(0, cook_rank)
        dishes_in_progress -= 1

@csrf_exempt
def search_dish(request, cook_rank):
    global ready_id

    dish_id = 0
    dish_complexity = 0

    id_data = {'order_id': -2}

    while (dish_id == 0):
        for item in order_list:
            order_items = item['items']
            for it in order_items:
                for f in foods:
                    if (it == f['id']):
                        dish_complexity = f['complexity']
                        if (dish_complexity == cook_rank):
                            dish_id = it
                            print("dish in work: " + str(dish_id))
                            if (dish_id in item['items']):
                                item['items'].remove(dish_id)
                                check_cooking_apparatus(dish_id)
                                if len(order_items) == 0:
                                    print("Order " + str(item['id']) + " is ready!")
                                    id_data = {'order_id': item['id']}
                                    headers = {'Content-Type' : 'application/json'}
                                    response = requests.post('http://127.0.0.1:8000/dinning/', data=json.dumps(id_data), headers = headers)
                                    print("Response is sent for the order " + str(item['id']))
                                    if (item in order_list):
                                        order_list.remove(item)
                            else:
                                break

    return HttpResponse(id_data)


@csrf_exempt
def cooking(dish_id):
    preparation_time = 0

    for f in foods:
        if (dish_id == f['id']):
            preparation_time = f['preparation-time']
            break

    time.sleep(preparation_time)


@csrf_exempt
def index(request):
    if request.method == 'POST':
        received_order = json.loads(request.body.decode("utf-8"))
        print(str(received_order) + "received_order")

        order_list_dynamics = threading.Thread(target=check_priority, name="Order Queue", args=(received_order,))
        order_list_dynamics.start()

        cook1 = threading.Thread(target=cook, name=cooks[0]['name'], args=(cooks[0]['name'], cooks[0]['rank'], cooks[0]['proficiency'], 0, ))
        cook1.start()

        cook2 = threading.Thread(target=cook, name=cooks[1]['name'], args=(cooks[1]['name'], cooks[1]['rank'], cooks[1]['proficiency'], 0, ))
        cook2.start()

        cook3 = threading.Thread(target=cook, name=cooks[2]['name'], args=(cooks[2]['name'], cooks[2]['rank'], cooks[2]['proficiency'], 0, ))
        cook3.start()

        cook4 = threading.Thread(target=cook, name=cooks[3]['name'], args=(cooks[3]['name'], cooks[3]['rank'], cooks[3]['proficiency'], 0, ))
        cook4.start()

    return HttpResponse(ready_id)

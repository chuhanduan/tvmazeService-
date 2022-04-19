# coding=utf-8
from django.shortcuts import render
from django.core.serializers import serialize
from django.http import HttpResponse
from django.template.loader import render_to_string
from . import models
import json
import pandas as pd
from treelib import Tree, Node


# Create your views here.


def index(request):
    return render(request, 'tvmaze/mainPage.html')

def shows(request):
    showList = serialize('json', models.Show.objects.all())
    showList = [show['fields'] for show in json.loads(showList)]
    return render(request, 'tvmaze/shows.html',{'data':json.dumps(showList),})

def visualiza(request):
    try:
        showName = request.POST.get('showName','')
        showId = list(models.Show.objects.filter(name=showName).values_list('showid'))[0][0]
        actorIdList = [item[0] for item in list(models.Character.objects.filter(showid = showId).values_list('actorid'))]
        actorList = list(models.Actor.objects.filter(actorid__in=actorIdList).all().values())
        show_actors_dict = {
            'showId': showId,
            'showName':showName,
            'actors':actorList
        }
        return render(request,'tvmaze/visualiza.html',show_actors_dict)
    except:
        render(request, 'tvmaze/visualiza.html')

def actor(request):
    # 根据演员id获取演员参演的节目列表
    actorId = request.GET['actorid']
    showIdList = [show[0] for show in list(models.Character.objects.filter(actorid=actorId).values_list('showid'))]
    actorShowList = list(models.Show.objects.filter(showid__in=showIdList).values_list('name', 'genres', 'imageurl'))

    # 获得电影流派列表
    genresSet = set()
    showGenresList = [item[0] for item in list(models.Show.objects.values_list('genres'))]
    pd.Series(showGenresList).apply(
        lambda x: genresSet.update(str(x).split(',') if x != None else '')
    )
    genresSet.remove('')

    # 建立流派-流派值-参演电影的三级树结构
    tree = Tree()
    tree.create_node(tag='genres', identifier='genres', data='genres')
    for genres in list(genresSet):
        node = Node(tag='{0}'.format(genres),identifier='{0}'.format(genres),data=genres)
        tree.add_node(node, parent='genres')
    # 将演员参演的节目添加到不同流派结点中
    for show in actorShowList:
        if(show[1] != None):
            for genre in str(show[1]).split(','):
                node = Node(tag='{0}'.format(show[0]), data=(show[0],show[2]))
                tree.add_node(node, parent=genre)
    actorShowsDict = dict()
    for genre in genresSet:
        if (tree.children(genre) == []):
            tree.remove_node(genre)  # 若流派结点下无挂载电影则删除该结点
        else:
            actorShowsDict[genre] = [node.data for node in tree.children(genre)]
    tree.show()
    print(actorShowsDict)
    return render(request, 'tvmaze/actor.html',{'data':actorShowsDict,'firstGenre':list(actorShowsDict.keys())[0]})
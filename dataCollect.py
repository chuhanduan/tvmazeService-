import requests
import pandas as pd
from sqlalchemy import create_engine
import collections

engine = create_engine('sqlite:///tvmazeService/tvmazeDb.db')
showIdList = list()

dealedShowList = list()
for pageCnt in range(5):
    params = {'page': pageCnt,}   # 带参数的GET请求,timeout请求超时时间
    response = requests.get(url='https://api.tvmaze.com/shows', params=params, timeout=60)
    if(response.status_code == 200):
        showList = response.json()
        for item in showList:
            tmpDict = dict()
            tmpDict['showId'] = item['id']
            showIdList.append(item['id'])
            tmpDict['name'] = item['name']
            tmpDict['genres'] = ','.join(item['genres'])
            tmpDict['rating'] = item['rating']['average']
            tmpDict['summary'] = item['summary']
            tmpDict['imageUrl'] = item['image']["medium"] if item['image'] != None else None
            dealedShowList.append(tmpDict) # dict list
    else:
        raise ValueError("get {0} error status {1}".format('https://api.tvmaze.com/shows',response.status_code))
pd.DataFrame.from_records(dealedShowList).to_sql('show',engine,if_exists='replace',chunksize=1000,index=False)

'''
    Extract the show id that has been requested in the history from the sqlite cache database, 
    and remove it from this request to prevent redundant repeated requests
'''
alreadExistShows = set(pd.read_sql('show', engine)['showId'])
needRequestShows = list(set(showIdList) - alreadExistShows)
actorsDict = collections.defaultdict(dict)  # can unique
characterDict = collections.defaultdict(dict)
for id in needRequestShows:
    params = {'embed': "cast", }
    response = requests.get(url='https://api.tvmaze.com/shows/{0}'.format(id), params=params, timeout=60)
    if (response.status_code == 200):
        show = response.json()
        for item in show['_embedded']['cast']:
            tmpDict_actor = dict()
            tmpDict_actor['actorId'] = item['person']['id']
            tmpDict_actor['name'] = item['person']['name']
            tmpDict_actor['country'] = item['person']['country']['name'] if item['person']['country'] != None else None
            tmpDict_actor['birthday'] = item['person']['birthday']
            tmpDict_actor['deathday'] = item['person']['deathday']
            tmpDict_actor['gender'] = item['person']['gender']
            tmpDict_actor['imageUrl'] = item['person']["image"]["medium"] if item['person']["image"] != None else None
            actorsDict[tmpDict_actor['actorId']] = tmpDict_actor
            tmpDict_character = dict()
            tmpDict_character['showId'] = id
            tmpDict_character['actorId'] = item['person']['id']
            tmpDict_character['name'] = item['character']['name']
            tmpDict_character['url'] = item['character']['url']
            characterDict[item['character']['id']] = tmpDict_character
actorsList = list(actorsDict.values())
pd.DataFrame.from_records(actorsList).to_sql('actor', engine, if_exists='replace', chunksize=1000,
                                                         index=False)
charactersList = list(characterDict.values())
pd.DataFrame.from_records(charactersList).to_sql('character', engine, if_exists='replace', chunksize=1000,
                                                         index=False)

'''
    URL:
        https://api.tvmaze.com/?page=:num
        https://api.tvmaze.com/shows/:id?embed=cast
    documentation:
        https://www.tvmaze.com/api#show-index
'''
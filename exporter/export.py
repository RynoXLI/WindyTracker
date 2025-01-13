import os
from cta import SimpleAPI, AsyncSimpleAPI
from load_dotenv import load_dotenv
import asyncio

load_dotenv(override=True)
tracker = AsyncSimpleAPI(key=os.getenv('CTA_KEY'))

async def get_data():
    vehicle_response = await tracker.getvehicles(rt='20')
    vids = [v['vid'] for v in vehicle_response['bustime-response']['vehicle']]

    # make an intermediate list of vids with a max of 10 vids per list
    vids_list = [vids[i:i + 10] for i in range(0, len(vids), 10)]

    # get the prediction data for each list of vids, asynchonously
    coroutines = []
    for vid_list in vids_list:
        coroutines.append(tracker.getpredictions(vid=vid_list))
    
    # gather the results of the coroutines
    predictions = await asyncio.gather(*coroutines)
    return vehicle_response, predictions

# add response to a mongodb database
from pymongo import MongoClient

# create collection function if exists
def create_collection(db, collection_name):
    if collection_name in db.list_collection_names():
        # print(f'Collection {collection_name} already exists')
        pass
    else:
        db.create_collection(collection_name)
        # print(f'Collection {collection_name} created')


# create function to collect responses every 60 seconds
import time
from datetime import datetime

def collect_data():
    while True:
        # authenticate to the database
        client = MongoClient('mongodb://root:example@localhost:27017/')

        db = client['cta']
        create_collection(db, 'predictions')
        collection = db['predictions']
        vehicle_response, predictions = asyncio.run(get_data())
        collection.insert_one({'vehicle_response': vehicle_response, 'predictions': predictions, "timestamp": datetime.now()})
        client.close()
        time.sleep(60)

if __name__ == '__main__':
    collect_data()
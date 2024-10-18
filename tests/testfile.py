import pytest
import TravelAlerts.src.TravelAlerts_sbubiloctech.TravelAlert as ta
import asyncio
import aiohttp

@pytest.fixture
def travel():
    return ta.TravelAlert()


def test_getRequestData_badrequest(travel):
    with pytest.raises(Exception) as e:
        print("Running test for bad html request:")
        response = travel.getValidatedRequest(url="https://travel.quw")
        assert response == None


def test_getRequestData_successfulresponse(travel):
    print("Running test for successful html request:")
    response = travel.getValidatedRequest(url="https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html/")
    assert response != None

def test_parsetable(travel):
    print("Running test for successful parsetable:")
    response = travel.getValidatedRequest(travel.ta_url)
    travel.travel_df = travel.parseTable(response)
    assert not len(list(travel.travel_df.index)) == 0

def test_bad_parsetable(travel):
    with pytest.raises(Exception) as e:
        print("Running test for bad parsetable:")
        travel.travel_df = travel.parseTable(None)
        assert travel.travel_df == None

def test_no_body(travel):
    travel.travel_df = travel.parseTable("abcd")
    assert travel.travel_df == None

async def check_bad_fetch(travel):
   travel.refreshAlerts()
   travel.travel_df.drop(travel.travel_df.index.to_list()[1:],inplace=True)
   travel.travel_df.at[0,"Link"] = "https://travel.state.gov/nonsense.quw"

   async with aiohttp.ClientSession() as session:
       task_list = travel.fetch_link_info(session, 0)
       result = await asyncio.gather(task_list)
       return result
       

def test_bad_fetch(travel):
    result = asyncio.run(check_bad_fetch(travel))
    assert result == [""]



 
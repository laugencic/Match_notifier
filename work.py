from decouple import config
from datetime import datetime,timedelta
import requests
import json
import time
from tzlocal import get_localzone

key=config('KEY')
headers={"X-Auth-Token":key}
PL="http://api.football-data.org/v4/competitions/PL" #premier league
CL="http://api.football-data.org/v4/competitions/CL" #ucl
# ac="http://api.football-data.org/v4/competitions" #all comps
BSA="http://api.football-data.org/v4/competitions/BSA" #brazil league
ELC="http://api.football-data.org/v4/competitions/ELC" #championship
EC="http://api.football-data.org/v4/competitions/EC" #european championship
FL1="http://api.football-data.org/v4/competitions/FL1" #league 1
BL1="http://api.football-data.org/v4/competitions/BL1" #bundesliga
SA="http://api.football-data.org/v4/competitions/SA" #serie a
CLI="http://api.football-data.org/v4/competitions/CLI" #south america champions league
WC="http://api.football-data.org/v4/competitions/WC" #world cup
PD = "http://api.football-data.org/v4/competitions/PD" # La Liga


comps=["PL", "CL", "PD", "BSA", "ELC", "EC", "FL1", "BL1", "SA", "CLI", "WC", "EL", "UCL", "FAC", "FLC"]

#checks whether the end points are valid
def send_requests():
    for comp in comps:
        response=requests.get(comp,headers=headers)
        if response.status_code !=200:
            print(f"Invalid for {comp}")
        
        else:
            pass

#gets the matches being played that day

def match_day():
    today=datetime.now().strftime("%Y-%m-%d")
    tomorrow=(datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
    all_matches={}
    for comp in comps:
        comp_url=f"http://api.football-data.org/v4/competitions/{comp}"
        response=requests.get(comp_url,headers=headers)
        time.sleep(5)

        if response.status_code==200:
            match=f"http://api.football-data.org/v4/competitions/{comp}/matches?dateFrom={today}&dateTo={tomorrow}"
            response2=requests.get(match,headers=headers)
            if response2.status_code==200:
                data=response2.json()    
                all_matches[comp]=data
            else:
                print(f"{comp} had an error")

    with open("matches.json","w")as file:
        json.dump(all_matches,file,indent=4)

match_day()
def asta(matches):
    TOKEN=config('TOKEN')
    CHAT_ID=config('CHAT_ID')
    url=f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    time.sleep(5)

    params={
        "chat_id":CHAT_ID,
        "text":matches,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("Message sent to Telegram!")
    else:
        print(f"Failed: {response.text}")


#extract the details about the matches
def get_details():
    with open("matches.json", "r") as file:
        data = json.load(file)
    
    message = []
    
    # Competition name lookup
    comp_names = {
        "EL": "Europa League",
        "UCL": "Conference League",
        "FAC": "FA Cup",
        "FLC": "Carabao Cup",
        "EC": "European Championship",
        "CLI": "Copa Libertadores"
    }
    
    for comp in comps:
        league = data.get(comp)
        if league:
            matches = league.get('matches', [])
            
            if not matches:
                continue
            
            # Add competition header
            display_name = comp_names.get(comp, league.get('competition', {}).get('name', comp))
            message.append(f"{display_name}")
            message.append("")  # blank line
            
            for match in matches:
                home = match['homeTeam']['name']
                away = match['awayTeam']['name']
                timee = match['utcDate']
                tz = get_localzone()        
                timee = timee.replace("Z", "+00:00")
                tt = datetime.fromisoformat(timee)
                lt = tt.astimezone(tz)
                time_str = lt.strftime("%H:%M")
                date = lt.strftime("%A, %B %d")

                m1 = f"{home} vs {away} on {date} at {time_str}"  
                message.append(m1)
            
            message.append("")  # spacing between competitions

    # Join into single string and send
    if message:
        full_message = "\n".join(message)
        asta(full_message)
    else:
        print("No matches today")

get_details()


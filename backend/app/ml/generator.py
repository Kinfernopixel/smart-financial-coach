import csv, random, datetime, json
CATEGORIES = ["Food & Drink","Transportation","Groceries","Subscriptions","Entertainment","Income","Rent","Utilities","Other"]
MERCHANTS = {
  "CoffeeHouse":["CoffeeHouse","Friends Cafe","Brew Bros"],
  "Spotify":["Spotify","MusicBox"],
  "Netflix":["Netflix"],
  "Supermarket":["Costco","Safeway","Market"],
  "Uber":["Uber","Lyft"],
  "Electric":["PG&E","PowerCo"],
}
def random_date(start, end):
 return start + datetime.timedelta(days=random.randint(0,(end-start).days))
def generate(n=500):
start = datetime.date.today() - datetime.timedelta(days=180)
 end = datetime.date.today()
 rows=[]
 for i in range(n):
 cat = random.choices(CATEGORIES, weights=[10,8,12,6,6,5,7,5,6])[0]
 merchant = random.choice(MERCHANTS.get("Supermarket") if cat=="Groceries" else sum(MERCHANTS.values(),[]))
 amt = round(random.uniform(1,200) * (1 if cat!="Income" else -1),2)
if cat=="Income": amt = round(random.uniform(800,4000),2)

 date = random_date(start,end).isoformat()
 rows.append({"id":i+1,"date":date,"merchant":merchant,"category":cat,"amount":amt})
return rows
if __name__=='__main__':
rows = generate(800)
    with open('../../data/sample_transactions.json','w') as f:
        json.dump(rows,f,indent=2)
    with open('../../data/sample_transactions.csv','w',newline='') as f:
        writer = csv.DictWriter(f,fieldnames=["id","date","merchant","category","amount"])
        writer.writeheader()
        writer.writerows(rows)

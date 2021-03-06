from models.BusStop import *
from controller.getBusData import *
from operator import itemgetter

def init_red():
	with open(r"BusStopRed.json", "r") as stop_r:
		stop_red=json.load(stop_r)
	red_line_stops=[]
	Index=1
	for stop in stop_red:
		red_line_stops=insert(red_line_stops, Index, stop["lon"], stop["lat"], "Red", False, stop["code"], stop["title"])
		Index+=1
	red_line_stops=insert(red_line_stops, Index, stop_red[0]["lon"], stop_red[0]["lat"], "Red", False, stop_red[0]["code"], stop_red[0]["title"])

	with open(r"mapdelta.json", "r") as fake_r:
		fake_stop_red=json.load(fake_r)
	Index=0
	prev_str=""
	Code=-1
	for fake_stop in fake_stop_red:
		#print(fake_stop)
		if fake_stop["title"][:-1]!=prev_str:
			Index+=1
		red_line_stops=insert(red_line_stops, Index, float(fake_stop["lon"]), float(fake_stop["lat"]), "Red", True, Code, fake_stop["title"])
		Code-=1
		prev_str=fake_stop["title"][:-1]
		Index+=1
	dist=[]
	with open(r"red_dist.json", "r") as r_dist:
		red_dist=json.load(r_dist)
	for d in red_dist:
		dist.append(float(d))
	return red_line_stops, dist
#red_line_stops, dist=init_red()
#print(dist)
#red_line_stops, dist_red=init_red()
#print("1st")
def init_blue():
	with open(r"BusStopBlue.json", "r") as stop_r:
		stop_blue=json.load(stop_r)
	blue_line_stops=[]
	Index=1
	for stop in stop_blue:
		blue_line_stops=insert(blue_line_stops, Index, stop["lon"], stop["lat"], "Blue", False, stop["code"], stop["title"])
		Index+=1
	blue_line_stops=insert(blue_line_stops, Index, stop_blue[0]["lon"], stop_blue[0]["lat"], "Blue", False, stop_blue[0]["code"], stop_blue[0]["title"])

	with open(r"mapgamma.json", "r") as fake_r:
		fake_stop_blue=json.load(fake_r)
	Index=0
	prev_str=""
	Code=-100
	for fake_stop in fake_stop_blue:
		#print(fake_stop)
		if fake_stop["title"][:-1]!=prev_str:
			Index+=1
		blue_line_stops=insert(blue_line_stops, Index, float(fake_stop["lon"]), float(fake_stop["lat"]), "Blue", True, Code, fake_stop["title"])
		Code-=1
		prev_str=fake_stop["title"][:-1]
		Index+=1
	dist=[]
	with open(r"blue_dist.json", "r") as b_dist:
		blue_dist=json.load(b_dist)
	for d in blue_dist:
		dist.append(float(d))
	return blue_line_stops, dist

def bus_queue(stops, dist, colour, code):
	#red_line_stops ,dist_red =  init_red()
	ETA=[]
	bus=None
	if colour=="Red":
		#print('R')
		b=Bus()
		b.update_response()
		bus=b.get_red()
		cnt=0
		for buses in bus:
			for i in range(0, len(stops)-1):
				maxlon=max(float(stops[i].pos[0]), float(stops[i+1].pos[0]))
				minlon=min(float(stops[i].pos[0]), float(stops[i+1].pos[0]))
				maxlat=max(float(stops[i].pos[1]), float(stops[i+1].pos[1]))
				minlat=min(float(stops[i].pos[1]), float(stops[i+1].pos[1]))
				if minlon<=float(buses["lon"])<=maxlon and minlat<=float(buses["lat"])<=maxlat:
					Dist=distance((float(buses["lon"]), float(buses["lat"])), stops[i+1].pos, "driving")
					if stops[i+1].code==code:
						ETA.append((Dist, cnt))
						cnt+=1
						break
					done=False
					for j in range(i+2, len(stops)):
						Dist+=dist[j-1]
						if stops[j].code==code:
							ETA.append((Dist, cnt))
							cnt+=1
							done=True
							break
					if done:
						break
					for j in range(1, len(stops)):
						Dist+=dist[j-1]
						if stops[j].code==code:
							ETA.append((Dist, cnt))
							cnt+=1
							done=True
							break
					if done:
						break
		ETA=sorted(ETA, key=itemgetter(0))
		'''
		flag=True
		for i in range(0, len(ETA)):
			Dist, index=ETA[i]
			if bus[index]["speed"]=="0":
				ETA[i]="--"
				flag=False
				continue
			ETA[i]=3.6*Dist/float(bus[index]["speed"])/60
			if i and flag and ETA[i]<ETA[i-1]:
				ETA[i]=ETA[i-1]
			flag=True
		'''
	else:
		b=Bus()
		b.update_response()
		bus=b.get_blue()
		cnt=0
		for buses in bus:
			for i in range(0, len(stops)-1):
				maxlon=max(float(stops[i].pos[0]), float(stops[i+1].pos[0]))
				minlon=min(float(stops[i].pos[0]), float(stops[i+1].pos[0]))
				maxlat=max(float(stops[i].pos[1]), float(stops[i+1].pos[1]))
				minlat=min(float(stops[i].pos[1]), float(stops[i+1].pos[1]))
				if minlon<=float(buses["lon"])<=maxlon and minlat<=float(buses["lat"])<=maxlat:
					Dist=distance((float(buses["lon"]), float(buses["lat"])), stops[i+1].pos, "driving")
					if stops[i+1].code==code:
						ETA.append((Dist, cnt))
						cnt+=1
						break
					done=False
					for j in range(i+2, len(stops)):
						Dist+=dist[j-1]
						if stops[j].code==code:
							ETA.append((Dist, cnt))
							cnt+=1
							done=True
							break
					if done:
						break
					for j in range(1, len(stops)):
						Dist+=dist[j-1]
						if stops[j].code==code:
							ETA.append((Dist, cnt))
							cnt+=1
							done=True
							break
					if done:
						break
		ETA=sorted(ETA, key=itemgetter(0))
	return ETA, bus

def dumb(etaToNear, Spos, Tpos, bus):
	etaToDest=[]
	flag=True
	DIST=distance(Spos, Tpos, "driving")
	for i in range(len(etaToNear)):
		Dist, index=etaToNear[i]
		#print(bus[index]["speed"], index)
		if int(bus[index]["speed"])==0:
			etaToNear[i]="--"
			etaToDest.append("--")
			flag=False
			continue
		etaToNear[i]=3.6*Dist/float(bus[index]["speed"])/60
		etaToDest.append(3.6*(Dist+DIST)/float(bus[index]["speed"])/60)
		if i and flag:
			if etaToNear[i]<etaToNear[i-1]:
				etaToNear[i]=etaToNear[i-1]
			if etaToDest[i]<etaToDest[i-1]:
				etaToDest[i]=etaToDest[i-1]
		flag=True
	return etaToNear, etaToDest

def judge(code, pos, stops):
	for i in range(0, len(stops)-1):
		maxlon=max(float(stops[i].pos[0]), float(stops[i+1].pos[0]))
		minlon=min(float(stops[i].pos[0]), float(stops[i+1].pos[0]))
		maxlat=max(float(stops[i].pos[1]), float(stops[i+1].pos[1]))
		minlat=min(float(stops[i].pos[1]), float(stops[i+1].pos[1]))
		if minlon<=pos[0]<=maxlon and minlat<=pos[1]<=maxlat:
			for j in range(i+1, len(stops)):
				if type(stops[j].code) is str:
					if stops[j].code==code:
						return True
					else:
						return False
#E=bus_queue("Red", "27011")
#print(E)
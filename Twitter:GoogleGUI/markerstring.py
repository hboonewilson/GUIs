#function that iterates through tweet locations;

def generateMarkerString(currentTweetIndex, tweetLatLonList, mapCenterLatLon):
	currentTweet = tweetLatLonList[currentTweetIndex]
	#if current tweet has no location attached to it, use map's center lat/lng
	#twitters lat/ln is actually flipped so use index 1 then index 0
	if currentTweet == None:
		mainMarker = f'|{mapCenterLatLon[1]},{mapCenterLatLon[0]}'
		secodaryM = ''
		#attach secondary markers as secondaryM 
		#(tweets with locations not being looked at)
		for tweet in tweetLatLonList:
			if tweet != None:
				secodaryM += f"|{tweet[1]},{tweet[0]}"
	else:
		#if current tweet has lat/ln use it!
		theLocal = tweetLatLonList[currentTweetIndex]
		mainMarker = f"|{theLocal[1]},{theLocal[0]}"
		secodaryM = ''
		#attach secondary markers as secondaryM 
		#(tweets with locations not being looked at)
		for i in range(0,len(tweetLatLonList)):
			if i != currentTweetIndex:
				mark = tweetLatLonList[i]
				if mark != None:
					secodaryM += f'|{mark[1]},{mark[0]}'
	#return a marker string to be added to googlemaps api call display a map with proper markers
	return f'&markers=color:red{mainMarker}&markers=color:blue|size:small{secodaryM}'


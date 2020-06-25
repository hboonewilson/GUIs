import tkinter
import math
import ssl
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlencode, quote_plus
import json
from twitteraccess import *
from markerstring import generateMarkerString as gMS
import webbrowser

#
# use two Google services, Google Static Maps API
# and Google Geocoding API.  Both require use of an API key.
# 
# When you have the API key, put it between the quotes in the string below
GOOGLEAPIKEY = 'Get GOOGLEAPIKEY'


# The Globals class demonstrates a better style of managing "global variables"
# than simply scattering the globals around the code and using "global x" within
# functions to identify a variable as global.
#
# We make all of the variables that we wish to access from various places in the
# program properties of this Globals class.  They get initial values here
# and then can be referenced and set anywhere in the program via code like
# e.g. Globals.zoomLevel = Globals.zoomLevel + 1
#
class Globals:
   rootWindow = None
   mapLabel = None
   enterPlace = None
   enterTweet = None
   currentTweetI = None
   tweetText = None 
   twitterTopic = None
   defaultLocation = "Mauna Kea, Hawaii"
   mapLocation = defaultLocation
   mapFileName = 'googlemap.gif'
   mapSize = 400
   zoomLevel = 9
   mapType = 'roadmap'
   lat = None
   screenName = None
   name = None
   lenTweetList = None
   latLnList = None 
   urlTweet = None 

   
# Given a string representing a location, return 2-element tuple
# (latitude, longitude) for that location 

def geocodeAddress(addressString):
   urlbase = "https://maps.googleapis.com/maps/api/geocode/json?address="
   geoURL = urlbase + quote_plus(addressString)
   geoURL = geoURL + "&key=" + GOOGLEAPIKEY

   # required (non-secure) security stuff for use of urlopen
   ctx = ssl.create_default_context()
   ctx.check_hostname = False
   ctx.verify_mode = ssl.CERT_NONE
   
   stringResultFromGoogle = urlopen(geoURL, context=ctx).read().decode('utf8')
   jsonResult = json.loads(stringResultFromGoogle)
   if (jsonResult['status'] != "OK"):
      print("Status returned from Google geocoder *not* OK: {}".format(jsonResult['status']))
      result = (0.0, 0.0) # this prevents crash in retrieveMapFromGoogle - yields maps with lat/lon center at 0.0, 0.0
   else:
      loc = jsonResult['results'][0]['geometry']['location']
      result = (float(loc['lat']),float(loc['lng']))
   return result

# See https://developers.google.com/maps/documentation/static-maps/
#
#
#
def getMapUrl():
   urlbase = "http://maps.google.com/maps/api/staticmap?"
   args = "center={},{}&zoom={}&size={}x{}&format=gif&maptype={}".format(Globals.lat,Globals.lng,Globals.zoomLevel,Globals.mapSize,Globals.mapSize,Globals.mapType)
   #encodedMarker = quote_plus(f'&markers={Globals.lat},{Globals.lng}')
   if Globals.latLnList == None or Globals.lenTweetList == 0: 
      encodedMarker = f'&markers={Globals.lat},{Globals.lng}' 
   else:
      encodedMarker = Globals.markerStr

   args += encodedMarker
   args = args + "&key=" + GOOGLEAPIKEY
   mapURL = urlbase + args
   return mapURL



# Retrieve a map image via Google Static Maps API, storing the 
# returned image in file name specified by Globals' mapFileName
#
def retrieveMapFromGoogle():
   url = getMapUrl()
   urlretrieve(url, Globals.mapFileName)

########## 
#  basic GUI code

def displayMap():
   if Globals.lat == None:
      createGeoTag(Globals.mapLocation)
   Globals.trackZoom.configure(text=f'ZoomLevel:{Globals.zoomLevel}')
   retrieveMapFromGoogle()    
   mapImage = tkinter.PhotoImage(file=Globals.mapFileName)
   Globals.mapLabel.configure(image=mapImage)
   # next line necessary to "prevent (image) from being garbage collected" - http://effbot.org/tkinterbook/label.htm
   Globals.mapLabel.mapImage = mapImage

def retTweets():
   authTwitter()
   tweets = searchTwitter(Globals.twitterTopic, latlngcenter=(Globals.lat, Globals.lng))
   Globals.savedTweets = []
   Globals.latLnList = []
   for tweet in tweets:
      Globals.savedTweets.append(tweet)
      if tweet['coordinates'] != None:
         Globals.latLnList.append(tweet['coordinates']['coordinates'])
      else:
         Globals.latLnList.append(None)
   Globals.currentTweetI = 0
   Globals.lenTweetList = len(Globals.savedTweets)

def createGeoTag(addressString):
   Globals.lat, Globals.lng =  geocodeAddress(addressString)
def genMarkerStr():
   Globals.markerStr = gMS(Globals.currentTweetI, Globals.latLnList, (Globals.lat,Globals.lng))
def displayTweetAndInfo():
   if Globals.lenTweetList != 0:
      Globals.tweetTextWindow.configure(state=tkinter.NORMAL)
      Globals.tweetTextWindow.delete(1.0, tkinter.END)
      Globals.tweetTextWindow.insert(tkinter.INSERT,Globals.tweetText)
      Globals.tweetTextWindow.configure(state=tkinter.DISABLED)
      Globals.scNameWid.configure(text=f'Screen Name: {Globals.screenName}')
      Globals.nameWid.configure(text=f"Name: {Globals.name}")
      Globals.tweetListLable.configure(text=f'Tweet number {(Globals.currentTweetI) + 1} out of {Globals.lenTweetList} Tweets.')
      Globals.url.configure(state=tkinter.NORMAL)
      Globals.url.delete(1.0, tkinter.END)
      genMarkerStr()
   if Globals.urlTweet != None:
         Globals.url.insert(tkinter.INSERT, Globals.urlTweet)
         Globals.url.configure(state=tkinter.DISABLED)
def changeGlobals(index=0):
   if Globals.lenTweetList != 0:
      Globals.tweetText = Globals.savedTweets[index]['text']
      Globals.screenName = Globals.savedTweets[index]['user']['screen_name']
      Globals.name = Globals.savedTweets[index]['user']['name']
      Globals.urlTweet = Globals.savedTweets[index]['user']['url']
   else:
      Globals.tweetTextWindow.configure(state=tkinter.NORMAL)
      Globals.tweetTextWindow.delete(1.0, tkinter.END)
      Globals.tweetTextWindow.insert(tkinter.INSERT,'Sorry, but there were no tweets available in this location')
      Globals.tweetTextWindow.configure(state=tkinter.DISABLED)
      
def readEntryDisplayMapAndTweets():

   twtEnt = Globals.enterTweet.get()
   Globals.twitterTopic = twtEnt
   Globals.enterTweet.delete(0, tkinter.END)
   txtEnt = Globals.enterPlace.get()
   Globals.mapLocation = txtEnt
   Globals.enterPlace.delete(0, tkinter.END)
   createGeoTag(Globals.mapLocation)
   retTweets()
   changeGlobals()
   displayTweetAndInfo()
   displayMap()

def radioButtonPush():
   mapStyle = Globals.choiceMap.get()
   if mapStyle == 'roadmap':
      Globals.mapType = 'roadmap'
   elif mapStyle == 'satellite':
      Globals.mapType = 'satellite'
   elif mapStyle == 'terrain':
      Globals.mapType = 'terrain'
   else:
      Globals.mapType = 'hybrid'
   displayMap()
def zoomIn():
   Globals.zoomLevel += 1
   displayMap()
def zoomOut():
   if Globals.zoomLevel > 0:
      Globals.zoomLevel -= 1
      displayMap()
def goBackTweets():
   if Globals.currentTweetI > 0:
      Globals.currentTweetI -= 1
      changeGlobals(Globals.currentTweetI)
      displayTweetAndInfo()
      displayMap()
def goForwardTweets():
   if Globals.lenTweetList > Globals.currentTweetI:
      Globals.currentTweetI += 1
      changeGlobals(Globals.currentTweetI)
      displayTweetAndInfo()
      displayMap()
def openUrl():
   webbrowser.open(Globals.urlTweet)
def initializeGUIetc():
   Globals.rootWindow = tkinter.Tk()
   Globals.choiceMap = tkinter.StringVar()
   Globals.choiceMap.set('roadmap')

   Globals.rootWindow.title("HW9")

   mainFrame = tkinter.Frame(Globals.rootWindow) 
   mainFrame.pack()
   top = tkinter.Frame(mainFrame)
   top.pack()
   topLeft = tkinter.Frame(top)
   topLeft.pack(side=tkinter.LEFT)
   
   Globals.enterPlace = tkinter.Entry(topLeft)
   Globals.enterPlace.pack()
   Globals.enterTweet = tkinter.Entry(topLeft)
   Globals.enterTweet.pack()
   
   topRight = tkinter.Frame(top)
   topRight.pack()

   placeLabel = tkinter.Label(topRight, text='Enter Place Here!')
   placeLabel.pack()

   tweetLabel = tkinter.Label(topRight, text='Enter Tweet Topic Here!')
   tweetLabel.pack()

   readEntryAndDisplayMapButton = tkinter.Button(mainFrame, text="Execute Search!", command=readEntryDisplayMapAndTweets)
   readEntryAndDisplayMapButton.pack()

   # we use a tkinter Label to display the map image
   Globals.mapLabel = tkinter.Label(mainFrame, width=Globals.mapSize, bd=2, relief=tkinter.FLAT)
   Globals.mapLabel.pack()

   userNameFrame = tkinter.Frame(mainFrame)
   userNameFrame.pack()

   Globals.scNameWid = tkinter.Label(userNameFrame, text=f'Screen Name: {Globals.screenName}')
   Globals.scNameWid.pack(side=tkinter.LEFT)

   Globals.nameWid = tkinter.Label(userNameFrame, text=f'Name: {Globals.name}')
   Globals.nameWid.pack()

   tweetTextFrame = tkinter.Frame(mainFrame)
   tweetTextFrame.pack()

   Globals.tweetTextWindow = tkinter.Text(tweetTextFrame, width=72, height=3, bd=2, relief=tkinter.GROOVE)
   Globals.tweetTextWindow.insert(tkinter.INSERT, 'No tweets available')
   Globals.tweetTextWindow.configure(state=tkinter.DISABLED)
   Globals.tweetTextWindow.pack()

   tweetFrame = tkinter.Frame(mainFrame)
   tweetFrame.pack()
   tweetBack = tkinter.Button(tweetFrame, text='<<', command=goBackTweets)
   tweetBack.pack(side=tkinter.LEFT)
   Globals.tweetListLable = tkinter.Label(tweetFrame, text=f'Tweet number 0 out of 0 Tweets.')
   Globals.tweetListLable.pack(side=tkinter.LEFT)
   tweetForward = tkinter.Button(tweetFrame, text='>>', command=goForwardTweets)
   tweetForward.pack()
   urlFrame = tkinter.Frame(mainFrame)
   urlFrame.pack()
   urlLabel = tkinter.Label(urlFrame, text="Tweet's url")
   urlLabel.pack(side=tkinter.LEFT)

   Globals.url = tkinter.Text(tweetTextFrame, width=36, height=3, bd=2, relief=tkinter.GROOVE)
   Globals.url.insert(tkinter.INSERT, 'No url')
   Globals.url.configure(state=tkinter.DISABLED)
   Globals.url.pack(side=tkinter.LEFT)
   urlButton = tkinter.Button(tweetTextFrame, text='Open Url', command=openUrl)
   urlButton.pack()

   bottomFrame = tkinter.Frame(mainFrame)
   bottomFrame.pack()

   bottomLeft = tkinter.Frame(bottomFrame)
   bottomLeft.pack(side=tkinter.LEFT)
   Globals.trackZoom = tkinter.Label(bottomLeft, text=f'ZoomLevel:{Globals.zoomLevel}')
   Globals.trackZoom.pack(side=tkinter.LEFT)
   plus = tkinter.Button(bottomLeft, text='+', command=zoomIn)
   plus.pack()
   minus = tkinter.Button(bottomLeft, text='-', command=zoomOut)
   minus.pack()

   bottomMiddle = tkinter.Frame(bottomFrame)
   bottomMiddle.pack(side=tkinter.LEFT)

   roadMap = tkinter.Radiobutton(bottomMiddle, text="Road Map", variable=Globals.choiceMap,value='roadmap',command=radioButtonPush)
   roadMap.pack()
   satellite = tkinter.Radiobutton(bottomMiddle, text="Satellite", variable=Globals.choiceMap, value='satellite',command=radioButtonPush)
   satellite.pack()


   bottomRight = tkinter.Frame(bottomFrame)
   bottomRight.pack()

   terrain = tkinter.Radiobutton(bottomRight, text='Terrain', variable=Globals.choiceMap, value='terrain',command=radioButtonPush)
   terrain.pack()
   hybrid = tkinter.Radiobutton(bottomRight, text='Hybrid', variable=Globals.choiceMap, value='hybrid',command=radioButtonPush)
   hybrid.pack()



def mainGui():
    initializeGUIetc()
    displayMap()
    Globals.rootWindow.mainloop()


'''
display a map pin in the center of the map. Note: for this and the previous item, in addition to adding GUI elements, you will need to modify getMapURL to add more parts to the string sent to Google.
'''

mainGui()


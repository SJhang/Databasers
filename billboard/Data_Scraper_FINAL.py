import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pymysql

#connect to database
conn= pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd='***', db='billboard')
cur = conn.cursor()
cur.execute("DROP DATABASE billboard")
print ("DROP DATABASE billboard")
cur.execute("CREATE DATABASE billboard")
print ("CREATE DATABASE billboard")
cur.execute("USE billboard")

cur.execute("CREATE TABLE song ("
            "SongID int(11) NOT NULL AUTO_INCREMENT, "
            "SongName varchar(255) DEFAULT NULL, "
            "Artist varchar(255) DEFAULT NULL, "
            "PRIMARY KEY (SongID)"
            ")")
print ("CREATE TABLE song")

cur.execute("CREATE TABLE rank ("
            "WeekName varchar(255) NOT NULL, "
            "SongID int(11) NOT NULL, "
            "CurrentRank int(11) NOT NULL, "
            "PRIMARY KEY(WeekName, SongID), "
            "FOREIGN KEY (SongID) REFERENCES song(SongID)"
            ");")
print ("CREATE TABLE rank")

def make_soup(url):
    thePage = requests.get(url)
    soupData = BeautifulSoup(thePage.content, "html.parser")
    return soupData



def song_parser():
    #2D list that stores unique songs and artists
    song_list = []

    today = datetime.strptime("2016-04-30", "%Y-%m-%d")
    for i in range(0, 70):
        #gets the week that the program is scraping
        weekAgo = today - timedelta(weeks=i)
        weekAgo = weekAgo.strftime("%Y-%m-%d")

        soup = make_soup("http://www.billboard.com/charts/hot-100/" + weekAgo)
        song_data = soup.findAll("article", {"class": "chart-row"}) 
        print ("scraping through week " + weekAgo)
        #This loop goes through the top 100 songs for each week
        for item in song_data:
            #inner list stores the song and artist for each song
            inner_list = []

            #scrapes each song name
            songName = item.find("h2").text
            inner_list.append(songName)
            songName=str(songName)
            
            #scrapes each artist name
            artist = item.find("a").text.strip()
            artist=str(artist)
            inner_list.append(artist)
            
            #makes a list of unique songs
            if inner_list not in song_list:
                song_list.append(inner_list)


    #populates the song table
    for song in song_list:
        songName= song[0]
        artist= song[1]
            
        cur.execute("INSERT INTO song(SongName, Artist) VALUES (%s, %s)", (songName, artist))
    print ("Finished populating song table")

#function that populates the ranking table
def populate_ranking():
    
    today = datetime.strptime("2016-04-30", "%Y-%m-%d")
    for i in range(0, 70):

        #gets the week that the program is scraping
        weekAgo = today - timedelta(weeks=i)
        weekAgo = weekAgo.strftime("%Y-%m-%d")

        soup = make_soup("http://www.billboard.com/charts/hot-100/" + weekAgo)
        song_data = soup.findAll("article", {"class": "chart-row"})
        print("going through week " + weekAgo)

        #This loop goes through the top 100 songs for each week
        for item in song_data:
            #gets the current ranking of a song for the week
            currentRanking = item.findAll("span")[0].text
            currentRanking = str(currentRanking)
            currentRanking = int(currentRanking)

            #gets the song name for the week                                  
            songName = item.find("h2").text
            songName = str(songName)
            
            #gets the artist name
            artist = item.find("a").text.strip()
            artist = str(artist)
        

           
            #queries the songID from the song table and makes it into an int
            cur.execute("SELECT SongID FROM song WHERE (SongName=%s and Artist=%s)",(songName,artist))
            songID = cur.fetchone()
            songID = str(songID)
            songID = songID.replace("(", "")
            songID = songID.replace(")", "")
            songID = songID.replace(",", "")
            songID = int(songID)

            #populate the ranking table
            cur.execute("INSERT INTO rank (WeekName, SongID, CurrentRank) VALUES (%s,%s,%s)", (weekAgo,songID,currentRanking))

    print ("Finished populating rank table")
            

def main():
    print ("-----------------------")
    song_parser()
    print ("-----------------------")
    populate_ranking()

main()

cur.connection.commit()
cur.close()
conn.close()

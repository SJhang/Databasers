import pymysql
from datetime import datetime, timedelta

conn= pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd='***', db='billboard')
cur = conn.cursor()
cur.execute("USE billboard")


def getSat(input):
    inputDate = datetime.strptime(input, "%Y-%m-%d") + timedelta(days=1)
    monday = inputDate - timedelta(days=inputDate.weekday())
    saturday = monday + timedelta(days=5)
    return saturday.strftime("%Y-%m-%d")

option = ""
while option != "7":
    option = str(input(" Choose a number:\n"
                       " 1) Get the rank of a song from a specific week\n"
                       " 2) A list of Top 100 songs that an artist had this year\n"
                       " 3) The number of times a song appeared in the Top 100 songs this year\n"
                       " 4) The #1 song for a specific week\n"
                       " 5) The peak ranking a song has received for this year\n"
                       " 6) The change of rank of a song over time\n"
                       " 7) Exit\n"
                       " **This database dates between 2015-01-03 ~ 2016-04-30**\n"
                       " Enter: \n"))

    if option == "1":

        # get rank of song in specific week
        is_valid_input = False
        while not is_valid_input:
            try:
                week = (input("Enter the date(YYYY-MM-DD): "))
                week = getSat(week)
                is_valid_input = True
            except:
                print("Input should be in YYYY-MM-DD")

        song = str(input("Enter the song name: "))

        cur.execute("SELECT song.SongName, rank.CurrentRank "
                    "FROM rank, song "
                    "WHERE rank.SongID = song.SongID AND song.SongName REGEXP %s And rank.WeekName=%s", (song, week))
        result = cur.fetchone()

        if not result:
            print("No song name found")
        else:
            result_int = result[1]
            result_song = result[0]
            print("The ranking for the song, '" + result_song + "' on the week of " + week + " is", result_int)

    elif option == "2":

        # songs that an artist had in top 100
        artist = str(input("Enter artist name: "))
        cur.execute("SELECT SongName, Artist FROM song WHERE Artist REGEXP %s", (artist))
        result = cur.fetchall()

        for i in result:
            print(i[0], "by", i[1])

    elif option == "3":

        # Number of times song appeared in top 100
        song = str(input("Enter the song: "))
        cur.execute("SELECT song.SongName, song.Artist, COUNT(rank.CurrentRank) "
                    "FROM song, rank "
                    "WHERE song.SongID=rank.SongID AND song.SongName REGEXP %s"
                    "GROUP BY song.SongName, song.Artist", (song))
        result = cur.fetchall()


        def iteratorTuple(tuple):
            for x, y, z in tuple:
                print(x, "by", y, "appeared in the chart", z, "times")


        if not result:
            print("Song not found")
        else:
            iteratorTuple(result)

    elif option == "4":

        # 1 song for specific week
        is_valid_input = False
        while not is_valid_input:
            try:
                week = (input("Enter the date(YYYY-MM-DD): "))
                week = getSat(week)
                is_valid_input = True
            except:
                print("Input should be in YYYY-MM-DD")
        cur.execute(
            "SELECT song.SongName, song.Artist FROM rank, song WHERE song.SongID=rank.SongID AND rank.WeekName=%s AND rank.CurrentRank='1'",
            (week))
        result = cur.fetchone()
        print("During the week of "+week)
        print("The #1 song in the Billboard Chart Hot 100 is '" + result[0] + "' by " + result[1])

    elif option == "5":

        # Peak ranking a song has received from the latest timeline
        song = str(input("Enter the song name: "))
        cur.execute(
            "SELECT ANY_VALUE(rank.WeekName), ANY_VALUE(song.SongName), ANY_VALUE(song.Artist), MIN(rank.CurrentRank) "
            "FROM rank, song "
            "WHERE song.SongID=rank.SongID AND song.SongName REGEXP %s", (song))
        result = cur.fetchall()
        if not result:
            print("Song not found")
        else:
            # print (result)
            print(result[0][1], "by", result[0][2])
            print("Week:", result[0][0])
            print("Peak ranking:", result[0][3])
            print(result[0][1], "by", result[0][2], "was at the peak ranking as high as", result[0][3],
                  "in the week of", result[0][0])

    elif option == "6":

        # The change of rank of a song over time
        is_valid_input = False
        while not is_valid_input:
            try:
                week1 = (input("Enter the beginning date(YYYY-MM-DD): "))
                week1 = getSat(week1)
                is_valid_input = True
            except:
                print("Input should be in YYYY-MM-DD")

        is_valid_input1 = False
        while not is_valid_input1:
            try:
                week2 = str(input("Enter the ending date(YYYY-MM-DD): "))
                week2 = getSat(week2)
                is_valid_input1 = True
            except:
                print("Input should be in YYYY-MM-DD")

        song = str(input("Enter the song name: "))

        cur.execute("SELECT song.SongName, song.Artist, rank.CurrentRank, rank.WeekName "
                    "FROM rank, song "
                    "WHERE song.SongID=rank.SongID AND song.SongName REGEXP %s AND %s <= rank.WeekName AND rank.WeekName <= %s",
                    (song, week1, week2))

        result = cur.fetchall()


        def checkEqual(list):
            return list[1:] == list[:-1]


        def iteratorTuple(tuple):
            for x, y, z, a in tuple:
                print(x, "by", y, "ranks", z, "in the week", a)


        if not result:
            print("Song not found")
        else:
            iteratorTuple(result)



cur.connection.commit()
cur.close()
conn.close()

from flask import Flask, request, render_template, jsonify
import imdb
from bs4 import BeautifulSoup
from urllib.request import urlopen

moviesDB = imdb.IMDb()

app = Flask(__name__)

# normal function  to get the image url 
def movie_url(m_id):
	film_id = m_id
	url = 'http://www.imdb.com/title/tt%s/' % (film_id)
	soup = BeautifulSoup(urlopen(url).read())
	links = soup.find_all('div', {'class': 'poster'})
	if links:
		image = links[0].find('img')['src']
	else:
		image = "static/image/default_movie.jpg"
	return image

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def movie():
	re = request.get_data()
	re = str(re.decode("utf-8"))[5:]
	movies = moviesDB.search_movie(re)
	# print("movies is",movies)

	data = []
	
	for movie in movies:
		title = movie['title']
		id = movie.getID()
		image = movie.get('full-size cover url', "static/image/default_movie.jpg")
		if 'nopicture' in image:
			image = "static/image/default_movie.jpg"
		d = {'id': id, 'title': title, 'image': image, 'year': movie.get('year',' ') }

		if d not in data:
			data.append(d)
	
	#print("data is",data)
	return jsonify(data)

@app.route('/<movie>')
def movie_details(movie):
	movie_d = moviesDB.get_movie(movie)

	if 'box office' in movie_d.keys():
		budget = movie_d['box office'].get('Budget','Data Not Available')
		boxoffice = movie_d['box office'].get('Cumulative Worldwide Gross','Data Not Available')
	else:
		budget = 'Data Not Available'
		boxoffice = 'Data Not Available'

	if 'directors' in movie_d.keys():
		directors = movie_d['directors']
	elif 'writer' in movie_d.keys():
		directors =  movie_d['writer']
	else:
		directors = moviesDB.get_movie('4154796')['directors']

	if 'cast' in movie_d.keys():
		cast = movie_d['cast'][0:10]
	else:
		cast = moviesDB.get_movie('4154796')['cast'][0:1]

	d = {'id': movie, 
	'title': movie_d['title'], 
	'image': movie_d.get('full-size cover url', "static/image/default_movie.jpg"), 
	'year': str(movie_d.get('year'," ")),
	'cast':cast ,
	'genres':movie_d['genres'],
	'runtime': movie_d.get('runtime','Data Not Available'),
	'budget': budget,
	'boxoffice': boxoffice,
	'rating': movie_d.get('rating','Data Not Available'),
	'votes': movie_d.get('votes','Data Not Available'),
	'directors': directors,
	'lang': movie_d.get('languages',{'Data Not Available'}),
	'plot': movie_d.get('plot',{'Data Not Available'}),
	'imdb':'https://www.imdb.com/title/tt'+ movie +'/'
	}

	return render_template("movie_details.html", movie = d)

@app.route('/actor')
def actor():
    return render_template("actor.html")


@app.route('/actor', methods=['POST'])
def actors():
	re = request.get_data()
	re = str(re.decode("utf-8"))[5:]
	actors = moviesDB.search_person(re)

	data = []
	
	for actor in actors:
		name = actor['name']
		id = actor.getID()
		image = actor.get('full-size headshot', "/static/image/default_actor_M.jpg")
		if 'nopicture' in image:
			image = "static/image/default_actor_M.jpg"

		d = {'id': id, 'name': name, 'image': image}
		
		if d  not in data:
			data.append(d)
	
	return jsonify(data)


@app.route('/actor/<actor>')
def actor_details(actor):
	print("under actor section")
	actor_d = moviesDB.get_person(actor)

	if 'nick names' in actor_d.keys():
		nickN= actor_d['nicknames']  
	elif 'birth name' in actor_d.keys():
		nickN= { actor_d['birth name'] }
	else:
		nickN= { actor_d['name'] }
	
	if 'birth info' in actor_d.keys():
		birth = actor_d['birth info'].get('birth place','Data Not Available')
	else:
		birth = 'Data Not Available'

	if 'in development' in actor_d.keys():
		develp = actor_d.get('in development',{'Data Not Available'})[:2]
	else:
		develp = {'Data Not Available'}
	
	mf = list(actor_d['filmography'][0].keys())[0] 

	if mf == 'actor':
		image =  actor_d.get('full-size headshot', "/static/image/default_actor_M.jpg")
	elif mf == 'actress':
		image =  actor_d.get('full-size headshot', "/static/image/default_actor_F.jpg")
	else:
		image =  actor_d.get('full-size headshot', "/static/image/default_actor_M.jpg")


	d = {'id': actor, 
	'name': actor_d.get('name',actor) , 
	'nickN' : nickN  ,
	'image': image, 
	'birthPlace' : birth ,
	'bdate':  actor_d.get('birth date','Data Not Available'),
	'films': actor_d['filmography'][0][mf],
	'biography': actor_d.get('mini biography',{'Data Not Available'}) ,
	'tradeMark' :  actor_d.get('trade mark',{'Data not Available'}),
	'imdb':'https://www.imdb.com/name/nm'+ actor +'/',
	'develp' : develp,
	'salary': actor_d.get('salary history',{'Data Not Available'})
	}

	return render_template("actor_details.html", actor = d)

@app.route('/top12')
def top12():
	top = moviesDB.get_top250_movies()[0:12]

	head = 'Top 12 movies of 250 all time'

	data = []

	for movie in top:
		id = movie.movieID
		title = movie.get('title'," ")
		image =  movie_url(id)
		year =  movie.get('year', " ")
		rating = movie.get('rating', "N/A")
		rank = movie.get('top 250 rank',"N/A")

		d = {'id': id, 'title': title, 'image': image, 'year': year, 'rank' : rank,'rating': rating}

		data.append(d)
	
	return render_template("top12_movies.html", movie = data, head = head)

@app.route('/top12/<movie>')
def top12_movie_details(movie):
	print('under movie section top12',movie)
	movie_d = moviesDB.get_movie(movie)

	if 'box office' in movie_d.keys():
		budget = movie_d['box office'].get('Budget','Data Not Available')
		boxoffice = movie_d['box office'].get('Cumulative Worldwide Gross','Data Not Available')
	else:
		budget = 'Data Not Available'
		boxoffice = 'Data Not Available'

	if 'directors' in movie_d.keys():
		directors = movie_d['directors']
	elif 'writer' in movie_d.keys():
		directors =  movie_d['writer']
	else:
		directors = moviesDB.get_movie('4154796')['directors']

	if 'cast' in movie_d.keys():
		cast = movie_d['cast'][0:10]
	else:
		cast = moviesDB.get_movie('4154796')['cast'][0:1]

	d = {'id': movie, 
	'title': movie_d['title'], 
	'image': movie_d.get('full-size cover url', "static/image/default_movie.jpg"), 
	'year': str(movie_d.get('year',' ')),
	'cast':cast ,
	'genres':movie_d['genres'],
	'runtime': movie_d.get('runtime','Data Not Available'),
	'budget': budget,
	'boxoffice': boxoffice,
	'rating': movie_d.get('rating','Data Not Available'),
	'votes': movie_d.get('votes','Data Not Available'),
	'directors': directors,
	'lang': movie_d.get('languages',{'Data Not Available'}),
	'plot': movie_d.get('plot',{'Data Not Available'}),
	'imdb':'https://www.imdb.com/title/tt'+ movie +'/'
	}

	return render_template("movie_details.html", movie = d)

@app.route('/bottom12')
def bot12():
	top = moviesDB.get_top250_movies()[-12:]
	head = 'Last 12 movies of 250 all time'
	data = []
	
	for movie in top:
		id = movie.movieID
		title = movie.get('title'," ")
		image =  movie_url(id)
		year =  movie.get('year', " ")
		rating = movie.get('rating', "N/A")
		rank = movie.get('top 250 rank',"N/A")

		d = {'id': id, 'title': title, 'image': image, 'year': year, 'rank' : rank,'rating': rating}

		data.append(d)
	
	return render_template("bot12_movies.html", movie = data, head = head)

@app.route('/bottom12/<movie>')
def bot12_movie_details(movie):

	movie_d = moviesDB.get_movie(movie)

	if 'box office' in movie_d.keys():
		budget = movie_d['box office'].get('Budget','Data Not Available')
		boxoffice = movie_d['box office'].get('Cumulative Worldwide Gross','Data Not Available')
	else:
		budget = 'Data Not Available'
		boxoffice = 'Data Not Available'

	if 'directors' in movie_d.keys():
		directors = movie_d['directors']
	elif 'writer' in movie_d.keys():
		directors =  movie_d['writer']
	else:
		directors = moviesDB.get_movie('4154796')['directors']

	if 'cast' in movie_d.keys():
		cast = movie_d['cast'][0:10]
	else:
		cast = moviesDB.get_movie('4154796')['cast'][0:1]

	d = {'id': movie, 
	'title': movie_d['title'], 
	'image': movie_d.get('full-size cover url', "static/image/default_movie.jpg"), 
	'year': str(movie_d.get('year',' ')),
	'cast':cast ,
	'genres':movie_d['genres'],
	'runtime': movie_d.get('runtime','Data Not Available'),
	'budget': budget,
	'boxoffice': boxoffice,
	'rating': movie_d.get('rating','Data Not Available'),
	'votes': movie_d.get('votes','Data Not Available'),
	'directors': directors,
	'lang': movie_d.get('languages',{'Data Not Available'}),
	'plot': movie_d.get('plot',{'Data Not Available'}),
	'imdb':'https://www.imdb.com/title/tt'+ movie +'/'
	}

	return render_template("movie_details.html", movie = d)

if __name__ == '__main__':
    app.run(debug=True)

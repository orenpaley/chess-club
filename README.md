
## Chess Club 
#### Springboard Captsone 1 Project
##### written by Oren Paley 2022

##### Chess Club is an app to share and post chess games with other chess enthusiasts. 

##### This app was built with Flask, Python, PostgresSQL, HTML, CSS, and Bootstrap

#### Visit Live Site -
#### [chessbyte.herokuapp.com/](https://chessbyte.herokuapp.com/)

##### This site features an API endpoint from chess.com - details at this link:

https://www.chess.com/news/view/published-data-api#pubapi-endpoint-games

### Features

- post a game (pgn format)
- search for chess.com user month and year and set offset/limit to search user's monthly game archives and post one of their games
- like a game / unlike a game 
- tag a game with a unique tag or with a tag it has already been given
- homepage sorting
- profile, saved games, profile image
- login auth. w/ bcrypt
- html board viewer courtesy of Chesstempo.com

### Flow

##### 1) Register an account with secure password auth.

![Register Demo](https://github.com/orenpaley/chessbyte/blob/main/static/images/1RegisterDemo.png)

##### 2) See other game posts from other users. Sort, like, tag, post. 

![Home Demo](https://github.com/orenpaley/chessbyte/blob/main/static/images/2Home.png)

##### 3) Find Games using external API search from chess.com. Set username, year, month, offset and limit
![Find Games Demo](https://github.com/orenpaley/chessbyte/blob/main/static/images/3FindGames.png)

##### 4) Select a Game from retrieved list

![Select Game Demo](https://github.com/orenpaley/chessbyte/blob/main/static/images/4SelectGame.png)

##### 5) Add title and post the pgn

![Game Form Demo](https://github.com/orenpaley/chessbyte/blob/main/static/images/5GameForm.png)

##### 6) Tag your post with as many tags as you like. 

![Game Tags Demo](https://github.com/orenpaley/chessbyte/blob/main/static/images/6GameTags.png)

##### 7) Sort by Newest and see your post live on chessbyte

![View Added Game and Sort Demo](https://github.com/orenpaley/chessbyte/blob/main/static/images/7SortAndViewAddedGame.png)


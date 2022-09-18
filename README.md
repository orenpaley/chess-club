
## Chess Club 
#### Springboard Captsone 1 Project
##### written by Oren Paley 2022

##### Chess Club is an app to share and post chess games with other chess enthusiasts. 

##### This app was built with Flask, Python, PostgresSQL, HTML, CSS, and Bootstrap

#### Visit Live Site -
####[chessbyte.herokuapp.com/](https://chessbyte.herokuapp.com/)

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

##### 1) Register an account with secure pathword auth.
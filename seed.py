
from app import db
from models import User, Game, Tag, GameTag, GameTagLikes, Like

########################################
########################################
########################################
######### TABLE DELETION ################
########################################
########################################
########################################

def drop_everything():
    """(On a live db) drops all foreign key constraints before dropping all tables.
    Workaround for SQLAlchemy not doing DROP ## CASCADE for drop_all()
    (https://github.com/pallets/flask-sqlalchemy/issues/722)
    """
    from sqlalchemy.engine.reflection import Inspector
    from sqlalchemy.schema import DropConstraint, DropTable, MetaData, Table

    con = db.engine.connect()
    trans = con.begin()
    inspector = Inspector.from_engine(db.engine)

    # We need to re-create a minimal metadata with only the required things to
    # successfully emit drop constraints and tables commands for postgres (based
    # on the actual schema of the running instance)
    meta = MetaData()
    tables = []
    all_fkeys = []

    for table_name in inspector.get_table_names():
        fkeys = []

        for fkey in inspector.get_foreign_keys(table_name):
            if not fkey["name"]:
                continue

            fkeys.append(db.ForeignKeyConstraint((), (), name=fkey["name"]))

        tables.append(Table(table_name, meta, *fkeys))
        all_fkeys.extend(fkeys)

    for fkey in all_fkeys:
        con.execute(DropConstraint(fkey))

    for table in tables:
        con.execute(DropTable(table))

    trans.commit()

drop_everything()
db.create_all()

########################################
########################################
########################################
######### TABLE CREATION ################
########################################
########################################
########################################

user1 = User.signup(username='ivanchuk',
                    password='ivanchuk',
                    email='ivan@ivan.ivan', 
                    image_url='https://upload.wikimedia.org/wikipedia/commons/3/37/Vasyll_Ivanchuk1_Ukr_Ch_2014_%28cropped%29.jpg')
db.session.add(user1)
db.session.commit()

game1 = Game(user_id=user1.id, title='ivanchuk1', 
pgn='''[Event "Hoogovens Group A"]
[Site "Wijk aan Zee NED"]
[Date "1996.01.16"]
[EventDate "1996.01.13"]
[Round "3"]
[Result "1-0"]
[White "Vassily Ivanchuk"]
[Black "Alexey Shirov"]
[ECO "D44"]
[WhiteElo "?"]
[BlackElo "?"]
[PlyCount "69"]

1.d4 d5 2.c4 c6 3.Nc3 Nf6 4.Nf3 e6 5.Bg5 dxc4 6.e4 b5 7.e5 h6
8.Bh4 g5 9.Nxg5 hxg5 10.Bxg5 Nbd7 11.exf6 Bb7 12.g3 c5 13.d5
Qb6 14.Bg2 O-O-O 15.O-O b4 16.Na4 Qb5 17.a3 exd5 18.axb4 cxb4
19.Be3 Nc5 20.Qg4+ Rd7 21.Qg7 Bxg7 22.fxg7 Rg8 23.Nxc5 d4
24.Bxb7+ Rxb7 25.Nxb7 Qb6 26.Bxd4 Qxd4 27.Rfd1 Qxb2 28.Nd6+
Kb8 29.Rdb1 Qxg7 30.Rxb4+ Kc7 31.Ra6 Rb8 32.Rxa7+ Kxd6 33.Rxb8
Qg4 34.Rd8+ Kc6 35.Ra1 1-0
''')

game2 = Game(user_id=user1.id, title='ivanchuk2', 
pgn='''
[Event "Linares"]
[Site "Linares ESP"]
[Date "1991.02.23"]
[EventDate "1991.02.23"]
[Round "1"]
[Result "1-0"]
[White "Vassily Ivanchuk"]
[Black "Garry Kasparov"]
[ECO "B51"]
[WhiteElo "?"]
[BlackElo "?"]
[PlyCount "75"]

1.e4 c5 2.Nf3 d6 3.Bb5+ Nd7 4.d4 Nf6 5.O-O cxd4 6.Qxd4 a6
7.Bxd7+ Bxd7 8.Bg5 h6 9.Bxf6 gxf6 10.c4 e6 11.Nc3 Rc8 12.Kh1
h5 13.a4 h4 14.h3 Be7 15.b4 a5 16.b5 Qc7 17.Nd2 Qc5 18.Qd3 Rg8
19.Rae1 Qg5 20.Rg1 Qf4 21.Ref1 b6 22.Ne2 Qh6 23.c5 Rxc5 24.Nc4
Kf8 25.Nxb6 Be8 26.f4 f5 27.exf5 Rxf5 28.Rc1 Kg7 29.g4 Rc5
30.Rxc5 dxc5 31.Nc8 Bf8 32.Qd8 Qg6 33.f5 Qh6 34.g5 Qh5 35.Rg4
exf5 36.Nf4 Qh8 37.Qf6+ Kh7 38.Rxh4+ 1-0

''')
game3 = Game(user_id=user1.id, title='ivanchuk3', 
pgn='''
[Event "Chess Olympiad"]
[Site "Khanty-Mansiysk RUS"]
[Date "2010.09.28"]
[EventDate "2010.09.21"]
[Round "7"]
[Result "1-0"]
[White "Vassily Ivanchuk"]
[Black "Baadur Aleksandrovich Jobava"]
[ECO "B12"]
[WhiteElo "2754"]
[BlackElo "2710"]
[PlyCount "67"]

1. e4 c6 2. d4 d5 3. f3 Qb6 4. a3 e5 5. exd5 Nf6 6. dxe5 Bc5
7. exf6 Bf2+ 8. Ke2 O-O 9. Qd2 Re8+ 10. Kd1 Re1+ 11. Qxe1 Bxe1
12. Kxe1 Bf5 13. Be2 Nd7 14. dxc6 bxc6 15. Bd1 Re8+ 16. Ne2
Nxf6 17. Nc3 Bc8 18. a4 a5 19. Rf1 Ba6 20. Rf2 h5 21. Ra3 h4
22. g3 h3 23. g4 Rd8 24. Nf4 Nd7 25. Rb3 Qd4 26. Nfe2 Re8
27. Ne4 Qxa4 28. Bd2 Qa1 29. Bc3 Ne5 30. Ra3 Qb1 31. Nd2 Qc1
32. Rxa5 Ng6 33. Rxa6 Nf4 34. Ra8 1-0

''')\

game4 = Game(user_id=user1.id, title='ivanchuk4', 
pgn='''
[Event "Morelia-Linares"]
[Site "Morelia MEX"]
[Date "2007.02.18"]
[EventDate "2007.02.17"]
[Round "2"]
[Result "1-0"]
[White "Vassily Ivanchuk"]
[Black "Veselin Topalov"]
[ECO "B90"]
[WhiteElo "?"]
[BlackElo "?"]
[PlyCount "81"]

1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6 6.Be3 e5 7.Nf3
Be7 8.Bc4 O-O 9.O-O Be6 10.Bxe6 fxe6 11.Na4 Ng4 12.Qd3 Nxe3
13.Qxe3 b5 14.Nb6 Ra7 15.Nd5 Rb7 16.Qd2 Nc6 17.Rad1 Rd7 18.Qc3
Nb8 19.Nxe7+ Qxe7 20.Rd3 h6 21.Rfd1 Rfd8 22.h4 Kh7 23.R1d2 Qf8
24.Qb3 Qe8 25.a4 Qg6 26.axb5 axb5 27.Re3 Na6 28.Qxb5 Nc5
29.Qc4 Ra7 30.Re1 Qe8 31.b4 Na4 32.Qb3 Nb6 33.Red1 Rad7 34.Qd3
Rc8 35.c3 Ra7 36.Qe3 Ra6 37.Qe2 Nc4 38.Ra2 Rac6 39.Ra7 R6c7
40.Rda1 Qf7 41.Qxc4 1-0

''')

game5 = Game(user_id=user1.id, title='ivanchuk5', 
pgn='''
[Event "EU-ch U20"]
[Site "Groningen NED"]
[Date "1986.12.29"]
[EventDate "1986.12.18"]
[Round "10"]
[Result "0-1"]
[White "James Clifford Howell"]
[Black "Vassily Ivanchuk"]
[ECO "C42"]
[WhiteElo "?"]
[BlackElo "?"]
[PlyCount "68"]

1.e4 e5 2.Nf3 Nf6 3.Nxe5 d6 4.Nf3 Nxe4 5.d4 d5 6.Bd3 Nc6 7.O-O
Bg4 8.c4 Nf6 9.Nc3 Bxf3 10.Qxf3 Nxd4 11.Qe3+ Ne6 12.cxd5 Nxd5
13.Nxd5 Qxd5 14.Be4 Qb5 15.a4 Qa6 16.Rd1 Be7 17.Qf3 Rb8 18.b4
O-O 19.Rd7 Rbd8 20.Bxb7 Qc4 21.Rxd8 Rxd8 22.Be3 Qxb4 23.Be4
Bc5 24.Bxc5 Qxc5 25.h4 Qd4 26.Re1 Qxa4 27.h5 Ng5 28.Qf5 Nxe4
29.Rxe4 Qd1+ 30.Kh2 g6 31.hxg6 hxg6 32.Qg5 Rd5 33.Qf6 Qh5+
34.Rh4 Qxh4+ 0-1


''')

db.session.add(game1)
db.session.add(game2)
db.session.add(game3)
db.session.add(game4)
db.session.add(game5)
db.session.commit()

tag1 = Tag(name='sacrfice')
tag2 = Tag(name='miniature')
tag3 = Tag(name='checkmate')
tag4 = Tag(name='positional')
tag5 = Tag(name='tactical')
tag6 = Tag(name='fork')
tag7 = Tag(name='brilliancy')

db.session.add(tag1)
db.session.add(tag2)
db.session.add(tag3)
db.session.add(tag4)
db.session.add(tag5)
db.session.add(tag6)
db.session.add(tag7)
db.session.commit()

gt1 = GameTag(game_id=1,tag_id=1)
gt2 = GameTag(game_id=1,tag_id=2)
gt3 = GameTag(game_id=1,tag_id=5)
gt4 = GameTag(game_id=1,tag_id=7)
gt5 = GameTag(game_id=2,tag_id=2)
gt6 = GameTag(game_id=2,tag_id=3)
gt7 = GameTag(game_id=2,tag_id=5)
gt8 = GameTag(game_id=2,tag_id=6)
gt9 = GameTag(game_id=3,tag_id=1)
gt10 = GameTag(game_id=3,tag_id=2)
gt11 = GameTag(game_id=4,tag_id=5)

db.session.add(gt1)
db.session.add(gt2)
db.session.add(gt3)
db.session.add(gt4)
db.session.add(gt5)
db.session.add(gt6)
db.session.add(gt7)
db.session.add(gt8)
db.session.add(gt9)
db.session.add(gt10)
db.session.add(gt11)
db.session.commit()

gtl1 = GameTagLikes(game_tag_id=1, user_id=1)
gtl2 = GameTagLikes(game_tag_id=2, user_id=1)
gtl3 = GameTagLikes(game_tag_id=3, user_id=1)
gtl4 = GameTagLikes(game_tag_id=4, user_id=1)
gtl5 = GameTagLikes(game_tag_id=5, user_id=1)
gtl6 = GameTagLikes(game_tag_id=6, user_id=1)
gtl7 = GameTagLikes(game_tag_id=7, user_id=1)
gtl8 = GameTagLikes(game_tag_id=8, user_id=1)
gtl9 = GameTagLikes(game_tag_id=9, user_id=1)
gtl10 = GameTagLikes(game_tag_id=10, user_id=1)
gtl11 = GameTagLikes(game_tag_id=11, user_id=1)

db.session.add(gtl1)
db.session.add(gtl2)
db.session.add(gtl3)
db.session.add(gtl4)
db.session.add(gtl5)
db.session.add(gtl6)
db.session.add(gtl7)
db.session.add(gtl8)
db.session.add(gtl9)
db.session.add(gtl10)
db.session.add(gtl11)
db.session.commit()

like1 = Like(game_id=1,user_id=1)
like2 = Like(game_id=2,user_id=1)
like3 = Like(game_id=3,user_id=1)
like4 = Like(game_id=4,user_id=1)

db.session.add(like1)
db.session.add(like2)
db.session.add(like3)
db.session.add(like4)

db.session.commit()





from tinydb import TinyDB, Query
db = TinyDB('/Users/fmohammedibr/Desktop/sample.db.json')
db.insert({'int': 1, 'char': 'a'})
db.insert({'int': 1, 'char': 'b'})



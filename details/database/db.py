from tinydb import TinyDB, Query
from tinydb.database import Document

db1 = TinyDB('details/database/base.json', indent=4)
db2 = TinyDB('details/database/question.json', indent=4)

users     = db1.table("Users")

def get(table, user_id=None):
    if table == "users":
        if user_id == None:
            return users.all()
        else:
            return users.get(doc_id=user_id) 


def insert(table, data, user_id=None):

    if table == "users":
        try:
            doc = Document(
                value=data,
                doc_id=user_id
            )
            users.insert(doc)
            print("User bazaga qo'shildi ❗️")
        except:
            print("User bazada oldindan mavjud ❗️")

    elif table == "question":
        db2.insert(data)
        print("Savol bazaga qo'shildi ❗️")

def upd(table, data, user_id=None):

    if table == "users":
        users.update(data, doc_ids=[user_id])
        print("Users bazada mode yangilanishi ❗️")

    
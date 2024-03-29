from graphene import List,Field,Int,String,Float,ObjectType,InputObjectType

from app.db.models import ItemModel,ItemDetailModel
from app.db.database import Session


   
    

 
    
# class to fill data of respective item with there id.
class ItemDetailInput(InputObjectType):
    weight = String()
    unit = String()
    discount = Float()
    mrp = Float()
    quantity = Int()
    
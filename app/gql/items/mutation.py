from graphene import Int,String,List,Float,Mutation,ObjectType,Field

from app.db.models import ItemModel,ItemDetailModel
from app.db.database import Session

from app.gql.items.types import ItemDetailInput
from app.gql.types import ItemType
from app.utils import calculate_price

from sqlalchemy.orm import joinedload

from app.utils import admin_privaleges






# lets add class for item,
class AddProduct(Mutation):
    """
    add item to the database using this mutation
    """
    class Arguments:
        name = String()
        description = String()
        title = String()
        image_url = String()
        item_details = ItemDetailInput()
    
    status = String()
    status_code = Int()
    message = String()
    item_data = Field(lambda:ItemType)
    
    @staticmethod
    def mutate(root,info,
               name,
               description,
               title,
               image_url,
               item_details):
        
        admin_data = admin_privaleges(info.context,Session)
        
        if not admin_data:
            return AddProduct(
                status = "failed",
                status_code = 404,
                message = "faield to add banner."
            ) 
        try:
            with Session() as session:
                item = ItemModel(
                    name = name,
                    description = description,
                    title = title,
                    image_url = image_url,
                )
                
            # adding item_details to item table later because we need item id first for item_id in item_details table
            #lets first add and commit item.
            
                session.add(item)
                session.commit()
                
                product_details = ItemDetailModel(**item_details)
                product_details.item_id = item.id
                
                product_details.price = calculate_price(product_details.mrp,product_details.discount)
            
            #lets add item_details to item.
                item.item_details.append(product_details)
                
                session.add(item)
                session.commit()
                session.refresh(item)
            
            return AddProduct(
                status = "success",
                status_code = 201,
                message = "item has been added.",
                item_data = item
            )
         
        except:
            session.rollback()
            return AddProduct(
                status = "failed",
                status_code = 404,
                message = "item has not been added."
            )       
            
            
            
# lets update the item and item_details
class UpdateItem(Mutation):
    """
    update the item details by using this mutation
    """
    class Arguments:
        id = Int(required = True)
        name = String()
        description = String()
        title = String()
        image_url = String()
        weight = String()
        unit = String()
        quantity = Int()
        mrp = Float()
        discount = Float()
        
    status = String()
    status_code = Int()
    message = String()
    item_data = Field(lambda: ItemType)
    
    @staticmethod
    def mutate(root,info,
               id,
               name,
               description,
               title,
               image_url,
               weight,
               unit,
               discount,
               mrp,
               quantity):
        admin_data = admin_privaleges(info.context,Session)
        
        if not admin_data:
            return UpdateItem(
                status = "failed",
                status_code = 404,
                message = "faield to add banner."
            ) 
            
        try:
        
            with Session() as session:
                
                item = session.query(ItemModel).filter(ItemModel.id == id).first()
                
                if not item:
                    return UpdateItem(
                        status = "failed",
                        status_code = 403,
                        message = f"failed to find item with {id} in database."
                    )       
                
                if name:
                    item.name = name
                
                if description:
                    item.description = description
                
                if title:
                    item.title = title
                
                if image_url:
                    item.image_url = image_url
                    
                session.add(item)
                session.commit()
                
                item_details = session.query(ItemDetailModel).filter(ItemDetailModel.id == id).first()
                
                if not item_details:
                    return UpdateItem(
                        status = "failed",
                        status_code = 404,
                        message = f"failed to find item_deatail for item with {id}"
                    )
                
                if weight:
                    item_details.weight = weight
                
                
                if mrp:
                    item_details.mrp = mrp
                
                if discount:
                    item_details.discount = discount
                    
                if unit:
                    item_details.unit = unit
                
                if quantity:
                    item_details.quantity = quantity
                
                item_details.price = calculate_price(mrp,discount)
                
                session.add(item_details)
                session.commit()
                session.refresh(item_details)
            
            return UpdateItem(
                status = "success",
                status_code = 201,
                message = "item with {id} has been updated succesfully",
                item_data = item
            )
        except:
            session.rollback()
            return UpdateItem(
                status = "failed",
                status_code = 403,
                message = "failed to update the item."
            )
            
            
# lets delete item

class DeleteItem(Mutation):
    
    """
    delete the item by using this mutation.
    """
    class Arguments:
        id = Int(required = True)
        
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info,id):
        
        admin_data = admin_privaleges(info.context,Session)
        
        if not admin_data:
            return DeleteItem(
                status = "failed",
                status_code = 404,
                message = "faield to add banner."
            ) 
            
        try:
            with Session() as session:
                item = session.query(ItemModel).filter(ItemModel.id == id).first()
                
                if not item:
                    return DeleteItem(
                        status = "failed",
                        status_code = 404,
                        message = f"failed to find item with {id} in database."
                    )
                session.delete(item)
                session.commit()
                
            return DeleteItem(
                status = "success",
                status_code = 200,
                message = f"item with {id} has been deleted"
            )
        except:
            session.rollback()
            return DeleteItem(
                status = "failed",
                status_code = 403,
                message = f"failed to delete item with id {id}"
            )
            
# lets create mutation to delete all items from database.
class DeleteItems(Mutation):
    """
    delete all items by this mutation.
    """
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info):
        try:
            with Session() as session:
                items = session.query(ItemModel).all()

                session.delete(items)
                session.commit()
                
            return DeleteItems(
                status = "success",
                status_code = 200,
                message = "all items from database has been deleted."
            )
        except:
            return DeleteItems(
                status = "failed",
                status_code = 404,
                message = "failed to delete all items."
            )
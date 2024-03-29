from app.db.database import Session 
from app.db.models import BannerModel
from app.gql.banner.types import BannerOutpt


from graphene import Int,String,Field,ObjectType,Mutation

from app.utils import admin_privaleges,get_authenticated_admin



class AddBanner(Mutation):
    
    """
    Mutation to add Banner data to the database,
    with taking name and image_url as input from client.
    
    """
    class Arguments:
        name = String(required = True)
        image_url = String(required = True)
    
    output = Field(lambda: BannerOutpt)
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info,name,image_url):
        
        admin_data = admin_privaleges(info.context,Session)
        
        if not admin_data:
            return AddBanner(
                status = "failed",
                status_code = 404,
                message = "faield to add banner."
            ) 
        try:
            with Session() as session:
                banner = BannerModel(
                    name = name,
                    image_url = image_url
                )
                
                session.add(banner)
                session.commit()
                session.refresh(banner)
            return AddBanner(
                output = banner, status = "success", status_code = 201,message = "successfully added banner."
            )
        except:
            session.rollback()
            return AddBanner(
                status = "failed", status_code = 404, message = "failed to add banner data to database."
            )
            
class UpdateBanner(Mutation):
    
    """
    Mutation to update banner data,
    id is required to specify which banner to update,
    alongside id we are taking name and image_url but not
    mandatory.
    
    """
    class Arguments:
        id = Int(required = True)
        name = String()
        image_url = String()
    
    output = Field(lambda: BannerOutpt)
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info,id,name,image_url):
        
        admin_data = admin_privaleges(info.context,Session)
        
        if not admin_data:
            return UpdateBanner(
                status = "failed",
                status_code = 404,
                message = "faield to add banner."
            ) 
            
        try:
            with Session() as session:
                banner = session.query(BannerModel).filter(BannerModel.id == id).first()
                
                if not banner:
                    return BannerOutpt(
                        status = "failed",
                        status_code = 404,
                        message = "banner do not exist"
                    )
                if name:
                    banner.name = name
                else:
                    banner.name = banner.name
                    
                if image_url:
                    banner.image_url = image_url
                else:
                    banner.image_url = banner.image_url
                
                session.add(banner)
                session.commit()
                session.refresh(banner)
            return UpdateBanner(
                output = banner,
                status = "success",
                status_code = 201,
                message = f"banner with {id} has been updated."
            )
            
        except:
            session.rollback()
            return UpdateBanner(
                status = "failed",
                status_code = 404,
                message = "failed to update banner data"
            )



class DeleteBanner(Mutation):
    """
    Mutation to delete banner with id.
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
            return DeleteBanner(
                status = "failed",
                status_code = 404,
                message = "faield to add banner."
            ) 
        try:
            with Session() as session:
                banner = session.query(BannerModel).filter(BannerModel.id == id).first()
                
                if not banner:
                    return DeleteBanner(
                        status = "failed",
                        status_code = 404,
                        message = f" banner with {id} cant be found."
                    )
                session.delete(banner)
                session.commit()
            return DeleteBanner(
                status = "success",
                status_code = 200,
                message = f"banner with {id} has been deleted."
            )
        except:
            session.rollback()
            return DeleteBanner(
                status = "failed",
                status_code = 404,
                message = f"failed to"
            )
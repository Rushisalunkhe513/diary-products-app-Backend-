from graphene import Mutation,String,Int,List,Field,ObjectType

from app.db.database import Session
from app.db.models import UserObject,AdminModel,UserSession,AdminSession

from app.gql.users.types import UserInfo,AdminType
from app.utils import (password_hash,
                      validate_password,
                      gen_user_access_and_refresh_token,
                      get_authenticated_admin,
                      token_for_new_acc_ref_token,
                      add_tokens_to_user_session,
                      add_tokens_to_admin_session,
                      admin_privaleges,
                      store_otp,
                      verify_otp)

from app.db.blocklist import BlockList
from app.db.database import config

import random

from graphql import GraphQLError

import os
from datetime import datetime,timedelta

"""
now lets create 
    user_registration mutation,
    user_login mutation, 
    user_delete mutation,
    update_user_data muttaion.
"""


# user_registration mutation
class UserRegistartion(Mutation): # Mutation to say this is for adding,updating or for deleting.
    """
    Add user to the database by using this mutation
    """
    class Arguments:
        first_name = String(required = True)
        last_name = String(required = True)
        mobile_number = String(required = True)
        pin = String(required = True)
        land_mark = String(required = True)
        city = String(required = True)
        pincode = String(required = True)
        address = String(required = True)
    
    status = String()
    status_code = Int()
    message = String()
    user_output = Field(lambda:UserInfo)
    access_token = String()
    refresh_token = String()
    
    @staticmethod
    def mutate(root,info,
               first_name,
               last_name,
               mobile_number,
               pin,
               pincode,
               city,
               land_mark,
               address):
        try:
            with Session() as session:
                
                # lets check for user in database by mobile_number
                
                user = session.query(UserObject).filter(UserObject.mobile_number == mobile_number).first()
                
                if user:
                    return UserRegistartion(
                        status = "failed",
                        message = f"user with mobile_number {mobile_number} already exists. 'please Login !'",
                        status_code = 404
                    )
                else:
                    otp = random.randint(1000,9999)
                    store_otp(mobile_number,otp,config.r_client)
                    new_user = UserObject(
                        first_name = first_name,
                        last_name = last_name,
                        pin_hash = password_hash(pin),
                        pincode = pincode,
                        city = city,
                        land_mark = land_mark,
                        address = address,
                        mobile_number = mobile_number
                    )
                    
                    
                    session.add(new_user)
                    session.commit()
                    session.refresh(new_user)
                    
                    acc_exp_time = (datetime.now() + timedelta(hours=int(os.getenv("USER_EXP_ACCESS_TIME")))).isoformat()
                    ref_exp_time = (datetime.now() + timedelta(hours=int(os.getenv("USER_EXP_REF_TIME")))).isoformat()
                    
                    # genrating token and creating user session.
                    token_data = gen_user_access_and_refresh_token(new_user.id,new_user.mobile_number,acc_exp_time,ref_exp_time,role="user")
                    user_session = add_tokens_to_user_session(token_data["access_token"],token_data["refresh_token"],new_user.mobile_number,new_user.id,new_user.first_name,Session)
                
                if user_session:
                    return UserRegistartion(
                        status = "success",
                        status_code = 201,
                        message = "user has succesfully registred",
                        user_output = new_user,
                        access_token = token_data["access_token"],
                        refresh_token = token_data["refresh_token"]
                    )
        except:
            session.rollback()
            return UserRegistartion(
                status = "failed",
                status_code = 404,
                message = "user has failed to register"
            )
            
class UserLogin(Mutation):
    
    """
    make user login by this mutation.
    """
    class Arguments:
        mobile_number = String(required=True)
        pin = String(required=True)
        otp = Int(required = True)
        
    status = String()
    message = String()
    status_code = Int()
    access_token = String()
    refresh_token = String()
    
    @staticmethod
    def mutate(root, info, mobile_number, pin,otp):
        try:
            with Session() as session:
                user = session.query(UserObject).filter(UserObject.mobile_number == mobile_number).first()
                    
                if not user:
                    return UserLogin(
                        status="failed",
                        status_code=401,
                        message="User does not exist, please register first to proceed."
                    )
                
                verify_user = validate_password(user.pin_hash, pin)
                
                # verifying otp from user at user login
                verify_otp_data = verify_otp(mobile_number,otp,config.r_client)
                
                if verify_user and verify_otp_data:
                    
                    # now user is verified then lets gen access and refresh tokens.
                    acc_exp_time = (datetime.now() + timedelta(hours=int(os.getenv("USER_EXP_ACCESS_TIME")))).isoformat()
                    ref_exp_time = (datetime.now() + timedelta(hours=int(os.getenv("USER_EXP_REF_TIME")))).isoformat()
                
                    # genrating token and creating user session.
                    token_data = gen_user_access_and_refresh_token(user.id,user.mobile_number,acc_exp_time,ref_exp_time,role="user")
                    user_session = add_tokens_to_user_session(token_data["access_token"],token_data["refresh_token"],user.mobile_number,user.id,user.first_name,Session)
                    
                    if user_session:
                        return UserLogin(
                            status="success",
                            status_code=200,
                            message="User has successfully logged in.",
                            access_token = token_data["access_token"],
                            refresh_token = token_data["refresh_token"]
                        )
        except:
                return UserLogin(
                    status="failed",
                    status_code=401,
                    message="Entered mobile number or pin is not valid. Please ensure provided mobile number and pin are correct."
                )  
                    
class ForgetPin(Mutation):
    """
    reset forgetted pin by this mutation.
    """
    class Arguments:
        mobile_number = String(required = True)
        new_pin = String(required = True)
        re_enter_pin = String(required = True)
    
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info,
               mobile_number,
               new_pin,
               re_enter_pin
               ):
        try:
            with Session() as session:
                # lets see user with mobile_number is in database.
                
                user = session.query(UserObject).filter(UserObject.mobile_number == mobile_number).first()
                
                if not user:
                    return ForgetPin(
                        status = "failed",
                        status_code = 404,
                        message = "user do not exist. Please register yourself First."
                    )
                
                elif user and new_pin != re_enter_pin:
                    return ForgetPin(
                        status = "failed",
                        status_code = 404,
                        message = "new_pin and re_entred pin do not match."
                    )
                else:
                    user.pin_hash = password_hash(new_pin)
                    session.add(user)
                    session.commit()
                    session.refresh(user)
            
            return ForgetPin(
                status = "success",
                status_code = 201,
                message = "your pin has been reset"
            )
        except:
            session.rollback()
            return ForgetPin(
                status = "failed",
                status_code = 404,
                message = "failed to update user pin."
            )                       
                
                
# class for updating user details
class UpdateUserDetails(Mutation):
    """
    Mutation for updating the User Details.
    """   
    class Arguments:
        first_name = String()
        last_name = String()
        mobile_number = String()
        pin = String()
        land_mark = String()
        city = String()
        pincode = String()
        address = String()
    
    status = String()
    status_code = Int()
    message = String()
    user_data = Field(lambda:UserInfo)
    
    @staticmethod
    def mutate(root,info,
               first_name,
               last_name,
               mobile_number,
               pin,
               pincode,
               city,
               land_mark,
               address):
        
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return UpdateUserDetails(
                status = "failed",
                status_code = 404,
                message = "failed to find user"
            )
            
        try:
                
            with Session() as session:  
                
                if first_name:
                    user.first_name = first_name
                
                if last_name:
                    user.last_name = last_name
                
                if mobile_number:
                    user.mobile_number = mobile_number
                    
                if pin:
                    user.pin_hash = password_hash(pin)
                
                if pincode:
                    user.pincode = pincode
                
                if city:
                    user.city = city
                    
                if land_mark:
                    user.land_mark = land_mark
                    
                if address:
                    user.address = address
                    
                # now lets add updated iser data to database.
                
                session.add(user)
                session.commit()
                session.refresh(user)
            
            return UpdateUserDetails(
                status = "success",
                status_code = 201,
                message = f"user with id has been updated.",
                user_data = user
            )
        except:
            session.rollback()
            
            return UpdateUserDetails(
                status = "failed",
                status_code = 404,
                message = "can not update user with id to database."
            ) 
                
                
        
# delete user 
class DeleteUser(Mutation):
    """
    Mutation to delete User from database.
    """
        
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info):
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return UpdateUserDetails(
                status = "failed",
                status_code = 404,
                message = "failed to find user"
            )
        try:
            with Session() as session:
    
                session.delete(user)
                session.commit()
                
            return DeleteUser(
                status = "success",
                status_code = 200,
                message = f"user with id {user_id} is succesully deleted."
            )
        except:
            session.rollback()
            return DeleteUser(
                status = "failed",
                status_code = 404,
                message = "failed to delete user."
            )
            

# Mutation for admin_login
class AdminLogin(Mutation):
    """
    Mutation for admin login
    """
    class Arguments:
        mobile_number = String(required = True)
        pin = String(required =True)
    
    status = String()
    status_code = Int()
    message = String()
    access_token = String()
    refresh_token = String()
    
    @staticmethod
    def mutate(root,info,mobile_number,pin):
        
        
        try:
            with Session() as session:
                
                get_admin = session.query(AdminModel).filter(AdminModel.admin_mobile_number == mobile_number).first()
                
                if not get_admin:
                    return AdminLogin(
                        status = "failed",
                        status_code = 404,
                        message = "failed to find admin in database."
                    )
                
                if get_admin.admin_mobile_number == mobile_number and validate_password(get_admin.admin_pin_hash,pin):
                    
                
                    acc_exp_time = (datetime.now() + timedelta(hours=int(os.getenv("ADMIN_EXP_ACCESS_TIME")))).isoformat()
                    ref_exp_time = (datetime.now() + timedelta(hours=int(os.getenv("ADMIN_EXP_REF_TIME")))).isoformat()
                        
                    # genrating token and creating user session.
                    token_data = gen_user_access_and_refresh_token(get_admin.id,get_admin.admin_mobile_number,acc_exp_time,ref_exp_time,role="admin")
                    token_to_session = add_tokens_to_admin_session(token_data["access_token"],token_data["refresh_token"],get_admin.admin_mobile_number,get_admin.id,get_admin.admin_name,Session)  

                    if token_to_session:
                        return AdminLogin(
                            status = "success",
                            status_code = 200,
                            message = "successfully logged in",
                            access_token = token_data["access_token"],
                            refresh_token = token_data["refresh_token"]
                        )
                
        except:
            session.rollback()
            return AdminLogin(
                status = "failed",
                status_code = 404,
                message = "failed to login"
            )
            
            
# Mutation for updating admin data
class UpdateAdminDetails(Mutation):
    """
    Mutation to update admin_details
    """
    class Arguments:
        admin_name = String()
        admin_mobile_number = String()
        
    status = String()
    status_code = Int()
    message = String()
    admin_details = Field(lambda:AdminType)
    
    @staticmethod
    def mutate(root,info,
               admin_name,
               admin_mobile_number):
        
        admin = admin_privaleges(info.context,Session)
        
        if not admin:
            return UpdateAdminDetails(
                status = "failed",
                status_code = 404,
                message = "admin not found in database."
                )
        try:
            with Session() as session:
                
                
                if admin_name:
                    admin.admin_name = admin_name
                
                if admin_mobile_number:
                    admin.admin_mobile_number = admin_mobile_number
                
                session.add(admin)
                session.commit()
                session.refresh(admin)
                
            return UpdateAdminDetails(
                status = "success",
                status_code = 201,
                message = "succesfully updated admin details."
            )
        except:
            session.rollback()
            return UpdateAdminDetails(
                status = "failed",
                status_code = 404,
                message = "failed to update admin details."
            )
            
    
# set pin again for user
class ResetPin(Mutation):
    """
    change the pin to new pin.
    """
    class Arguments:
        mobile_number = String(required = True)
        new_pin = String(required = True)
        reenter_pin = String(required = True)
        
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info,
            mobile_number,
            new_pin,
            reenter_pin):
        
        user = get_authenticated_admin(info.context,Session)
        if not user:
            return ResetPin(
                status = "failed",
                status_code = 404,
                message = "faield to find user in database."
            )
            
        try:
            with Session() as session:
                """
                look for user exist or not in database with mobile_number
                """
                
                if user.mobile_number == mobile_number and new_pin == reenter_pin:
                    user.pin_hash = password_hash(new_pin)
                    
                session.add(user)
                session.commit()
                session.refresh(user)
            
            return ResetPin(
                status = "success",
                status_code = 201,
                message = f"successfully updated pin."
            )
        except:
            session.rollback()
            return ResetPin(
                status = "failed",
                status_code = 404,
                message = "failed to change pin to new one."
            )
 
 
# reset admin pin           
class ResetAdminPin(Mutation):
    """
    change the Admin pin to new pin.
    """
    class Arguments:
        mobile_number = String(required = True)
        new_pin = String(required = True)
        reenter_pin = String(required = True)
        
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info,
            mobile_number,
            new_pin,
            reenter_pin):
        
        admin = admin_privaleges(info.context,Session)
        
        if not admin:
            return ResetAdminPin(
                status = "failed",
                status_code = 404,
                message = "failed to find admin in database."
            )
        
        try:
            with Session() as session:
                """
                look for user exist or not in database with mobile_number
                """
                
                if admin.admin_mobile_number == mobile_number and new_pin == reenter_pin:
                    admin.admin_pin_hash = password_hash(new_pin)
                    
                session.add(admin)
                session.commit()
                session.refresh(admin)
            
            return ResetPin(
                status = "success",
                status_code = 201,
                message = f"successfully updated pin."
            )
        except:
            session.rollback()
            return ResetPin(
                status = "failed",
                status_code = 404,
                message = "failed to change pin to new one."
            )
            

# get new token by refresh token for user and admin.
class RefreshToken(Mutation):
    """
    Mutation to genrate new access token and refresh token.
    we will get token from header rather than exposing it to response.
    """
        
    status = String()
    status_code = Int()
    message = String()
    access_token = String()
    refresh_token = String()
    
    @staticmethod
    def mutate(root,info):
        """
        lets get authenticated user and admin.
        """
        new_tokens = token_for_new_acc_ref_token(info.context,Session)
        if not new_tokens:
            return GraphQLError("user is not found")
        else:
            return RefreshToken(
                status = "success",
                status_code = 200,
                message = f"new token genrated and added to session.",
                access_token = new_tokens["access_token"],
                refresh_token = new_tokens["refresh_token"]
            )
            
        
        
    
    
# lets write user logout mutation
class Logout(Mutation):
    """
    Mutation for logout user/admin from system.
    """
    
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info): 
            
        user_admin = get_authenticated_admin(info.context,Session)
        
        if not user_admin:
            return Logout(
                status = "failed",
                status_code = 404,
                message = f"{user_admin}"
            )
        
        with Session() as session:
            # for user
            user = session.query(UserSession).filter(UserSession.user_id == user_admin.id and UserSession.token_holder_mobile_number == user_admin.mobile_number).first()
            if user:
                session.delete(user)
                session.commit()
            
            
            # for admin
            
            admin = session.query(AdminSession).filter(AdminSession.admin_id == user_admin.id and AdminSession.token_holder_mobile_number == user_admin.mobile_number).first()
            if admin:
                session.delete(admin)
                session.commit()
        if not user and  not admin:
            return Logout(
                status = "failed",
                status_code = 404,
                message = "token is not valid one."
            )
        
        else:
            return Logout(
                status = "success",
                status_code = 201,
                message = "user logged out succesfully."
            )
        
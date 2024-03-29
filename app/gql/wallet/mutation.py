from graphene import String,Int,DateTime,List,Field,Mutation,Float

from app.gql.wallet.types import WalletDetails,WalletDetailsInputType

from app.db.models import WalletModel,UserWalletTransactions
from app.db.database import Session

from datetime import datetime

from app.utils import genrate_wallet_id,get_authenticated_admin








# lets create wallet
class AddWallet(Mutation):
    """
    Mutation to add wallet.
    """
    class Arguments:
        wallet_details = WalletDetailsInputType()
    
    status = String()
    status_code = Int()
    message = String()
    wallet_output = Field(lambda: WalletDetails)
    
    @staticmethod
    def mutate(root,info,
               wallet_details):
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return AddWallet(
                status = "faield",
                status_code = 404,
                message = "failed to add wallet."
            )
            
        try:
            with Session() as session:
                
                wallet_id = genrate_wallet_id(wallet_details.user_name)
                wallet_data = WalletModel(
                    wallet_id = wallet_id,
                    balance = wallet_details.balance,
                    user_id = wallet_details.user_id,
                    user_name = wallet_details.user_name,
                    user_mobile_number = wallet_details.user_mobile_number,
                    created_at = datetime.now(),
                    # updated_at = datetime.now()
                )
                user_wallet_transaction = UserWalletTransactions(
                    user_id = wallet_details.user_id,
                    wallet_id = wallet_id,
                    updated_at = datetime.now(),
                    amount_change = f"+{wallet_details.balance}",
                    
                )
            
                session.add(user_wallet_transaction)           
                session.add(wallet_data)
                session.commit()
                session.refresh(wallet_data)
            return AddWallet(
                status = "success",
                status_code = 201,
                message = "wallet ades succesfully",
                wallet_output = wallet_data
            )
        except:
            session.rollback()
            
            return AddWallet(
                status = "failed",
                status_code = 404,
                message = "failed to add wallet."
            )
            

# lets update wallet details by UpdateWallet Mutation
class UpdateWalletDetails(Mutation):
    """
    Mutation to update wallet details.
    """
    class Arguments:
        wallet_id = Int()
        wallet_new_data = WalletDetailsInputType()
    
    status = String()
    status_code = Int()
    message = String()
    wallet_details = Field(lambda:WalletDetails)
    
    @staticmethod
    def mutate(root,info,
               wallet_id,
               wallet_new_data):
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return UpdateWalletDetails(
                status = "faield",
                status_code = 404,
                message = "failed to update wallet details."
            )
            
        try:
            with Session() as session:
                wallet_data = session.query(WalletModel).filter(WalletModel.user_id == user.id).first()
                
                if not wallet_data:
                    return UpdateWalletDetails(
                        status = "failed",
                        status_code = 404,
                        message = f"can not find wallet with id {wallet_id}."
                    )
                    
                if wallet_new_data:
                    wallet_data.user_id = wallet_new_data.user_id
                    wallet_data.user_name = wallet_new_data.user_name
                    wallet_data.user_mobile_number = wallet_new_data.user_mobile_number
                    
                session.add(wallet_data)
                session.commit()
                session.refresh(wallet_data)
            return UpdateWalletDetails(
                status = "success",
                status_code = 201,
                message = "wallet details has been updated.",
                wallet_details = wallet_data
            )
        except:
            session.rollback()
            
            return UpdateWalletDetails(
                status = "success",
                status_code = 404,
                message = "wallet_details has not been updated."
            )
                    
        
#Mutation for adding balance in wallet.
class AddBalance(Mutation):
    """
    Mutation to add balance to wallet.
    """
    class Arguments:
        wallet_id = String(required = True)
        balance = Float()
        
    status = String()
    status_code = Int()
    message = String()
    wallet_data = Field(lambda:WalletDetails)
    
    @staticmethod
    def mutate(root,info,wallet_id,balance):
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return AddBalance(
                status = "faield",
                status_code = 404,
                message = "failed to add balance."
            )
            
        try:
            with Session() as session:
                wallet = session.query(WalletModel).filter(WalletModel.user_id == user.id).first()
                
                if not wallet:
                    return AddBalance(
                        status = "failed",
                        status_code = 404,
                        message = f"failed to find wallet with id {wallet_id}"
                    )
                
                if balance:
                    wallet.balance +=balance
                
                # wallet.updated_at = datetime.now()
                # wallet_transaction = session.query(UserWalletTransactions).filter(UserWalletTransactions.wallet_id == wallet_id).first()
                wallet_transaction = UserWalletTransactions(
                    user_id = wallet.user_id,
                    wallet_id = wallet.wallet_id,
                    updated_at = datetime.now(),
                    amount_change = f"+{balance}"
                )
                
                session.add(wallet_transaction)
                session.add(wallet)
                session.commit()
                session.refresh(wallet)
            return AddBalance(
                status = "success",
                status_code = 201,
                message = "wallet balance has been updated.",
                wallet_data = wallet
            )
        except:
            session.rollback()
            
            return AddBalance(
                status = "failed",
                status_code = 404,
                message = "failed to ad balance to wallet"
            )
            
# mutation to delete wallet from database.
class DeleteWallet(Mutation):
    """
    Delete wallet by id
    """            
    class Arguments:
        wallet_id = Int()
        
    status = String()
    status_code = Int()
    message = String()
    
    @staticmethod
    def mutate(root,info,wallet_id):
        
        user = get_authenticated_admin(info.context,Session)
        
        if not user:
            return DeleteWallet(
                status = "faield",
                status_code = 404,
                message = "failed to delete wallet."
            )
            
        try:
            with Session() as session:
                wallet = session.query(WalletModel).filter(WalletModel.user_id == user.id).first()
                
                if not wallet:
                    return DeleteWallet(
                        status = "failed",
                        status_code = 404,
                        message = f"failed to find wallet with id {wallet_id}."
                    )
                session.delete(wallet)
                session.commit()
            return DeleteWallet(
                status = "success",
                status_code = 200,
                message = f"wallet with id {wallet_id} is sucesfully deleted."
            )
        except:
            session.rollback()
            
            return DeleteWallet(
                status = "failed",
                status_code = 404,
                message = f"failed to find wallet with id {wallet_id} in database."
            )
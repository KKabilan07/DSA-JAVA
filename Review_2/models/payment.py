# models/payment.py

from bson.objectid import ObjectId
import datetime

class Payment:
    def __init__(self, member_id, amount, date=None, status="Pending"):
        """
        Initialize a new Payment instance.
        
        :param member_id: The ID of the member making the payment.
        :param amount: The payment amount.
        :param date: The payment date (defaults to current datetime if not provided).
        :param status: Payment status (default is "Pending").
        """
        self.member_id = member_id
        self.amount = amount
        self.date = date if date is not None else datetime.datetime.now()
        self.status = status

    def to_dict(self):
        """
        Convert the Payment instance into a dictionary for MongoDB insertion.
        """
        return {
            "member_id": self.member_id,
            "amount": self.amount,
            "date": self.date,
            "status": self.status
        }

    def save(self, db):
        """
        Save this payment record to the database.
        
        :param db: The MongoDB database connection (e.g., mongo.db)
        """
        db.payments.insert_one(self.to_dict())

    @staticmethod
    def get_all(db):
        """
        Retrieve all payment records from the database.
        
        :param db: The MongoDB database connection
        :return: List of payment documents
        """
        return list(db.payments.find())

    @staticmethod
    def update_payment(db, payment_id, updated_data):
        """
        Update a payment record in the database.
        
        :param db: The MongoDB database connection
        :param payment_id: The ObjectId (as string) of the payment to update.
        :param updated_data: Dictionary with updated fields.
        """
        db.payments.update_one({"_id": ObjectId(payment_id)}, {"$set": updated_data})

    @staticmethod
    def delete_payment(db, payment_id):
        """
        Delete a payment record from the database.
        
        :param db: The MongoDB database connection
        :param payment_id: The ObjectId (as string) of the payment to delete.
        """
        db.payments.delete_one({"_id": ObjectId(payment_id)})

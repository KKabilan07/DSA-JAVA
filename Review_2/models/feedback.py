# models/feedback.py

from bson.objectid import ObjectId
import datetime

class Feedback:
    def __init__(self, member_id, message, date=None):
        """
        Initialize a new Feedback instance.
        
        :param member_id: The ID of the member providing feedback.
        :param message: The feedback message.
        :param date: The feedback date (defaults to current datetime if not provided).
        """
        self.member_id = member_id
        self.message = message
        self.date = date if date is not None else datetime.datetime.now()

    def to_dict(self):
        """
        Convert the Feedback instance into a dictionary for MongoDB insertion.
        """
        return {
            "member_id": self.member_id,
            "message": self.message,
            "date": self.date
        }

    def save(self, db):
        """
        Save this feedback record to the database.
        
        :param db: The MongoDB database connection (e.g., mongo.db)
        """
        db.feedback.insert_one(self.to_dict())

    @staticmethod
    def get_all(db):
        """
        Retrieve all feedback records from the database.
        
        :param db: The MongoDB database connection.
        :return: List of feedback documents.
        """
        return list(db.feedback.find())

    @staticmethod
    def update_feedback(db, feedback_id, updated_data):
        """
        Update a feedback record in the database.
        
        :param db: The MongoDB database connection.
        :param feedback_id: The ObjectId (as string) of the feedback to update.
        :param updated_data: Dictionary with updated fields.
        """
        db.feedback.update_one({"_id": ObjectId(feedback_id)}, {"$set": updated_data})

    @staticmethod
    def delete_feedback(db, feedback_id):
        """
        Delete a feedback record from the database.
        
        :param db: The MongoDB database connection.
        :param feedback_id: The ObjectId (as string) of the feedback to delete.
        """
        db.feedback.delete_one({"_id": ObjectId(feedback_id)})

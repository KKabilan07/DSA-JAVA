# models/workout.py

from bson.objectid import ObjectId
import datetime

class Workout:
    def __init__(self, member_id, workout_plan, schedule, date=None):
        """
        Initialize a new Workout instance.
        
        :param member_id: The ID of the member for whom the workout is assigned.
        :param workout_plan: The workout plan description.
        :param schedule: The scheduled days or times for the workout.
        :param date: (Optional) The date when the workout was created. Defaults to current datetime.
        """
        self.member_id = member_id
        self.workout_plan = workout_plan
        self.schedule = schedule
        self.date = date if date is not None else datetime.datetime.now()

    def to_dict(self):
        """
        Convert the Workout instance to a dictionary for database insertion.
        """
        return {
            'member_id': self.member_id,
            'workout_plan': self.workout_plan,
            'schedule': self.schedule,
            'date': self.date
        }

    def save(self, db):
        """
        Save this workout record to the database.
        
        :param db: The MongoDB database connection (e.g., mongo.db)
        """
        db.workouts.insert_one(self.to_dict())

    @staticmethod
    def get_all(db):
        """
        Retrieve all workout records from the database.
        
        :param db: The MongoDB database connection
        :return: List of workout documents
        """
        return list(db.workouts.find())

    @staticmethod
    def update_workout(db, workout_id, updated_data):
        """
        Update a workout record in the database.
        
        :param db: The MongoDB database connection
        :param workout_id: The ObjectId (as string) of the workout to update.
        :param updated_data: Dictionary with updated fields.
        """
        db.workouts.update_one({'_id': ObjectId(workout_id)}, {'$set': updated_data})

    @staticmethod
    def delete_workout(db, workout_id):
        """
        Delete a workout record from the database.
        
        :param db: The MongoDB database connection
        :param workout_id: The ObjectId (as string) of the workout to delete.
        """
        db.workouts.delete_one({'_id': ObjectId(workout_id)})

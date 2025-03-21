# models/equipments.py

from bson.objectid import ObjectId

class Equipment:
    def __init__(self, name, equipment_type, available, maintenance_date):
        """
        Initialize a new Equipment instance.
        
        :param name: Name of the equipment.
        :param equipment_type: Type or category of the equipment.
        :param available: Boolean indicating if the equipment is available.
        :param maintenance_date: Date (as a string or datetime) for the next maintenance.
        """
        self.name = name
        self.equipment_type = equipment_type
        self.available = available
        self.maintenance_date = maintenance_date

    def to_dict(self):
        """
        Convert the Equipment instance to a dictionary for database insertion.
        """
        return {
            'name': self.name,
            'type': self.equipment_type,
            'available': self.available,
            'maintenance_date': self.maintenance_date
        }

    def save(self, db):
        """
        Save this equipment record to the database.
        
        :param db: The database connection (e.g., mongo.db)
        """
        db.equipment.insert_one(self.to_dict())

    @staticmethod
    def get_all(db):
        """
        Retrieve all equipment records from the database.
        
        :param db: The database connection (e.g., mongo.db)
        :return: List of equipment documents.
        """
        return list(db.equipment.find())

    @staticmethod
    def update_equipment(db, equipment_id, updated_data):
        """
        Update an equipment record in the database.
        
        :param db: The database connection (e.g., mongo.db)
        :param equipment_id: The ObjectId (as string) of the equipment to update.
        :param updated_data: Dictionary with the updated fields.
        """
        db.equipment.update_one({'_id': ObjectId(equipment_id)}, {'$set': updated_data})

    @staticmethod
    def delete_equipment(db, equipment_id):
        """
        Delete an equipment record from the database.
        
        :param db: The database connection (e.g., mongo.db)
        :param equipment_id: The ObjectId (as string) of the equipment to delete.
        """
        db.equipment.delete_one({'_id': ObjectId(equipment_id)})

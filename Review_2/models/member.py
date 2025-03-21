# models/member.py

from bson.objectid import ObjectId

class Member:
    def __init__(self, name, age, membership_type, contact):
        self.name = name
        self.age = age
        self.membership_type = membership_type
        self.contact = contact

    def to_dict(self):
        return {
            'name': self.name,
            'age': self.age,
            'membership_type': self.membership_type,
            'contact': self.contact
        }

    def save(self, db):
        """Save this member to the database."""
        db.members.insert_one(self.to_dict())

    @staticmethod
    def get_all(db):
        """Retrieve all members from the database."""
        return list(db.members.find())
    @staticmethod
    def delete_member(db, member_id):
        db.members.delete_one({'_id': ObjectId(member_id)})

    

    @staticmethod
    def update_member(db, member_id, updated_data):
        """Update a member's data by ID."""
        db.members.update_one({'_id': ObjectId(member_id)}, {'$set': updated_data})

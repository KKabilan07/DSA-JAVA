from pymongo import MongoClient

class MemberManagement:
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = MongoClient("mongodb://localhost:27017/")  # Connect to MongoDB
        self.db = self.client["gym_management"]  # Database
        self.members = self.db["members"]  # Collection

    def add_member(self):
        """Add a new member to MongoDB"""
        name = input("Enter Member Name: ").strip()
        age = input("Enter Member Age: ").strip()
        membership_type = input("Enter Membership Type (Normal/Gold/Silver/Platinum): ").strip()

        if not name or not age.isdigit() or not membership_type:
            print("❌ Error: All fields are required, and age must be a number!\n")
            return

        age = int(age)
        member_id = self.members.count_documents({}) + 1  # Auto-generate member ID
        new_member = {
            "_id": member_id,
            "name": name,
            "age": age,
            "membership_type": membership_type
        }
        self.members.insert_one(new_member)  # Insert into MongoDB
        print(f"✅ Member {name} added successfully with ID: {member_id}\n")

    def update_member(self):
        """Update an existing member in MongoDB"""
        member_id = input("Enter Member ID to update: ")

        if not member_id.isdigit():
            print("❌ Error: Member ID must be a number!\n")
            return

        member_id = int(member_id)
        member = self.members.find_one({"_id": member_id})

        if not member:
            print("❌ Member not found!\n")
            return

        print(f"Current Data: {member}")

        name = input("Enter New Name (Leave blank to keep unchanged): ").strip()
        age = input("Enter New Age (Leave blank to keep unchanged): ").strip()
        membership_type = input("Enter New Membership Type (Leave blank to keep unchanged): ").strip()

        update_data = {}
        if name:
            update_data["name"] = name
        if age.isdigit():
            update_data["age"] = int(age)
        if membership_type:
            update_data["membership_type"] = membership_type

        if update_data:
            self.members.update_one({"_id": member_id}, {"$set": update_data})  # Update in MongoDB
            print(f"✅ Member {member_id} updated successfully.\n")

    def delete_member(self):
        """Delete a member from MongoDB"""
        member_id = input("Enter Member ID to delete: ")

        if not member_id.isdigit():
            print("❌ Error: Member ID must be a number!\n")
            return

        member_id = int(member_id)
        result = self.members.delete_one({"_id": member_id})  # Delete from MongoDB

        if result.deleted_count > 0:
            print(f"✅ Member {member_id} deleted successfully.\n")
        else:
            print("❌ Member not found!\n")

    def search_member(self):
        """Search for a member in MongoDB"""
        member_id = input("Enter Member ID to search: ")

        if not member_id.isdigit():
            print("❌ Error: Member ID must be a number!\n")
            return

        member_id = int(member_id)
        member = self.members.find_one({"_id": member_id})

        if member:
            print(f"✅ Member Found: {member}\n")
        else:
            print("❌ Member not found!\n")

    def display_all_members(self):
        """Display all members from MongoDB"""
        members = self.members.find()
        members_list = list(members)

        if not members_list:
            print("❌ No members registered in the system.\n")
        else:
            print("\n--- Gym Members List ---")
            for member in members_list:
                print(f"ID: {member['_id']}, Name: {member['name']}, Age: {member['age']}, Membership: {member['membership_type']}")
            print("------------------------\n")


# Menu-driven program
def main():
    system = MemberManagement()

    while True:
        print("\n GYM MEMBER MANAGEMENT SYSTEM")
        print("1. Add Member")
        print("2. Display All Members")
        print("3. Update Member")
        print("4. Delete Member")
        print("5. Search Member")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            system.add_member()
        elif choice == "2":
            system.display_all_members()
        elif choice == "3":
            system.update_member()
        elif choice == "4":
            system.delete_member()
        elif choice == "5":
            system.search_member()
        elif choice == "6":
            print("Exiting... Thank you!\n")
            break
        else:
            print("❌ Invalid choice! Please enter a number between 1-6.\n")


if __name__ == "__main__":
    main()

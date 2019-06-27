class Group:
    """
    A class that holds messages and information of members in a group
    Jason Yu/Sunny Yan/Abdur (DB methods)
    """

    def __init__(self, app, data):
        self.app = app
        self.id = data["group_id"]
        self.name = data["name"]
        self.members = data["members"]
        self.owner = data["owner_id"]
        self.messages = data["messages"]

    @classmethod
    def from_db(cls, app, group_id):
        document = app.db.groups.find_one({"_id": group_id})
        return cls(app, document)

    def invite_person(self, person):
        self.members.append(person)

    def invite_people(self, people):
        for person in people:
            self.invite_person(person)

    def __iter__(self):
        return zip(vars(self).keys(), vars(self).values())

    def to_dict(self):
        return vars(self)

    def update_db(self):
        self.app.db.groups.update_one({"_id": self.id}, {"$set": self.__dict__})

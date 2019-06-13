from .utils import run_with_ngrok, snowflake, parse_snowflake
import datetime

class Group:
    """
    A class that holds messages and information of members in a group
    Jason Yu/Sunny Yan/Abdur (DB methods)
    """
    def __init__(self, app, data):
        self.app = app
        self.id = data['group_id']
        self.name = data['name']
        self.members = data['members']
        self.owner = data['owner_id']
        self.messages = data['messages']
	
    @classmethod
    def from_db(cls, app, group_id):
        document = app.db.groups.find_one({'_id':group_id})
        return cls(app,document)

    def invite_person(self, person):
        self.members.append(person)

    def invite_people(self,people):
        for person in people:
            self.invite_person(person)

    def __iter__(self):
        return zip(vars(self).keys(),vars(self).values())

    def to_dict(self):
        return vars(self)

    def update_db(self):
        self.app.db.groups.update_one(
            {'_id': self.id},
            {'$set': self.__dict__}
        )

class Message:
    def __init__(self, id, author, group_id, content=None, image=None):
        self.id = id
        self.author = author
        self.group_id = group_id
        self.content = content
        self.image = image
    
    @property
    def created_at(self):
        return parse_snowflake(int(self.id))[0]

    def to_dict(self):
        return {
            '_id': self.id,
            'content': self.content,
            'image': self.image,
            'group_id': self.group_id,
            'created_at': self.created_at,
            'author': {
                "_id": self.author.id,
                "full_name": self.author.full_name,
                "username": self.author.username,
                "avatar_url": self.author.avatar_url
                }
        }

    @classmethod
    async def create(cls, app, user, data):
        message_id = snowflake()
        content = data.get('content')
        image = data.get('image')
        msg = cls(message_id, user, data['group_id'], content, image)
        

        data = msg.to_dict()
        data['created_at'] = datetime.utcfromtimestamp(data['created_at'])
        await app.db.messages.insert_one(data)
        return msg
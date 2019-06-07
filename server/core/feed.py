class Feed:
  def __init__(self, items):
    """
    Feed that grows from the back
    [] -> [1] -> [1,2] -> [1,3,5]
    """
    self.items = items

  def get_latest_ten(self):
    return self.get_items(0,10)
  
  def get_items(self, start, num_items):
    other_items = []
    current_index = start
    while current_index < len(self.items) and current_index < start + num_items:
      other_items.append(self.items[-1-current_index]) # Takes index from back no need to reverse list
      current_index += 1
    return other_items

  def add_item(self,user_id,saved_route_id):
    self.items.append(FeedItem(user_id,saved_route_id))

  def to_dict(self):
    return [feed_item.to_dict() for feed_item in self.items]

  @classmethod
  def from_data(cls,data):
    items = [FeedItem(**descriptor) for descriptor in data] # Descriptor is essentially to_dict()
    return cls(items)

class FeedItem:
  def __init__(self, user_id, saved_route_id):
    self.user_id = user_id
    self.saved_route_id = saved_route_id

  def to_dict(self):
    return {
      'user_id': self.user_id,
      'saved_route_id': self.saved_route_id,
    }
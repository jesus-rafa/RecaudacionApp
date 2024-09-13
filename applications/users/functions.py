def get_username(self):
    username = self.request.user.username

    return username

def get_id_user(self):
    id = self.request.user.id

    return id 

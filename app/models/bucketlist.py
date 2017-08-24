from app.models.baseModel import BaseModel, db


class Bucketlist(BaseModel):
    '''This class represents the bucketlist model'''

    __table__name = 'bucketlist'

    name = db.Column(db.String(255), nullable=False)
    # items = db.relationship(
    #     'Item', cascade='all, delete', backref='bucketlist')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @staticmethod
    def get_all():
        '''get all bucketlist items'''
        return Bucketlist.query.all()

    def save_bucketlist(self):
        ''' Method to save user '''
        if not self.exists():
            self.save()
            return True
        return False

    def delete_bucketlist(self):
        ''' Method to delete user '''
        if self.exists():
            self.delete()
            return True
        return False

    def exists(self):
        ''' Check if bucketlist exists '''
        return True if Bucketlist.query.filter_by(name=self.name).first() else False

    def __repr__(self):
        return "<Bucketlist: {}>".format(self.name)

    def __str__(self):
        return '{0}'.format(self.name)

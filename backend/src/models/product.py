from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    product_id = Column(Text, primary_key=True)
    title = Column(Text)
    bullet_points = Column(Text)
    description = Column(Text)
    product_type_id = Column(Integer)
    product_length = Column(Float)
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'title': self.title,
            'bullet_points': self.bullet_points,
            'description': self.description,
            'product_type_id': self.product_type_id,
            'product_length': self.product_length
        }

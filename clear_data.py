# clear_data.py
from app import db, Comment, Menu, app

with app.app_context():
    # Tüm yorumları sil
    deleted_comments = Comment.query.delete()
    
    # Tüm menüleri sil
    deleted_menus = Menu.query.delete()
    
    db.session.commit()
    
    print(f"{deleted_comments} yorum, {deleted_menus} menü silindi.")

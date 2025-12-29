#!/usr/bin/env python3
# server/seed.py
from faker import Faker # type: ignore
import random
from app import app
from models import db, Newsletter, User

with app.app_context():
    fake = Faker()
    print("Clearing DB...")
    Newsletter.query.delete()
    User.query.delete()

    print("Seeding Users...")
    users = [User(username=fake.user_name()) for _ in range(10)]
    db.session.add_all(users)
    db.session.commit()

    print("Seeding Newsletters...")
    for _ in range(50):
        n = Newsletter(
            title=fake.text(max_nb_chars=20),
            body=fake.paragraph(nb_sentences=5),
            user_id=random.choice(users).id
        )
        db.session.add(n)
    
    db.session.commit()
    print("Done!")
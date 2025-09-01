import datetime
import uuid
import json
from typing import List, Dict
from sqlalchemy import select, insert

from database import Session, scheduled_posts_table
from models.data_models import ScheduledPost

class CalendarModel:
    def add_post(self, post: ScheduledPost):
        """Adds a new post to the schedule in the database."""
        with Session() as session:
            stmt = insert(scheduled_posts_table).values(
                id=post.id,
                date=post.date,
                content_type=post.content_type,
                content_data_json=json.dumps(post.content_data)
            )
            session.execute(stmt)
            session.commit()

    def get_posts_for_month(self, year: int, month: int) -> Dict[int, List[ScheduledPost]]:
        """Returns a dictionary mapping day numbers to a list of posts for that day from the database."""
        posts_by_day: Dict[int, List[ScheduledPost]] = {}
        with Session() as session:
            start_of_month = datetime.date(year, month, 1)
            if month == 12:
                end_of_month = datetime.date(year + 1, 1, 1)
            else:
                end_of_month = datetime.date(year, month + 1, 1)

            stmt = select(scheduled_posts_table).where(
                scheduled_posts_table.c.date >= start_of_month,
                scheduled_posts_table.c.date < end_of_month
            )
            results = session.execute(stmt).all()

            for row in results:
                post = ScheduledPost(
                    id=row.id,
                    date=row.date,
                    content_type=row.content_type,
                    content_data=json.loads(row.content_data_json)
                )
                if post.date.day not in posts_by_day:
                    posts_by_day[post.date.day] = []
                posts_by_day[post.date.day].append(post)
        return posts_by_day

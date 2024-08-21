from sqlalchemy import Column
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

DB_FILE = "sqlite:///./no_hide.db"
engine = create_engine(DB_FILE)
Session = sessionmaker(bind=engine)

class Post(Base):
    __tablename__ = 'POSTS'
    link = Column(String, primary_key=True)
    date = Column(DateTime)
    get_date = Column(DateTime, default=datetime.utcnow)

class Link(Base):
    __tablename__ = 'LINKS'
    link = Column(String, primary_key=True)
    post_link = Column(String, ForeignKey('POSTS.link'))
    save_mode = Column(String)
    author = Column(String)
    sort_date = Column(DateTime, default=datetime.utcnow)
    download_date = Column(DateTime, nullable=True)
    download_path = Column(String, nullable=True)
    post = relationship("Post", back_populates="links")

def insert_post(session, link, date):
    post = Post(link=link, date=date)
    session.add(post)
    session.commit()
    return True


def insert_link_to_db(session, post_info, link, save_mode):
    author, post_link = post_info
    new_link = Link(link=link, save_mode=save_mode, author=author, post_link=post_link)
    try:
        session.add(new_link)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False


def insert_links_to_db(session, post_info, links, save_mode):
    author, post_link = post_info
    new_links = [
        Link(link=link.get_attribute("href"), save_mode=save_mode, author=author, post_link=post_link)
        for link in links
    ]
    try:
        session.add_all(new_links)
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False

def all_items_in_list_in_db(session, links):
    links_set = set(links)
    result = session.query(Link).filter(Link.link.in_(links_set)).all()
    return links_set.issubset({row.link for row in result})


def get_links(session):
    return {row.link for row in session.query(Post.link).all()}


def get_not_down_links(session):
    return {row for row in session.query(Link).filter(Link.download_date.is_(None)).all()}


def update_download_info(session, link, download_date, download_path):
    session.query(Link).filter(Link.link == link).update({
        Link.download_date: download_date,
        Link.download_path: download_path
    })
    session.commit()

Base.metadata.create_all(engine)
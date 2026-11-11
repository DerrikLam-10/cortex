from sqlalchemy import Column, Integer, String, Text, ForeignKey   # tools to define columns + the foreign-key link
from sqlalchemy.orm import relationship                            # lets us hop between related tables in python

from .database import Base                                         # our own Base from database.py; every table inherits it

# each class below = one table.  python class = table, object = row, attribute = column


class Class(Base):                                      # the "classes" table
    __tablename__ = "classes"                           # its real name inside the database

    id = Column(Integer, primary_key=True, index=True)  # unique auto-numbered id for each row
    name = Column(String, nullable=False)               # class name, required (e.g. "Machine Learning")
    code = Column(String)                               # course code, optional (e.g. "CSE 142")

    # one class has many lectures; cascade = delete the class and its lectures go too
    lectures = relationship("Lecture", back_populates="course", cascade="all, delete-orphan")


class Lecture(Base):                                    # the "lectures" table
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)  # same id pattern as above
    title = Column(String, nullable=False)              # lecture title, required

    class_id = Column(Integer, ForeignKey("classes.id"))  # the real link: which class this lecture belongs to

    course = relationship("Class", back_populates="lectures")                                # hop up to the class
    topics = relationship("Topic", back_populates="lecture", cascade="all, delete-orphan")   # hop down to its topics


class Topic(Base):                                      # the "topics" table
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)  # id
    name = Column(String, nullable=False)               # topic name, required
    lesson = Column(Text)                               # the LLM-written explanation (Text = long text)

    lecture_id = Column(Integer, ForeignKey("lectures.id"))     # link up to its lecture
    lecture = relationship("Lecture", back_populates="topics")  # hop up to that lecture

    # one topic has many quiz questions
    questions = relationship("Question", back_populates="topic", cascade="all, delete-orphan")


class Question(Base):                                   # the "questions" table
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)  # id
    prompt = Column(Text, nullable=False)               # the question text, required
    choices = Column(Text)                              # the 4 options, stored as JSON text
    answer = Column(Integer)                            # index 0-3 of the correct choice
    explanation = Column(Text)                          # why that answer is right

    topic_id = Column(Integer, ForeignKey("topics.id"))        # link up to its topic
    topic = relationship("Topic", back_populates="questions")  # hop up to that topic
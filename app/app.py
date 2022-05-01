from flask import Flask, request, abort
import sqlalchemy as db
from sqlalchemy import create_engine, Column
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import desc
import json
import requests


# conn = create_engine('postgresql+psycopg2://postgres:postgres@localhost:7777')
# локально
conn = create_engine('postgresql+psycopg2://postgres:postgres@postgres:5432')
Base = declarative_base(bind=conn)
Session = sessionmaker(bind=conn)
session = Session()

app = Flask(__name__)


class Question(Base):
    __tablename__ = 'questions'
    id = Column(db.Integer, primary_key=True)
    id_q = Column(db.Integer, nullable=False)
    text_q = Column(db.String, nullable=False)
    text_a = Column(db.String, nullable=False)
    data_create = Column(db.String, nullable=False)


Base.metadata.create_all(bind=conn)


@app.route('/bewise', methods=['POST'])
def post_query():
    if not request.json:
        abort(400)
    data: dict = request.json
    quantity_q: int = data['questions_num']
    result = session.query(Question).order_by(desc(Question.id)).limit(quantity_q).all()
    query_questions = session.query(Question).all()
    query_questions_str = {i.text_q for i in query_questions}
    no_db_questions = []
    no_db_questions_str = set()
    while len(no_db_questions) < quantity_q:
        try:
            response = requests.get(f"https://jservice.io/api/random?count"
                                 f"={quantity_q}", timeout=10)
        except TimeoutError:
            continue
        for item in response.json():
            if item['question'] not in query_questions_str and item['question'] not in no_db_questions_str:
                no_db_questions.append(item)
                no_db_questions_str.add(item['question'])
    for item in no_db_questions:
        quest = Question(
            id_q=item['id'],
            text_q=item['question'],
            text_a=item['answer'],
            data_create=item['created_at']
        )
        session.add(quest)
    session.commit()
    result_dict = []
    for i in result:
        result_dict.append({
            'id': i.id,
            'question': i.text_q,
            'answer': i.text_a,
            'created_at': i.data_create
        })
    return json.dumps(result_dict)


app.run(host='0.0.0.0', port=7070, debug=True)

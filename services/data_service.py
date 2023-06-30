from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from model.sqlalchemy.Models import Account, Utente
import urllib

class DataService():
    
    db_server: str = None
    db_port: int = None
    db_user: str = None
    db_password: str = None
    db_name: str = None
    
    _engine: Engine = None    

    def __init__(self, db_server: str, db_port: int, db_user: str, db_password: str, db_name: str) -> None:

        self.db_server = db_server
        self.db_port = db_port
        self.db_user = db_user 
        self.db_password = db_password
        self.db_name = db_name

        self.dsn = f"mysql+mysqldb://{self.db_user}:{urllib.parse.quote(self.db_password)}@{self.db_server}:{str(self.db_port)}/{self.db_name}"

        self._engine = create_engine(url=self.dsn)


    def get_account_by_id(self, account_id) -> Account:

        with Session(self._engine) as session:
            res = session.query(Account).filter_by(id=account_id).one_or_none()
            if res is None:
                return None
            else:
                return res

    def get_company_by_id(self, company_id: int) -> Utente:

        with Session(self._engine) as session:
            res = session.query(Utente).options(joinedload('*')).filter_by(id=company_id).one_or_none()
            if res is None:
                return None
            else:
                return res
        
    
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Boolean, Integer, Text, DateTime, BigInteger

class Base(DeclarativeBase):
    pass


# association_table = Table(
#     "account_utenti",
#     Base.metadata,
#     Column("id_account", ForeignKey("account.id"), primary_key=True),
#     Column("id_utente", ForeignKey("utenti.id"), primary_key=True),
# )

class AccountUtentiAssociation(Base):
    __tablename__ = "account_utenti"
    id_account: Mapped[str] = mapped_column(ForeignKey("account.id"), primary_key=True)
    id_utente: Mapped[int] = mapped_column(ForeignKey("utenti.id"), primary_key=True)
    level: Mapped[str] = mapped_column(String(10), nullable=False, default="ADMIN")
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="WAIT_APPR")
    
    account: Mapped["Account"] = relationship(back_populates="companies")
    company: Mapped["Utente"] = relationship(back_populates="accounts")

class Account(Base):
    __tablename__ = "account"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(2048))
    ft_userid: Mapped[str] = mapped_column(String(2048))
    password: Mapped[str] = mapped_column(String(2048))
    is_active: Mapped[bool] = mapped_column(Boolean())
    is_admin: Mapped[bool] = mapped_column(Boolean())
    is_suspended: Mapped[bool] = mapped_column(Boolean())
    name: Mapped[str] = mapped_column(String(255))
    surname: Mapped[str] = mapped_column(DateTime())
    language: Mapped[str] = mapped_column(String(2))
    auth_code: Mapped[str] = mapped_column(DateTime(255))
    activated_at: Mapped[datetime] = mapped_column(DateTime(255))
    created_at: Mapped[datetime] = mapped_column(String(255))
    updated_at: Mapped[datetime] = mapped_column(String(255))

    companies: Mapped[List["AccountUtentiAssociation"]] = relationship(back_populates="account")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


class Utente(Base):
    __tablename__ = "utenti"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    tipo_utenti_id: Mapped[int] = mapped_column(Integer(), default=3)
    numero_accessi: Mapped[int] = mapped_column(Integer(), default=0)
    logo: Mapped[str] = mapped_column(Text(), default=None)
    riceve_richieste: Mapped[bool] = mapped_column(Boolean(), default=False)
    is_visible: Mapped[bool] = mapped_column(Boolean(), default=False)
    foto: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=None)
    has_logo: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=None)
    nome: Mapped[str] = mapped_column(Text(), default=None)
    indirizzo: Mapped[str] = mapped_column(Text(), default=None)
    cap: Mapped[str] = mapped_column(Text(), default=None)
    citta: Mapped[str] = mapped_column(Text(), default=None)
    nazioni_id: Mapped[int] = mapped_column(Integer(), default=3)
    email: Mapped[str] = mapped_column(Text(), nullable=False)
    telefono: Mapped[str] = mapped_column(Text(), default=None)
    fax: Mapped[str] = mapped_column(Text(), default=None)
    skype: Mapped[str] = mapped_column(Text(), default=None)
    sito_web: Mapped[str] = mapped_column(Text(), default=None)
    lingua: Mapped[str] = mapped_column(Text(), nullable=False)
    piva: Mapped[str] = mapped_column(Text(), default=None)
    nomerif: Mapped[str] = mapped_column(Text(), default=None)
    cognomerif: Mapped[str] = mapped_column(Text(), default=None)
    emailrif: Mapped[str] = mapped_column(Text(), default=None)
    telrif: Mapped[str] = mapped_column(Text(), default=None)
    faxrif: Mapped[str] = mapped_column(Text(), default=None)
    skyperif: Mapped[str] = mapped_column(Text(), default=None)
    nomerif2: Mapped[str] = mapped_column(Text(), default=None)
    cognomerif2: Mapped[str] = mapped_column(Text(), default=None)
    telrif2: Mapped[str] = mapped_column(Text(), default=None)
    faxrif2: Mapped[str] = mapped_column(Text(), default=None)
    emailrif2: Mapped[str] = mapped_column(Text(), default=None)
    skyperif2: Mapped[str] = mapped_column(Text(), default=None)
    visitno: Mapped[int] = mapped_column(Integer(), nullable=True, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=False)
    login: Mapped[str] = mapped_column(Text(), default=None)
    password: Mapped[str] = mapped_column(Text(), default=None)
    zona: Mapped[int] = mapped_column(Integer(), default=None)
    provincia: Mapped[str] = mapped_column(Text(), default=None)
    fatt_nome: Mapped[str] = mapped_column(Text(), default=None)
    fatt_indirizzo: Mapped[str] = mapped_column(Text(), default=None)
    fatt_cap: Mapped[str] = mapped_column(Text(), default=None)
    fatt_citta: Mapped[str] = mapped_column(Text(), default=None)
    fatt_provincia: Mapped[str] = mapped_column(Text(), default=None)
    fatt_nazione: Mapped[str] = mapped_column(Text(), default=None)
    fatt_piva: Mapped[str] = mapped_column(Text(), default=None)
    fatt_email: Mapped[str] = mapped_column(Text(), default=None)
    titolo: Mapped[str] = mapped_column(Text(), default=None)
    pagato: Mapped[bool] = mapped_column(Boolean(), default=False)
    scadenza: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    traduzioni: Mapped[bool] = mapped_column(Boolean(), nullable=True)
    sub_date: Mapped[datetime] = mapped_column(DateTime(), nullable=True)
    dipendenti: Mapped[int] = mapped_column(Text(), default=None)
    fatturato: Mapped[str] = mapped_column(Text(), default=None)
    inox: Mapped[bool] = mapped_column(Boolean(), default=None, nullable=True)
    temp: Mapped[bool] = mapped_column(Boolean(), default=None, nullable=True)
    log_counter: Mapped[int] = mapped_column(Integer(), default=None, nullable=True)
    reserved: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=None)    
    specialita_it: Mapped[str] = mapped_column(Text(), nullable=True, default=None)
    catspecia: Mapped[int] = mapped_column(Integer(), nullable=True, default=None)
    specialita_uk: Mapped[str] = mapped_column(Text(), nullable=True, default=None)
    specialita_de: Mapped[str] = mapped_column(Text(), nullable=True, default=None)
    specialita_fr: Mapped[str] = mapped_column(Text(), nullable=True, default=None)
    specialita_es: Mapped[str] = mapped_column(Text(), nullable=True, default=None)
    tablehtml: Mapped[str] = mapped_column(Text(), nullable=True, default=None)
    cat_machspecia: Mapped[int] = mapped_column(Integer(), nullable=True, default=None)
    catspecia2: Mapped[int] = mapped_column(Integer(), nullable=True, default=None)
    catspecia3: Mapped[int] = mapped_column(Integer(), nullable=True, default=None)
    ordinamento: Mapped[int] = mapped_column(Integer(), nullable=True, default=None)
    informazioni: Mapped[str] = mapped_column(Text(), nullable=True, default=None)
    riceve_richieste_generiche: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    lastmod: Mapped[datetime] = mapped_column(DateTime(), nullable=True, default=None)
    is_surplus_stock: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=False)
    is_base: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=False)
    contatti_extra: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    is_free: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=None)
    is_premium: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=None)
    contatti_extra_it: Mapped[str] = mapped_column(String(512), nullable=True, default=None)
    contatti_extra_uk: Mapped[str] = mapped_column(String(512), nullable=True, default=None)
    contatti_extra_de: Mapped[str] = mapped_column(String(512), nullable=True, default=None)
    auth_code: Mapped[str] = mapped_column(String(128), nullable=True, default=None)
    is_admin: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=None)
    video: Mapped[str] = mapped_column(Text(), nullable=True, default=None)
    certificazioni: Mapped[str] = mapped_column(Text(), nullable=True, default=None)
    bln_fotoprodottifull: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=None)
    bln_privacy_accettata: Mapped[bool] = mapped_column(Boolean(), nullable=True, default=True)
    utenti_registrazione_id: Mapped[int] = mapped_column(Integer(), nullable=True, default=1)
    activation_date: Mapped[datetime] = mapped_column(DateTime(), nullable=True, default=None)
    
    # Relationships 
    accounts: Mapped[List["AccountUtentiAssociation"]] = relationship(back_populates="company")



    def __repr__(self) -> str:
        return f"Azienda (id={self.id!r}, name={self.nome!r})"


class Nazione(Base):
    __tablename__ = "nazioni"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    subzoneof: Mapped[int] = mapped_column(Integer())
    zone_it: Mapped[str] = mapped_column(String(255))
    zone_de: Mapped[str] = mapped_column(String(255))
    zone_es: Mapped[str] = mapped_column(String(255))
    zone_uk: Mapped[str] = mapped_column(String(255))
    zone_fr: Mapped[str] = mapped_column(String(255))
    code: Mapped[str] = mapped_column(Text())
    loc: Mapped[str] = mapped_column(Text())

    def __repr__(self) -> str:
        return f"Country(id={self.id!r}, name={self.zone_it!r})"
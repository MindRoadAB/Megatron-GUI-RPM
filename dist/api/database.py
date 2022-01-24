from sqlalchemy import create_engine, insert, update, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import pathlib
import configparser


def get_connection_string():
    config = configparser.ConfigParser()
    script_path = pathlib.Path(__file__).parent.resolve()
    config.read(script_path / 'db.cfg')
    cfg = config['db']
    conn_str = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}?charset=utf8mb4'.format(
        cfg['user'],
        cfg['password'],
        cfg['host'],
        cfg['port'],
        cfg['database']
    )
    return conn_str


engine = create_engine(get_connection_string(), echo=False)
Base = declarative_base(engine)
Session = scoped_session(sessionmaker(bind=engine))


class Organization(Base):
    __tablename__ = 'organization'
    __table_args__ = {'autoload': True}


class ASN(Base):
    __tablename__ = 'asn'
    __table_args__ = {'autoload': True}


class Contact(Base):
    __tablename__ = 'contact'
    __table_args__ = {'autoload': True}


class DomainName(Base):
    __tablename__ = 'domain_name'
    __table_args__ = {'autoload': True}


class IpRange(Base):
    __tablename__ = 'ip_range'
    __table_args__ = {'autoload': True}


def thread_scoped_session(func):
    def inner(*args, **kwargs):
        Session()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            Session.rollback()
            raise e
        finally:
            Session.remove()
    return inner


def update_row(table, data):
    stmt = (
        update(table).
            where(table.id == data['id']).
            values(**data)
    )
    Session.execute(stmt)


def insert_row(table, data):
    stmt = (
        insert(table).values(**data)
    )
    Session.execute(stmt)
    return int(next(Session.execute("SELECT LAST_INSERT_ID()"))[0])


def delete_row(table, data):
    stmt = (
        delete(table).where(table.id == data['id'])
    )
    Session.execute(stmt)


def upsert(table, data, org_id):
    for d in data:
        d['org_id'] = org_id
    prev_q = Session.query(table) \
        .filter(table.org_id == org_id) \
        .all()
    prev_dict = {}
    for row in prev_q:
        prev_it = row2dict(row)
        prev_dict[prev_it['id']] = prev_it
    for item in data:
        if 'id' in item and item['id'] in prev_dict:
            update_row(table, item)
            del prev_dict[item['id']]
        else:
            insert_row(table, item)
    for del_it in prev_dict.values():
        delete_row(table, del_it)


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)
    return d


@thread_scoped_session
def add_organization(org_data):
    if 'id' in org_data:
        del org_data['id']
    org_id = insert_row(Organization, org_data)
    Session.commit()
    return get_organization(org_id)


@thread_scoped_session
def update_organization(org_id, org_data):
    organization = org_data['organization']
    organization['id'] = org_id
    update_row(Organization, organization)
    upsert(ASN, org_data['asn'], org_id)
    upsert(IpRange, org_data['ip_range'], org_id)
    upsert(Contact, org_data['contact'], org_id)
    upsert(DomainName, org_data['domain_name'], org_id)
    Session.commit()
    return get_organization(org_id)


@thread_scoped_session
def list_organizations():
    organizations = []
    for org_row in Session.query(Organization).all():
        organizations.append(row2dict(org_row))
    return organizations


@thread_scoped_session
def get_organization(org_id):
    def get_list(table, org_id):
        res = Session.query(table)\
                     .filter(table.org_id == org_id) \
                     .order_by(table.id) \
                     .all()
        res_l = []
        for row in res:
            row_dict = row2dict(row)
            del row_dict['org_id']
            res_l.append(row_dict)
        return res_l
    org_res = Session.query(Organization).get(org_id)
    organization = {
        'organization': row2dict(org_res),
        'asn': get_list(ASN, org_id),
        'contact': get_list(Contact, org_id),
        'domain_name': get_list(DomainName, org_id),
        'ip_range': get_list(IpRange, org_id)
    }
    return organization


@thread_scoped_session
def delete_organization(org_id):
    def delete_dependent(table, org_id):
        stmt = (
            delete(table).where(table.org_id == org_id)
        )
        Session.execute(stmt)
    delete_dependent(ASN, org_id)
    delete_dependent(Contact, org_id)
    delete_dependent(DomainName, org_id)
    delete_dependent(IpRange, org_id)
    delete_row(Organization, {'id': org_id})
    Session.commit()


@thread_scoped_session
def dump_table(table_name):
    table_rows = None
    for table in [ASN, Contact, DomainName, IpRange, Organization]:
        if table_name == table.__tablename__:
            table_rows = []
            for row in Session.query(table).order_by(table.id).all():
                table_rows.append(row2dict(row))
    return table_rows

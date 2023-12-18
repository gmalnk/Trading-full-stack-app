from sqlalchemy import Column, Integer, BIGINT, Float, String, DateTime, UniqueConstraint, CheckConstraint, event, DDL, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from FastAPI.Constants import ALL_TOKENS
# from FastAPI.DBConn.PGConn.PGConnectionNew import engine

TableSQL = declarative_base()


class DailyTFTable(TableSQL):
    __tablename__ = 'dailytf_data'
    __table_args__ = (
        UniqueConstraint('token', 'time', name='unique_token_time_for_dailytf_data'),
        {
            "postgresql_partition_by": "LIST (token)",
        },
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(Integer, index=True, nullable=False, primary_key=True)
    time = Column(DateTime(timezone=False), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    
# @event.listens_for(TableSQL.metadata, 'after_create')
# def create_partitions(target, connection, **kw):
#     for token in ALL_TOKENS:
#         input_params = {"token":int(token)}
#         ddl = text(f"""
#                     DO $$ 
#                     BEGIN
#                         EXECUTE 'CREATE TABLE IF NOT EXISTS dailytf_data_' || :token ||
#                                 ' PARTITION OF dailytf_data 
#                                 FOR VALUES IN (' || :token || ')
#                                 ';
#                     END $$;
#                 """)
#         ddl1 = text(f"""
#                     DO $$ 
#                     BEGIN
#                         EXECUTE 'ALTER TABLE  dailytf_data_' || :token ||
#                                 ' ADD CONSTRAINT unique_token_dailytf_data_' || :token || ' CHECK ( token = ' || :token || ' )
#                                 ';
#                     END $$;
#                 """)
#         compiled_ddl = ddl.bindparams(**input_params)
#         connection.execute(compiled_ddl)
#         compiled_ddl = ddl1.bindparams(**input_params)
#         connection.execute(compiled_ddl)
    

class FifteenTFTable(TableSQL):
    __tablename__ = 'fifteentf_data'

    __table_args__ = (
        UniqueConstraint('token', 'time', name='unique_token_time_for_fifteentf'),
        {
            "postgresql_partition_by": "LIST (token)",
        },
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(Integer, index=True, nullable=False, primary_key=True)
    time = Column(DateTime(timezone=False), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

# @event.listens_for(TableSQL.metadata, 'after_create')
# def create_partitions(target, connection, **kw):
#     for token in ALL_TOKENS:
#         input_params = {"token":int(token)}
#         ddl1 = text(f"""
#                     DO $$ 
#                     BEGIN
#                         EXECUTE 'ALTER TABLE fifteentf_data_' || :token ||
#                                 ' ADD CONSTRAINT unique_token_fifteentf_data' || :token || ' CHECK  ( token = ' || :token || ')
#                                 ';
#                     END $$;
#                 """)
#         ddl = text(f"""
#                     DO $$ 
#                     BEGIN
#                         EXECUTE 'CREATE TABLE IF NOT EXISTS fifteentf_data_' || :token ||
#                                 ' PARTITION OF fifteentf_data 
#                                 FOR VALUES IN (' || :token || ')
#                                 ';
#                     END $$;
#                 """)
#         compiled_ddl = ddl.bindparams(**input_params)
#         connection.execute(compiled_ddl)
#         compiled_ddl = ddl1.bindparams(**input_params)
#         connection.execute(compiled_ddl)
            
class HighLowTable(TableSQL):
    __tablename__ = 'highlow_data'
    __table_args__ = (
        CheckConstraint("high_low IN ('h', 'l', 'hl')", name='check_high_low_values_highlow_data'),
        CheckConstraint("tf IN ('1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '1D', '1W', '1M')", name='check_tf_values_highlow_data'),
        {
            "postgresql_partition_by": "LIST (token)",
        },
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    index = Column(Integer, nullable=False)
    token = Column(Integer, index=True, nullable=False, primary_key=True)
    time = Column(DateTime(timezone=False), nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BIGINT, nullable=False)
    high_low = Column(String(2))
    tf = Column(String(3))

# @event.listens_for(TableSQL.metadata, 'after_create')
# def create_partitions(target, connection, **kw):
#     for token in ALL_TOKENS:
#         input_params = {"token":int(token)}
#         ddl1 = text(f"""
#                     DO $$ 
#                     BEGIN
#                         EXECUTE 'ALTER TABLE highlow_data_' || :token ||
#                                 ' ADD CONSTRAINT unique_token_highlow_data_' || :token || ' CHECK  ( token = ' || :token || ')
#                                 ';
#                     END $$;
#                 """)
#         ddl = text(f"""
#                     DO $$ 
#                     BEGIN
#                         EXECUTE 'CREATE TABLE IF NOT EXISTS highlow_data_' || :token ||
#                                 ' PARTITION OF highlow_data 
#                                 FOR VALUES IN (' || :token || ')
#                                 ';
#                     END $$;
#                 """)
#         compiled_ddl = ddl.bindparams(**input_params)
#         connection.execute(compiled_ddl)
#         compiled_ddl = ddl1.bindparams(**input_params)
#         connection.execute(compiled_ddl)
      
class TicksTable(TableSQL):
    __tablename__ = 'ticks_data'

    id = Column(Integer, primary_key=True)
    token = Column(Integer, nullable=False)
    time = Column(DateTime(timezone=False))
    ltp = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint('token', 'time', name='unique_token_time_constraints_ticks_data'),
    )

class TrendlineTable(TableSQL):
    __tablename__ = 'trendline_data'

    id = Column(Integer, primary_key=True)
    token = Column(Integer, nullable=False)
    tf = Column(String(3))
    slope = Column(Float, nullable=False)
    intercept = Column(Float, nullable=False)
    startdate = Column(DateTime(timezone=False), nullable=False)
    enddate = Column(DateTime(timezone=False), nullable=False)
    hl = Column(String(2), nullable=False)
    index1 = Column(Integer, nullable=False)
    index2 = Column(Integer, nullable=False)
    index = Column(Integer, nullable=False)
    connects = Column(Integer, nullable=False)
    totalconnects = Column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint(hl.in_(['h', 'l']), name='check_hl_values_trendline_data'),
        CheckConstraint(tf.in_(['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '1D', '1W', '1M']), name='check_tf_values_trendline_data'),
    )

class SimTrendlineTable(TableSQL):
    __tablename__ = 'sim_trendline_data'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    token = Column(String, nullable=False)
    tf = Column(String(3), nullable=False)
    slope = Column(Float, nullable=False)
    intercept = Column(Float, nullable=False)
    hl = Column(String(2), nullable=False)
    connects = Column(Integer, nullable=False)
    totalconnects = Column(Integer, nullable=False)
    candlescount = Column(Integer, nullable=False)
    mean = Column(Float, nullable=False)
    median = Column(Float, nullable=False)
    mode = Column(Float, nullable=False)
    _range = Column(Float, name='range', nullable=False) # 'range' is a reserved keyword, so use a different name
    std = Column(Float, nullable=False)
    skewness = Column(Float, nullable=False)
    kurtosis = Column(Float, nullable=False)
    adf_stats = Column(Float, nullable=False)
    adf_p = Column(Float, nullable=False)
    adf_1 = Column(Float, nullable=False)
    adf_5 = Column(Float, nullable=False)
    adf_10 = Column(Float, nullable=False)
    kpss_stats = Column(Float, nullable=False)
    kpss_p = Column(Float, nullable=False)
    kpss_1 = Column(Float, nullable=False)
    kpss_5 = Column(Float, nullable=False)
    kpss_10 = Column(Float, nullable=False)
    volume_ratio = Column(Float, nullable=False)
    close_percentage = Column(Float, nullable=False)
    rrr1 = Column(Float, nullable=False)
    rrr2 = Column(Float, nullable=False)
    rrr3 = Column(Float, nullable=False)
    rrr4 = Column(Float, nullable=False)
    rrr5 = Column(Float, nullable=False)
    rrr6 = Column(Float, nullable=False)
    rrr7 = Column(Float, nullable=False)
    rrr8 = Column(Float, nullable=False)
    rrr9 = Column(Float, nullable=False)
    rrr10 = Column(Float, nullable=False)
    __table_args__ = (
        CheckConstraint(hl.in_(['h', 'l']), name='check_hl_values_sim_trendline_data'),
        CheckConstraint(tf.in_(['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '1D', '1W', '1M']), name='check_tf_values_sim_trendline_data'),
    )


class BrokenTrendlines(TableSQL):
    __tablename__ = 'broken_trendlines_data'

    id = Column(Integer, primary_key=True)
    token = Column(Integer, nullable=False)
    tf = Column(String(3))
    slope = Column(Float, nullable=False)
    intercept = Column(Float, nullable=False)
    startdate = Column(DateTime(timezone=False), nullable=False)
    enddate = Column(DateTime(timezone=False), nullable=False)
    hl = Column(String(2), nullable=False)
    index1 = Column(Integer, nullable=False)
    index2 = Column(Integer, nullable=False)
    index = Column(Integer, nullable=False)
    connects = Column(Integer, nullable=False)
    totalconnects = Column(Integer, nullable=False)
    __table_args__ = (
        CheckConstraint(hl.in_(['h', 'l']), name='check_hl_values_broken_trendlines_data'),
        CheckConstraint(tf.in_(['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '1D', '1W', '1M']), name='check_tf_values_broken_trendlines_data'),
    )

class StockDetails(TableSQL):
    __tablename__ = 'stock_details'

    id = Column(Integer, primary_key=True)
    token = Column(Integer, nullable=False)
    name = Column(String(15), nullable=False)
    category = Column(String(15))

class TradesTable(TableSQL):
    __tablename__ = 'trades_data'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    token = Column(Integer, nullable=False)
    tf = Column(String(14), nullable=False)
    status = Column(String(3))
    direction = Column(String(5))
    entry_condition = Column(String(5))
    entry = Column(DateTime(timezone=False), default=func.now())
    exit = Column(DateTime(timezone=False))
    tp = Column(Float)
    sl = Column(Float)
    bp = Column(Float)
    sp = Column(Float)
    rrr = Column(Float)
    quantity = Column(Float)
    cap = Column(Float)
    current_value = Column(Float)
    pl = Column(Float)

class UsersTable(TableSQL):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    email = Column(String(60), nullable=False)
    password = Column(String(60), nullable=False)



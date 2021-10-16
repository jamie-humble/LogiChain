import sqlite3
con = sqlite3.connect('LogiChain.db')
cur = con.cursor()

# create user table
cur.execute(
  """
  CREATE TABLE IF NOT EXISTS users(
    username CHAR(50) PRIMARY KEY,
    password CHAR(50),
    node CHAR(50),
    firstname CHAR(50), 
    lastname CHAR(50),
    email CHAR(200),
    phone CHAR(15)
  );
  """
)

# create node table
cur.execute(
  """
  CREATE TABLE IF NOT EXISTS nodes(
    type CHAR(20) PRIMARY KEY,
    seed CHAR(35),
    public_key CHAR(70),
    private_key CHAR(70), 
    classic_address CHAR(35),
    sequence INT
  );
  """
)

# create node table
cur.execute(
  """
  CREATE TABLE IF NOT EXISTS nodes(
    type CHAR(20) PRIMARY KEY,
    seed CHAR(35),
    public_key CHAR(70),
    private_key CHAR(70), 
    classic_address CHAR(35),
    sequence INT
  );
  """
)

# create events table
cur.execute(
  """
  CREATE TABLE IF NOT EXISTS events(
    username CHAR(20),
    time CHAR(35),
    event_type CHAR(70),
    memo CHAR(70)
  );
  """
)


con.commit()
con.close()

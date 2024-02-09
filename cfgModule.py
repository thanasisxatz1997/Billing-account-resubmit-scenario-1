from datetime import datetime
from cryptography.fernet import Fernet
import oracledb
import Customer

KEY =
FER = Fernet(KEY)
encOteMigPass =
osmPass =
decOsm = FER.decrypt(osmPass).decode()
decOtemig = FER.decrypt(encOteMigPass).decode()


def CurrentDateTime():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")


def ConnectToOtemigDb(password):
    oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_12")
    con = oracledb.connect(user='', password=password, dsn="")
    cursor = con.cursor()
    return cursor, con


def ConnectToOsmDb(password):
    oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_12")
    con = oracledb.connect(user='', password=password, dsn='')
    cursor = con.cursor()
    return cursor, con


def GetOsmData(cursor):
    query = '''SELECT  QUERY HERE'''
    cursor.execute(query)
    results = cursor.fetchall()
    for row in results:
        print(row)
    return results


def GetNumsFromOsmData(dataList):
    refNums = []
    for item in dataList:
        refNums.append(item[1])
    return refNums


def RunOteMigProcedure(cursor, connection, refNum):
    query = f"BEGIN ...('{refNum}'); COMMIT; END;"
    cursor.execute(query)
    connection.commit()


def GetOtemigColumns(cursor):
    query = "SELECT column_name FROM USER_TAB_COLUMNS WHERE table_name = ''"
    cursor.execute(query)
    results = cursor.fetchall()
    print(results)


def GetOtemigData(cursor):
    query = "SELECT * FROM  WHERE STATUS = '' AND CATEGORY = ''"
    cursor.execute(query)
    results = cursor.fetchall()
    print("OtemigData:")
    for row in results:
        print(row)
    return results


def ParsedOtemigData(otemigData):
    customers = []
    for item in otemigData:
        customer = Customer.make_customer(custId=item[0], orderId=item[1], baRid=item[5], baCode=item[6],
                                          category=item[10], action=item[14])
        customers.append(customer)
    return customers


def UpdateOtemigWithSuccess(cursor, connection, custId):
    query = f"UPDATE  SET STATUS = 'SUCCESS', UPD_DATE = SYSDATE WHERE ID = '{custId}' AND CATEGORY = ''"
    cursor.execute(query)
    connection.commit()


def UpdateOtemigWithError(cursor, connection, custId, errorMessage="Error while submitting customer."):
    query = f"UPDATE  SET STATUS = 'ERROR', UPD_DATE = SYSDATE, ERROR_DESC = '{errorMessage}' WHERE ID = '{custId}' AND CATEGORY = ''"
    cursor.execute(query)
    connection.commit()


def RunConfig():
    osmCursor, osmConn = ConnectToOsmDb(decOsm)
    otemigCursor, otemigConn = ConnectToOtemigDb(decOtemig)
    osmData = GetOsmData(osmCursor)
    refNums = GetNumsFromOsmData(osmData)
    osmConn.close()
    for refNum in refNums:
        RunOteMigProcedure(otemigCursor, otemigConn, refNum)
    otemigData = GetOtemigData(otemigCursor)
    GetOtemigColumns(otemigCursor)
    customers = ParsedOtemigData(otemigData)
    otemigConn.close()
    return customers

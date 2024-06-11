class Customer(object):
    custId = None,
    orderId = None,
    baRid = None,
    baCode = None,
    category = None,
    action = None,

    def __init__(self, custId, orderId, baRid, baCode, category, action):
        self.custId = custId
        self.orderId = orderId
        self.baRid = baRid
        self.baCode = baCode
        self.category = category
        self.action = action

    def PrintCustomer(self):
        print(self.custId,self.orderId,self.baRid,self.baCode,self.category,self.action)

    def GetCustomerStr(self):
        return str(self.custId+' '+self.orderId+' '+self.baRid+' '+self.baCode+' '+self.category+' '+self.action)

def make_customer(custId, orderId, baRid, baCode, category, action):
    customer = Customer(custId, orderId, baRid, baCode, category, action)
    return customer

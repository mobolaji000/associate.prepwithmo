from app.models import Transaction,InstallmentPlan,InstallmentInvoice
from app import db
from datetime import datetime
import math
import uuid
from dateutil.parser import parse
import logging
import traceback

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class AppDBUtil():
    def __init__(self):
        pass

    @classmethod
    def createOrModifyClientTransaction(cls, clientData={}, transaction_code=None, action=''):
        transaction_code = transaction_code if transaction_code else str(uuid.uuid4().int>>64)[:6]
        stripe_customer_id = clientData.get('stripe_customer_id','')
        first_name = clientData.get('first_name','')
        last_name = clientData.get('last_name','')
        phone_number = clientData.get('phone_number','999')
        email = clientData.get('email','')
        was_diagnostic_purchased = clientData.get('was_diagnostic_purchased', '')
        diag_units = 0 if clientData.get('diag_units','') == '' else clientData.get('diag_units','')
        diag_total = 0 if clientData.get('diag_total','') == '' else clientData.get('diag_total','')
        was_test_prep_purchased = clientData.get('was_test_prep_purchased','')
        tp_product = clientData.get('tp_product','')
        tp_units = 0 if clientData.get('tp_units','') == '' else clientData.get('tp_units','')
        tp_total = 0 if clientData.get('tp_total','') == '' else clientData.get('tp_total','')
        was_college_apps_purchased = clientData.get('was_college_apps_purchased', '')
        college_apps_product = clientData.get('college_apps_product','')
        college_apps_units = 0 if clientData.get('college_apps_units','') == '' else clientData.get('college_apps_units','')
        college_apps_total = 0 if clientData.get('college_apps_total','') == '' else clientData.get('college_apps_total','')
        adjust_total = 0 if clientData.get('adjust_total','') == '' else clientData.get('adjust_total','')
        adjustment_explanation = clientData.get('adjustment_explanation','')
        transaction_total = 0 if clientData.get('transaction_total','') == '' else clientData.get('transaction_total','')
        installment_counter = 0 if clientData.get('installment_counter','') == '' else int(clientData.get('installment_counter',''))#-1
        # client-side counter is always one more; get the actual number here



        number_of_rows_modified = None
        if action=='create':

            transaction = Transaction(transaction_code=transaction_code, stripe_customer_id=stripe_customer_id, first_name=first_name, last_name=last_name,
                                  phone_number=phone_number, email=email, was_diagnostic_purchased=was_diagnostic_purchased, diag_units=diag_units,
                                  diag_total=diag_total, was_test_prep_purchased=was_test_prep_purchased, tp_product=tp_product, tp_units=tp_units,
                                  tp_total=tp_total, was_college_apps_purchased=was_college_apps_purchased, college_apps_product=college_apps_product,
                                  college_apps_units=college_apps_units, college_apps_total=college_apps_total,
                                  adjust_total=adjust_total, adjustment_explanation=adjustment_explanation, transaction_total=transaction_total, installment_counter=installment_counter)


            db.session.add(transaction)

        elif action=='modify':
            #what happens in the unlikely event that 2 rows have the same transaction code?
            number_of_rows_modified = db.session.query(Transaction).filter_by(transaction_code=transaction_code).update\
                ({"stripe_customer_id": stripe_customer_id,"first_name": first_name,"last_name": last_name,"phone_number": phone_number,
                        "email": email,"was_diagnostic_purchased": was_diagnostic_purchased,"diag_units": diag_units,"diag_total": diag_total,
                        "was_test_prep_purchased": was_test_prep_purchased,"tp_product": tp_product,"tp_units": tp_units,"tp_total": tp_total,
                        "was_college_apps_purchased": was_college_apps_purchased,"college_apps_product": college_apps_product,"college_apps_units": college_apps_units,
                        "college_apps_total": college_apps_total,"adjust_total": adjust_total,
                        "adjustment_explanation": adjustment_explanation,"transaction_total": transaction_total, "installment_counter":installment_counter})

            print("number of transaction rows modified is: ",number_of_rows_modified) #printing of rows modified to logs to help with auditing



        cls.executeDBQuery()

        cls.createOrModifyInstallmentPlan(clientData=clientData, transaction_code=transaction_code, action=action)

        return transaction_code,number_of_rows_modified

    @classmethod
    def createOrModifyInstallmentInvoice(cls,first_name=None,last_name=None,phone_number=None,email=None,transaction_code=None,stripe_customer_id=None,stripe_invoice_id=None,installment_payment_date=None,installment_payment_amount=None):
        #
        installment_invoice = InstallmentInvoice(first_name=first_name,last_name=last_name,phone_number=phone_number, email=email,
                                                 transaction_code=transaction_code, stripe_customer_id=stripe_customer_id,
                                                 installment_payment_date=installment_payment_date,installment_payment_amount=installment_payment_amount,
                                                 stripe_invoice_id=stripe_invoice_id)

        db.session.add(installment_invoice)
        print("installment invoice created is: ", installment_invoice)
        cls.executeDBQuery()


    @classmethod
    def createOrModifyInstallmentPlan(cls, clientData={}, transaction_code=None, action=''):

        if int(clientData['installment_counter']) > 1:
            installments = {}
            print("number of installments is " + str(int(clientData['installment_counter'])-1))
            for k in range(1, int(clientData['installment_counter'])):
                print("current installment being updated is " + str(k))
                installments.update({'date_' + str(k): clientData['date_' + str(k)], 'amount_' + str(k): clientData['amount_' + str(k)]})

            installment_plan = InstallmentPlan(transaction_code=transaction_code, stripe_customer_id=clientData['stripe_customer_id'], first_name=clientData['first_name'], last_name=clientData['last_name'], phone_number=clientData['phone_number'], email=clientData['email'])
            db.session.add(installment_plan)
            print("installment plan created is: ", installment_plan)
            cls.executeDBQuery()

            installment_plan = db.session.query(InstallmentPlan).filter_by(transaction_code=transaction_code)
            number_of_rows_modified = installment_plan.update(installments)
            print("number of installment rows added or modified is: ", number_of_rows_modified)

            cls.executeDBQuery()
        else:
            print("No installment created or modified")

    @classmethod
    def is_date(cls,string_date, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            parse(string_date, fuzzy=fuzzy)
            return True

        # except Exception as e:
        #     return False
        except ValueError as v:
            #logger.error(v)
            #traceback.print_exc()
            return False

    @classmethod
    def deleteTransaction(cls, codeOfTransactionToDelete):
        transaction = Transaction.query.filter_by(transaction_code=codeOfTransactionToDelete).first()
        db.session.delete(transaction)
        cls.executeDBQuery()

    @classmethod
    def modifyTransactionDetails(cls, data_to_modify):
        return cls.createOrModifyClientTransaction(clientData=data_to_modify, transaction_code=data_to_modify['transaction_code'], action='modify')


    @classmethod
    def updateAmountPaidAgainstTransaction(cls,transaction_code,amount_paid):
        transaction = Transaction.query.filter_by(transaction_code=transaction_code).first()
        transaction.amount_from_transaction_paid_so_far = transaction.amount_from_transaction_paid_so_far + amount_paid
        cls.executeDBQuery()

    @classmethod
    def updateInstallmentInvoiceAsPaid(cls, stripe_invoice_id=None):
        invoice = InstallmentInvoice.query.filter_by(stripe_invoice_id=stripe_invoice_id).first()
        invoice.payment_made = True
        cls.executeDBQuery()

    @classmethod
    def findInstallmentInvoicesToPay(cls):
        #installment_invoices_to_pay = InstallmentInvoice.query.filter_by(payment_made=False,installment_payment_date=datetime.today()).all()
        installment_invoices_to_pay = db.session.query(InstallmentInvoice).filter((InstallmentInvoice.payment_made==False) & (InstallmentInvoice.installment_payment_date<=datetime.today())).all()
        #or_(db.users.name=='Ryan', db.users.country=='England')
        #cls.executeDBQuery()
        print("installment_invoices_to_pay are: ",installment_invoices_to_pay)
        search_results = []
        for installment_invoice in installment_invoices_to_pay:
            installment_invoice_details = {}
            installment_invoice_details['first_name'] = installment_invoice.first_name
            installment_invoice_details['last_name'] = installment_invoice.last_name
            installment_invoice_details['installment_payment_amount'] = installment_invoice.installment_payment_amount
            installment_invoice_details['stripe_invoice_id'] = installment_invoice.stripe_invoice_id
            print(installment_invoice_details)
            print(" ")
            search_results.append(installment_invoice_details)
        return search_results

    @classmethod
    def findClientsToReceiveReminders(cls):
        transaction_details = Transaction.query.filter_by(payment_started=False).all()
        search_results = []
        for transaction in transaction_details:
            client = {}
            client['first_name'] = transaction.first_name
            client['last_name'] = transaction.last_name
            client['phone_number'] = transaction.phone_number
            client['email'] = transaction.email
            client['transaction_code'] = transaction.transaction_code
            client['payment_started'] = str(transaction.payment_started)
            search_results.append(client)

        return search_results

    @classmethod
    def searchTransactions(cls, search_query):
        if search_query.isdigit():
            if len(search_query) == 6:
                transaction_details = Transaction.query.filter_by(transaction_code=search_query).order_by(Transaction.date_created.desc()).all()
            else:
                transaction_details = Transaction.query.filter_by(phone_number=search_query).order_by(Transaction.date_created.desc()).all()
        elif "@" in search_query:
            transaction_details = Transaction.query.filter_by(email=search_query).order_by(Transaction.date_created.desc()).all()
        elif cls.is_date(search_query):
            #do something to get the date in the right format first
            transaction_details = Transaction.query.filter_by(date_created=search_query).order_by(Transaction.date_created.desc()).all()
        else:
            transaction_details = Transaction.query.filter((Transaction.first_name == search_query.capitalize()) | (Transaction.last_name == search_query.capitalize())
                                                       | (Transaction.first_name == search_query.lower()) | (Transaction.last_name == search_query.lower())
                                                       | (Transaction.first_name == search_query) | (Transaction.last_name == search_query))\
                .order_by(Transaction.date_created.desc()).all()




        search_results = []
        for transaction in transaction_details:
            client = {}
            client['first_name'] = transaction.first_name
            client['last_name'] = transaction.last_name
            client['phone_number'] = transaction.phone_number
            client['email'] = transaction.email
            client['stripe_customer_id'] = transaction.stripe_customer_id
            client['adjust_total'] = transaction.adjust_total
            client['adjustment_explanation'] = transaction.adjustment_explanation
            client['transaction_total'] = transaction.transaction_total
            client['date_created'] = transaction.date_created.strftime("%m/%d/%Y")
            client['transaction_code'] = transaction.transaction_code
            client['was_diagnostic_purchased'] = transaction.was_diagnostic_purchased
            client['diag_units'] = transaction.diag_units
            client['diag_total'] = transaction.diag_total
            client['was_test_prep_purchased'] = transaction.was_test_prep_purchased
            client['tp_units'] = transaction.tp_units
            client['tp_total'] = transaction.tp_total
            client['was_college_apps_purchased'] = transaction.was_college_apps_purchased
            client['college_apps_units'] = transaction.college_apps_units
            client['college_apps_total'] = transaction.college_apps_total
            client['adjust_total'] = transaction.adjust_total
            client['installment_counter'] = transaction.installment_counter
            client['adjustment_explanation'] = transaction.adjustment_explanation
            client['transaction_total'] = transaction.transaction_total
            client['payment_started'] = str(transaction.payment_started)

            installment_details = InstallmentPlan.query.filter_by(transaction_code=transaction.transaction_code).first()
            #cls.executeDBQuery()

            if installment_details:
                installments = {}
                for k in range(1, int(transaction.installment_counter)):
                    installments.update({'date_' + str(k): installment_details.__dict__['date_' + str(k)].strftime("%m/%d/%Y"), 'amount_' + str(k): installment_details.__dict__['amount_' + str(k)]})

                client['installment_details'] = installments
                #print("installment details are ",client['installment_details'])

            search_results.append(client)
        print("search results are ",search_results)
        return search_results

    @classmethod
    def getTransactionDetails(cls,transaction_code):
        showACHOverride = False
        if 'ach' in transaction_code.lower():
            showACHOverride = True
            transaction_code = transaction_code.lower().split('ach')[0]

        print("showACHOverride is: ",showACHOverride)

        admin_transaction_details = Transaction.query.filter_by(transaction_code=transaction_code).order_by(Transaction.date_created.desc()).first()
        if admin_transaction_details.installment_counter > 1:
            admin_transaction_details.turn_on_installments = True
        return cls.computeClientTransactionDetails(admin_transaction_details,showACHOverride)

    @classmethod
    def updateTransactionPaymentStarted(cls, transaction_code):
        transaction = Transaction.query.filter_by(transaction_code=transaction_code).order_by(Transaction.date_created.desc()).first()
        transaction.payment_started = True
        cls.executeDBQuery()

    @classmethod
    def computeClientTransactionDetails(cls,admin_transaction_details,showACHOverride):
        client_info = {}
        products_info = []
        try:
            client_info['first_name'] = admin_transaction_details.first_name
            client_info['last_name'] = admin_transaction_details.last_name
            client_info['phone_number'] = admin_transaction_details.phone_number
            client_info['email'] = admin_transaction_details.email
            client_info['stripe_customer_id'] = admin_transaction_details.stripe_customer_id
            client_info['adjust_total'] = admin_transaction_details.adjust_total
            client_info['adjustment_explanation'] = admin_transaction_details.adjustment_explanation
            client_info['transaction_total'] = admin_transaction_details.transaction_total
            client_info['transaction_code'] = admin_transaction_details.transaction_code
            client_info['payment_started'] = admin_transaction_details.payment_started
            client_info['installment_counter'] = admin_transaction_details.installment_counter
            client_info['showACHOverride'] = str(showACHOverride)
            print("client_info_installment_counter is "+str(admin_transaction_details.installment_counter))

            if admin_transaction_details.was_diagnostic_purchased:
                next_product = {}
                next_product['number_of_product_units'] = admin_transaction_details.diag_units
                next_product['per_product_cost'] = 50
                next_product['total_product_cost'] = admin_transaction_details.diag_total
                next_product['product_description'] = "Diagnostic/Consultation"
                products_info.append(next_product)

            if admin_transaction_details.was_test_prep_purchased:
                next_product = {}
                next_product['number_of_product_units'] = admin_transaction_details.tp_units
                next_product['per_product_cost'] = admin_transaction_details.tp_product
                next_product['total_product_cost'] = admin_transaction_details.tp_total

                test_prep_product_code = admin_transaction_details.was_test_prep_purchased.split('-')
                if len(test_prep_product_code) == 4:
                    test_prep_location = test_prep_product_code[1].capitalize()+" "+test_prep_product_code[2].capitalize()
                    test_prep_duration = str(int(test_prep_product_code[3][:2]))+"-Weeks" if int(test_prep_product_code[3][:2])>1 else str(int(test_prep_product_code[3][:2]))+"-Week"
                else:
                    test_prep_location = test_prep_product_code[1].capitalize()
                    test_prep_duration = str(int(test_prep_product_code[2][:2]))+"-Weeks" if int(test_prep_product_code[2][:2])>1 else str(int(test_prep_product_code[2][:2]))+"-Week"

                next_product['product_description'] = test_prep_duration + " " + test_prep_location + " SAT/ACT Prep"
                products_info.append(next_product)

            if admin_transaction_details.was_college_apps_purchased:
                next_product = {}
                next_product['number_of_product_units'] = 1
                next_product['per_product_cost'] = 275
                next_product['total_product_cost'] = 275
                next_product['product_description'] = "Consultation/Advisory Services"
                products_info.append(next_product)

                next_product = {}
                next_product['number_of_product_units'] = admin_transaction_details.college_apps_units
                next_product['per_product_cost'] = admin_transaction_details.college_apps_product
                next_product['total_product_cost'] = admin_transaction_details.college_apps_total

                college_apps_product_code = admin_transaction_details.was_college_apps_purchased

                if college_apps_product_code == 'apps-1':
                    next_product['product_description'] = "Per Essay Scholarships/Applications Package"
                elif college_apps_product_code == 'apps-2':
                    next_product['product_description'] = "1-3 Programs Scholarships/Applications Package"
                elif college_apps_product_code == 'apps-3':
                    next_product['product_description'] = "More Than 3 Programs Scholarships/Applications Package"

                products_info.append(next_product)


            if admin_transaction_details.turn_on_installments:
                #client_info['deposit'] = math.ceil(admin_transaction_details.transaction_total/2)
                client_info['turn_on_installments'] = True
                client_info['installments'] = []

                installment_details = InstallmentPlan.query.filter_by(transaction_code=admin_transaction_details.transaction_code).first()


                for k in range(1, int(admin_transaction_details.installment_counter)):
                    next_installment = {}
                    next_installment.update({'date': installment_details.__dict__['date_' + str(k)], 'amount': installment_details.__dict__['amount_' + str(k)]})
                    client_info['installments'].append(next_installment)

                #
                # index = 0
                # for installment_date in [admin_transaction_details.installment_date_1,admin_transaction_details.installment_date_2,admin_transaction_details.installment_date_3]:
                #     next_installment = {}
                #     if (installment_date-datetime(1,1,1).date()).days != 0:
                #         next_installment['installment_date'] = installment_date
                #         if index == 0:
                #             next_installment['installment_amount'] = math.ceil(admin_transaction_details.transaction_total/2)
                #         if index == 1:
                #             client_info['installments'][0]['installment_amount'] = math.ceil(admin_transaction_details.transaction_total/4)
                #             next_installment['installment_amount'] = math.ceil(admin_transaction_details.transaction_total/4)
                #         if index == 2:
                #             client_info['installments'][0]['installment_amount'] = math.ceil(admin_transaction_details.transaction_total / 6)
                #             client_info['installments'][1]['installment_amount'] = math.ceil(admin_transaction_details.transaction_total / 6)
                #             next_installment['installment_amount'] = math.ceil(admin_transaction_details.transaction_total / 6)
                #
                #         index=index+1
                #         client_info['installments'].append(next_installment)

        except Exception as e:
            print(e)

        return client_info,products_info,showACHOverride

    @classmethod
    def executeDBQuery(cls):
        try:
            db.session.commit()
        except Exception as e:
            # if any kind of exception occurs, rollback transaction
            db.session.rollback()
            traceback.print_exc()
        finally:
            db.session.close()





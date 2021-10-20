from app import db

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_code = db.Column(db.String(8), index=True, nullable=False, unique=True, default='')
    stripe_customer_id = db.Column(db.String(48),index=True,nullable=False, default='')
    first_name = db.Column(db.String(64), index=True,nullable=False, default='')
    last_name = db.Column(db.String(64), index=True,nullable=False, default='')
    phone_number = db.Column(db.String(12),index=True,nullable=False, default='')
    email = db.Column(db.String(120), index=True,nullable=False, default='')
    was_diagnostic_purchased = db.Column(db.String(30), index=True, nullable=False, default='')
    diag_units = db.Column(db.Integer, index=True, nullable=False, default=-1)
    diag_total = db.Column(db.Integer, index=True, nullable=False, default=-1)
    was_test_prep_purchased = db.Column(db.String(30), index=True,nullable=False, default='')
    tp_product = db.Column(db.String(64), index=True,nullable=False, default='')
    tp_units = db.Column(db.Integer, index=True,nullable=False, default=-1)
    tp_total = db.Column(db.Integer, index=True,nullable=False, default=-1)
    was_college_apps_purchased = db.Column(db.String(30), index=True,nullable=False, default='')
    college_apps_product = db.Column(db.String(64), index=True,nullable=False, default='')
    college_apps_units = db.Column(db.Integer, index=True,nullable=False, default=-1)
    college_apps_total = db.Column(db.Integer, index=True,nullable=False, default=-1)
    adjust_total = db.Column(db.Float, index=True,nullable=False, default=-1)
    adjustment_explanation = db.Column(db.String(190), index=True, nullable=False, default='')
    transaction_total = db.Column(db.Integer, index=True, nullable=False, default=-1)
    installment_counter = db.Column(db.Integer, index=True, nullable=False, default=-1)
    date_created = db.Column(db.DateTime(timezone=True), index=True, server_default=db.func.now())
    payment_started = db.Column(db.Boolean, unique=False,nullable=False, default=False)
    amount_from_transaction_paid_so_far = db.Column(db.Integer, index=True, nullable=False, default=0)
    #installment_date = db.Column(db.PickleType,  index=True, nullable=True, default='')
    #installment_amount = db.Column(db.PickleType, index=True, nullable=True, default='')
    #what happens when you try to update pickle type? do you have to instantiate a new variable?


    def __repr__(self):
        return '<Transaction {}>'.format(self.transaction_code)


class InstallmentPlan(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    transaction_code = db.Column(db.String(8), db.ForeignKey('transaction.transaction_code'), primary_key=True, nullable=False)
    #invoice_code = db.Column(db.String(8),index=True,nullable=False, default='')
    stripe_customer_id = db.Column(db.String(48),index=True,nullable=False, default='')
    first_name = db.Column(db.String(64), index=True,nullable=False, default='')
    last_name = db.Column(db.String(64), index=True,nullable=False, default='')
    phone_number = db.Column(db.String(12),index=True,nullable=False, default='')
    email = db.Column(db.String(120), index=True,nullable=False, default='')

    date_1 = db.Column(db.Date,index=True,nullable=True)
    date_2 = db.Column(db.Date, index=True, nullable=True)
    date_3 = db.Column(db.Date, index=True, nullable=True)
    date_4 = db.Column(db.Date, index=True, nullable=True)
    date_5 = db.Column(db.Date, index=True, nullable=True)
    date_6 = db.Column(db.Date, index=True, nullable=True)
    date_7 = db.Column(db.Date, index=True, nullable=True)
    date_8 = db.Column(db.Date, index=True, nullable=True)
    date_9 = db.Column(db.Date, index=True, nullable=True)
    date_10 = db.Column(db.Date, index=True, nullable=True)
    date_11 = db.Column(db.Date, index=True, nullable=True)
    date_12 = db.Column(db.Date, index=True, nullable=True)

    amount_1 = db.Column(db.Integer, index=True,nullable=True, default=-1)
    amount_2 = db.Column(db.Integer, index=True, nullable=True, default=-1)
    amount_3 = db.Column(db.Integer, index=True, nullable=True, default=-1)
    amount_4 = db.Column(db.Integer, index=True, nullable=True, default=-1)
    amount_5 = db.Column(db.Integer, index=True, nullable=True, default=-1)
    amount_6 = db.Column(db.Integer, index=True, nullable=True, default=-1)
    amount_7 = db.Column(db.Integer, index=True,nullable=True, default=-1)
    amount_8 = db.Column(db.Integer, index=True, nullable=True, default=-1)
    amount_9 = db.Column(db.Integer, index=True, nullable=True, default=-1)
    amount_10 = db.Column(db.Integer, index=True, nullable=True, default=-1)
    amount_11 = db.Column(db.Integer, index=True,nullable=True, default=-1)
    amount_12 = db.Column(db.Integer, index=True,nullable=True, default=-1)


    def __repr__(self):
        return '<InstallmentPlan created for {}>'.format(self.transaction_code)

class InstallmentInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_code = db.Column(db.String(8), db.ForeignKey('installment_plan.transaction_code'), nullable=False)
    stripe_customer_id = db.Column(db.String(48),index=True,nullable=False, default='')
    first_name = db.Column(db.String(64), index=True,nullable=False, default='')
    last_name = db.Column(db.String(64), index=True,nullable=False, default='')
    phone_number = db.Column(db.String(12),index=True,nullable=False, default='')
    email = db.Column(db.String(120), index=True,nullable=False, default='')

    installment_payment_date = db.Column(db.Date,index=True,nullable=True)
    installment_payment_amount = db.Column(db.Integer, index=True,nullable=True, default=-1)
    stripe_invoice_id = db.Column(db.String(64), index=True,nullable=False, default='')
    payment_made = db.Column(db.Boolean, unique=False, nullable=False, default=False)

    def __repr__(self):
        return '<InstallmentInvoice created for {}>'.format(self.last_name)

db.create_all()
try:
    db.session.commit()
except:
    # if any kind of exception occurs, rollback transaction
    db.session.rollback()
    raise
finally:
    db.session.close()


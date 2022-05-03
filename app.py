from flask import Flask, redirect, url_for, render_template, flash
from forms.login import LoginForm
from forms.sign_up import SignUpForm
from forms.apartment import ApartmentForm
from forms.tenant import TenantForm
from forms.employee import EmployeeForm
from forms.building import BuildingForm
from forms.device import DeviceForm
from forms.payment import PaymentForm
from forms .lease import LeaseForm
from forms.change_password import ChangePasswordForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:terril@localhost/apartments'
db = SQLAlchemy(app)

app.config.update(dict(
    SECRET_KEY="kordes",
    WTF_CSRF_SECRET_KEY="kordes"
))

Bootstrap(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return Person.query.get(int(user_id))


class Person(UserMixin, db.Model):
    person_id = db.Column(db.BigInteger, primary_key=True) # primary keys are required by SQLAlchemy
    date_of_birth = db.Column(db.Date)
    first_name = db.Column(db.String(15))
    last_name = db.Column(db.String(15))
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def get_id(self):
        return self.person_id



@app.route('/')
@login_required
def home():
    return render_template('home.html', user_names=[])



@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.sign_up.data:
        return redirect(url_for('sign_up'))
    if form.validate_on_submit():
        user = Person.query.filter_by(email=form.email.data).first()
        if not user or not user.password == form.password.data:
            return render_template('login_error.html')
        else:
            # add logic here to validate and redirect
            login_user(user, remember=True)
            return redirect(url_for('home'))
    return render_template('login.html', form=form)


@app.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        # add logic here to validate and redirect
        email = form.email.data
        user = Person.query.filter_by(email=email).first()
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash("User found please login with your preexisting credentials")
            return redirect(url_for('login'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = Person(email=email,
                          first_name=form.first_name.data,
                          last_name = form.last_name.data,
                          password=form.password.data,
                          date_of_birth = form.dob.data)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        flash("Login with your new credentials")
        return redirect(url_for('login'))
    return render_template('sign_up.html', form=form)


@app.route('/change-password', methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # add logic here to validate and redirect
        result = list(
            db.session.execute('SELECT first_name, last_name FROM person WHERE email = \'%s\' and password = \'%s\'' %
                               (form.email.data, form.old_password.data)))
        if result:
            db.session.execute('''update person set password = \'%s\'
                                    where email = \'%s\' and password = \'%s\'''' %
                               (form.new_password.data,
                                form.email.data,
                                form.old_password.data))
            db.session.commit()
        flash("Login with your new credentials")
        return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/sign-out')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/apartments-all')
@login_required
def apartments():
    apartments = list(db.session.execute(
        """
        select b.name, a.apartment_id, a.type
        from apartment a
            join building b on a.building_id = b.building_id;
        """
    ))
    return render_template("apartments.html", apartments=apartments)

@app.route('/apartments-available')
@login_required
def apartments_available():
    apartments = list(db.session.execute(
        """
        select b.name, a.apartment_id, a.type
        from apartment a
            join building b on a.building_id = b.building_id
            left join tenant t on t.building_id = a.building_id and t.apartment_id = a.apartment_id
        where t.person_id is null;
        """
    ))
    return render_template("apartments-available.html", apartments=apartments)

@app.route('/apartments-occupied')
@login_required
def apartments_occupied():
    apartments = list(db.session.execute(
        """
        select b.name, a.apartment_id, a.type
        from apartment a
            join building b on a.building_id = b.building_id
            join tenant t on t.building_id = a.building_id and t.apartment_id = a.apartment_id;
        """
    ))
    return render_template("apartments-occupied.html", apartments=apartments)


@app.route('/apartment-add', methods=["GET", "POST"])
@login_required
def apartment_add():
    form = ApartmentForm()
    if form.cancel.data:
        return redirect(url_for("apartments"))
    if form.validate_on_submit():
        db.session.execute(
            """
            insert into apartment (building_id, apartment_id, type)
            values (:building_id, :apartment_id, :type)
            """,
            {"building_id": form.building_id.data,
             "apartment_id": form.apartment_id.data,
             "type": form.type.data}
        )
        db.session.commit()
        return redirect(url_for("apartments"))
    return render_template("apartment-add.html", form=form)


@app.route('/tenants')
@login_required
def tenants():
    tenants = list(db.session.execute(
        """
        select t.person_id, p.first_name, p.last_name, t.building_id, t.apartment_id from tenant t
        join person p on p.person_id = t.person_id;
        """
    ))
    return render_template("tenants.html", tenants=tenants)


@app.route('/tenants-add', methods=["GET", "POST"])
@login_required
def tenants_add():
    form = TenantForm()
    people = list(db.session.execute(
        """
        select p.person_id, concat(p.first_name, ' ', p.last_name) from person p;
        """
    ));
    form.person_id.choices = [(person_id, name) for person_id, name in people]

    apartments = list(db.session.execute(
        """
        select distinct a.apartment_id from apartment a;
        """
    ))
    form.apartment_id.choices = [(apartment_id[0], str(apartment_id[0])) for apartment_id in apartments]

    buildings = list(db.session.execute(
        """
        select distinct b.building_id from building b;
        """
    ))
    form.building_id.choices = [(building_id[0], str(building_id[0])) for building_id in buildings]

    if form.cancel.data:
        return redirect(url_for('tenants'))
    if form.validate_on_submit():
        unit = list(db.session.execute(
            """
            select * from apartment a where a.apartment_id = :apartment_id and a.building_id = :building_id
            """, {'apartment_id': form.apartment_id.data, 'building_id': form.building_id.data}
        ))
        tenant = list(db.session.execute(
            """
            select * from tenant t where t.person_id = :person_id
            """, {'person_id': form.person_id.data}
        ))

        if unit:
            if tenant:
                db.session.execute(
                    """
                    update tenant t 
                    set t.apartment_id = :apartment_id,
                        t.building_id = :building_id
                    where t.person_id = :person_id;
                    """, {'apartment_id': form.apartment_id.data, 'building_id': form.building_id.data, 'person_id': form.person_id.data}
                )
            else:
                db.session.execute(
                    """
                    insert into tenant (person_id, building_id, apartment_id)
                    values (:person_id, :building_id, :apartment_id);
                    """, {'person_id': form.person_id.data, 'apartment_id': form.apartment_id.data, 'building_id': form.building_id.data}
                )
            db.session.commit()
            return redirect(url_for('tenants'))
        else:
            flash("The apartment you chose does not exist")
            return render_template('tenants-add.html', form = form)
    return render_template('tenants-add.html', form=form)


@app.route('/tenants-delete/<tenant_id>')
@login_required
def tenants_delete(tenant_id):
    db.session.execute(
        """
        delete from tenant t where t.person_id = :person_id;
        """, {'person_id': tenant_id}
    )
    db.session.commit()
    return redirect(url_for('tenants'))

@app.route('/employees')
@login_required
def employees():
    employees = list(db.session.execute(
        """
        select e.person_id, p.first_name, p.last_name, e.type from employee e
        join person p on p.person_id = e.person_id;
        """
    ))
    return render_template("employees.html", employees=employees)


@app.route('/employees-add', methods=["GET", "POST"])
@login_required
def employees_add():
    form = EmployeeForm()
    people = list(db.session.execute(
        """
        select p.person_id, concat(p.first_name, ' ', p.last_name) from person p;
        """
    ))
    form.person_id.choices = [(person_id, name) for person_id, name in people]

    if form.cancel.data:
        return redirect(url_for('employees'))

    if form.validate_on_submit():

        employee = list(db.session.execute(
            """
            select * from employee e where e.person_id = :person_id
            """, {'person_id': form.person_id.data}
        ))

        if employee:
            db.session.execute(
                """
                update employee e 
                set e.type = :e_type,
                where e.person_id = :person_id;
                """, {'person_id': form.person_id.data, 'e_type': form.type.data}
            )
        else:
            db.session.execute(
                """
                insert into employee (person_id, type)
                values (:person_id, :e_type);
                """, {'person_id': form.person_id.data, 'e_type': form.type.data}
            )
        db.session.commit()
        return redirect(url_for('employees'))
    return render_template('employee-add.html', form=form)

@app.route('/employee-delete/<employee_id>')
@login_required
def employees_delete(employee_id):
    db.session.execute(
        """
        delete from employee e where e.person_id = :person_id;
        """, {'person_id': employee_id}
    )
    db.session.commit()
    return redirect(url_for('employees'))

@app.route('/buildings')
@login_required
def buildings():
    buildings = list(db.session.execute(
        """
        select b.building_id, b.name, count(a.apartment_id)
        from building b
            left join apartment a on a.building_id = b.building_id
            left join tenant t on t.building_id = a.building_id and t.apartment_id = a.apartment_id
        where t.person_id is null
        group by b.building_id, b.name;
        """
    ))
    return render_template("buildings.html", buildings=buildings)

@app.route('/buildings-add', methods=["GET", "POST"])
@login_required
def building_add():
    form = BuildingForm()
    if form.cancel.data:
        return redirect(url_for("buildings"))
    if form.validate_on_submit():
        db.session.execute(
            """
            insert into building (building_id, name)
            values (:building_id, :name)
            """,
            {"building_id": form.building_id.data,
             "name": form.name.data}
        )
        db.session.commit()
        return redirect(url_for("buildings"))
    return render_template("buildings-add.html", form=form)

@app.route('/devices')
@login_required
def devices():
    devices = list(db.session.execute(
        """
        select d.device_id,
               d.name,
               p.person_id,
               concat(p.first_name, ' ', p.last_name),
               CASE
                    WHEN l.device_id is not null THEN 'Light'
                    WHEN therm.device_id is not null THEN 'Thermostat'
                    WHEN dlock.device_id is not null THEN 'Lock'
                    ELSE 'NA'
                END
        from device d
            join person p on p.person_id = d.person_id
            left join light l on l.device_id = d.device_id
            left join thermostat therm on therm.device_id = d.device_id
            left join door_lock dlock on dlock.device_id = d.device_id;
        """
    ))
    return render_template("devices.html", devices=devices)


@app.route('/devices-add', methods=["GET", "POST"])
@login_required
def device_add():
    form = DeviceForm()

    people = list(db.session.execute(
        """
        select t.person_id, concat(p.first_name, ' ', p.last_name) from person p join tenant t on t.person_id = p.person_id;
        """
    ))
    form.person_id.choices = [(person_id, name) for person_id, name in people]
    if form.cancel.data:
        return redirect(url_for("devices"))
    if form.validate_on_submit():
        device_id = list(db.session.execute(
            """
            select max(device_id) from device;
            """
        ))[0][0] + 1

        db.session.execute(
            """
            insert into device (device_id, person_id, name)
            values (:device_id, :person_id, :name)
            """, {'device_id': device_id, 'person_id': form.person_id.data, 'name': form.name.data}
        )
        db.session.commit()

        if form.type.data == 1:
            db.session.execute(
                """
                insert into light (device_id)
                values (:device_id)
                """, {'device_id': device_id}
            )

        elif form.type.data == 2:
            db.session.execute(
                """
                insert into thermostat (device_id)
                values (:device_id)
                """, {'device_id': device_id}
            )
        else:
            db.session.execute(
                """
                insert into door_lock (device_id)
                values (:device_id)
                """, {'device_id': device_id}
            )

        db.session.commit()
        return redirect(url_for("devices"))
    return render_template("devices-add.html", form=form)


@app.route('/device-delete/<device_id>')
@login_required
def device_delete(device_id):
    db.session.execute(
        """
        delete from device d where d.device_id = :device_id;
        """, {'device_id': device_id}
    )
    db.session.commit()
    return redirect(url_for('devices'))


@app.route('/payments')
@login_required
def payments():
    payments = list(db.session.execute(
        """
        select p.payment_id, p.paid_on, p.amount from payment p;
        """
    ))
    return render_template('payments.html', payments=payments)

@app.route('/payments-add', methods=["GET", "POST"])
@login_required
def payment_add():
    form = PaymentForm()
    people = list(db.session.execute(
        """
        select s.person_id, concat(p.first_name, ' ', p.last_name) from person p join signer s on s.person_id = p.person_id;
        """
    ))
    form.person_id.choices = [(person_id, name) for person_id, name in people]

    if form.cancel.data:
        return redirect(url_for('payments'))
    if form.validate_on_submit():
        db.session.execute(
            """
            insert into payment (person_id, paid_on, amount)
            values (:person_id, :paid_on, :amount)
            """, {'person_id': form.person_id.data, 'paid_on': form.paid_on.data, 'amount': form.amount.data}
        )
        db.session.commit()
        return redirect(url_for('payments'))
    return render_template('apartment-add.html', form=form)

@app.route('/payment-delete/<payment_id>')
@login_required
def payment_delete(payment_id):
    db.session.execute(
        """
        delete from payment p where p.payment_id = :payment_id;
        """, {'payment_id': payment_id}
    )
    db.session.commit()
    return redirect(url_for('payments'))

@app.route('/leases')
@login_required
def leases():
    leases = list(db.session.execute(
        """
        select concat(p.first_name, ' ', p.last_name), l.monthly_amt, l.expires_on 
        from lease l 
            join person p on p.person_id = l.person_id;
        """
    ))
    return render_template('lease.html', leases=leases)

@app.route('/lease-add', methods=["GET", "POST"])
@login_required
def lease_add():
    form = LeaseForm()
    people = list(db.session.execute(
        """
        select p.person_id, concat(p.first_name, ' ', p.last_name) from person p;
        """
    ))
    form.person_id.choices = [(person_id, name) for person_id, name in people]

    if form.cancel.data:
        return redirect(url_for('leases'))
    if form.validate_on_submit():
        signer = list(db.session.execute(
            """
            select * from signer where person_id = :person_id;
            """, {'person_id': form.person_id.data}
        ))
        if not signer:
            db.session.execute(
                """
                insert into signer (person_id)
                values (:person_id);
                """, {'person_id': form.person_id.data}
            )
            db.session.commit()
        db.session.execute(
            """
            insert into lease (person_id, expires_on, monthly_amt)
            values (:person_id, :expires_on, :monthly_amt)
            """, {'person_id': form.person_id.data, 'expires_on': form.expires_on.data, 'monthly_amt': form.monthly_amt.data}
        )
        db.session.commit()
        return redirect(url_for('leases'))
    return render_template('lease-add.html', form=form)


if __name__ == '__main__':
    app.run()

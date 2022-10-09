from asyncio.windows_events import NULL
import decimal
import re
from flask import Flask, flash, redirect, render_template, request, session, url_for,session
from flask_mysqldb import MySQL

app=Flask(__name__)
app.secret_key="a_a_a_"

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='db_Freemoney'
mysql=MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name=request.form['txtname']
        pat=request.form['txtpat']
        mat=request.form['txtmat']
        phone=request.form['txtphone']
        email=request.form['txtmail']
        pswd=request.form['txtpass']
        sql=mysql.connection.cursor()
        sql.execute("call sp_duplicar_signup('{0}','{1}','{2}','{3}','{4}');".format(name,pat,mat,phone,email))
        data=sql.fetchone()
        if data:
            flash("El usuario que acaba de crear no esta disponible o ya existe.")
            return redirect(url_for('client'))
        else:    
            sql=mysql.connection.cursor()
            sql.execute("call sp_signup('{0}','{1}','{2}','{3}','{4}','{5}');".format(name,pat,mat,phone,email,pswd))
            mysql.connection.commit()
            session['mail']=email
            flash("Bienvenido "+name+", Su cuenta a sido registrada exitosamente.")
            print(session)
            return redirect(url_for("dashboard"))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form['email']
        password=request.form['pswd']
        sql=mysql.connection.cursor()
        sql.execute("call sp_valid_login('{0}','{1}');".format(email,password))
        data=sql.fetchone()
        print(data)
        if data: 
            session['mail']=email
            flash("Bienvenido otra vez a Phoenix.")
            print(session)
            return redirect(url_for("dashboard"))
        else:
            flash(" Usted ingresó un correo o contraseña invalida.")  
            return redirect(url_for("client"))
    else: 
        if 'mail' in session: 
            return redirect(url_for("dashboard"))
        return redirect(url_for("client"))   

@app.route('/logout')
def logout():
    print(session)
    session.clear()
    print(session)
    return redirect(url_for("login"))

@app.route('/dashboard')
def dashboard():
    if 'mail' in session:
        email=session['mail']
        sql=mysql.connection.cursor()
        sql.execute("call sp_recordatorios('{0}');".format(email))
        data=sql.fetchall()
        print(data)
        print(email)
        sql=mysql.connection.cursor()
        sql.execute("call sp_mostrar_cuentas('{0}');".format(email))
        data2=sql.fetchall()
        print(data2)
        print(email)
        sql=mysql.connection.cursor()
        sql.execute("call sp_saldo_total('{0}');".format(email))
        data3=sql.fetchone()
        print(data3)
        print(email)
        return render_template('dashboard.html',data=data,data2=data2,data3=data3,email=email)
    return redirect(url_for('client'))

@app.route('/client')
def client():
    if 'mail' in session:
        return redirect(url_for('dashboard'))
    return render_template('client.html')

@app.route('/operaciones')
def operaciones():
      if 'mail' in session:
          email=session['mail']
          sql=mysql.connection.cursor()
          sql.execute("call sp_movimientos('{0}');".format(email))
          data=sql.fetchall()
          print(data)
          print(email)
          sql=mysql.connection.cursor()
          sql.execute("call sp_mostrar_cuentas('{0}');".format(email))
          data2=sql.fetchall()
          print(data2)
          print(email)
          sql=mysql.connection.cursor()
          sql.execute("call sp_mostrar_beneficiarios();")
          data3=sql.fetchall()
          print(data3)
          print(email)
          return render_template('operaciones.html',data=data,data2=data2,data3=data3,email=email)
      return redirect(url_for('client'))

@app.route('/transferencias')
def transferencias():
    if 'mail' in session:
        email=session['mail']
        sql=mysql.connection.cursor()
        sql.execute("call sp_mostrar_cuentas('{0}');".format(email))
        data=sql.fetchall()
        print(data)
        print(email)
        sql=mysql.connection.cursor()
        sql.execute("call sp_mostrar_trans('{0}');".format(email))
        data2=sql.fetchall()
        print(data2)
        print(email)
        return render_template('transferencias.html',email=email,data=data,data2=data2)
    return redirect(url_for('client'))

@app.route('/insert_trans',methods=['POST'])
def insert_trans():
    if request.method =='POST':
        orig=request.form['origen']
        dest=request.form['destino']
        desc=request.form['descripcion']
        monto=request.form['monto']
        mon=request.form['moneda']
        if mon=='2':
            print(monto)
            monto=float(monto)*3.71
            print(monto)
        else:
            monto=monto
        fech=request.form['fecha']
        sql=mysql.connection.cursor()
        sql.execute("call sp_update_cuenta({0},{1});".format(orig,monto))
        mysql.connection.commit()
        sql=mysql.connection.cursor()
        sql.execute("call sp_insert_trans({0},'{1}','{2}',{3},{4},'{5}');".format(orig, dest, desc, monto, mon,fech))
        mysql.connection.commit()
        flash("Transferencia realizada de manera exitosa.")
        return redirect(url_for('transferencias'))

@app.route('/delete_transferencias/<int:id>')
def delete_transferencias(id):
    sql=mysql.connection.cursor()
    sql.execute("call sp_delete_transferencias({0});".format(id))
    mysql.connection.commit()
    return redirect(url_for('transferencias'))

@app.route('/insert_gasto',methods=['GET','POST'])
def insert_gasto():
    if request.method == 'POST': 
        cat=request.form['categoria']
        fec=request.form['fecha']
        ben=request.form['beneficiario']
        cue=request.form['cuenta']
        nom=request.form['nombre']
        mont=request.form['monto'] 
        mon=request.form['moneda']
        if mon=='2':
            print(mont)
            mont=float(mont)*3.71
            print(mont)
        else:
            mont=mont
        ope=request.form['operacion']
        if ope=='2':
            sql=mysql.connection.cursor()
            sql.execute("call sp_resta_saldo({0},{1});".format(cue,mont))
            mysql.connection.commit()  
        else:
            sql=mysql.connection.cursor()
            sql.execute("call sp_suma_saldo({0},{1});".format(cue,mont))
            mysql.connection.commit()
        sql=mysql.connection.cursor()
        sql.execute("call sp_ingreso_gasto({0},{1},{2},{3},{4},{5},'{6}','{7}');".format(ope,cue,cat,ben,mont,mon,nom,fec))
        mysql.connection.commit()
        flash("Operacion realizada exitosamente.")
        print(ope,cat,fec,ben,mont,mon,nom,cue)
        return redirect(url_for('operaciones'))              
        
@app.route('/delete_movimiento/<int:id>')
def delete_movimiento(id):
    sql=mysql.connection.cursor()
    sql.execute("call sp_delete_movimiento({0});".format(id))
    mysql.connection.commit()
    return redirect(url_for('operaciones'))

@app.route('/recordatorios')
def recordatorios():
    if 'mail' in session:
        email=session['mail']
        sql=mysql.connection.cursor()
        sql.execute("call sp_recordatorios('{0}');".format(email))
        data=sql.fetchall()
        print(data)
        print(email)
        sql=mysql.connection.cursor()
        sql.execute("call sp_mostrar_cuentas('{0}');".format(email))
        data2=sql.fetchall()
        print(data2)
        print(email)
        sql=mysql.connection.cursor()
        sql.execute("call sp_mostrar_beneficiarios();")
        data3=sql.fetchall()
        print(data3)
        print(email)
        return render_template('recordatorios.html',data=data,data2=data2,data3=data3,email=email)
    return redirect(url_for('client'))    

@app.route('/insert_recordatorio',methods=['GET','POST'])
def insert_recordatorio():
    if request.method == 'POST':
        cuen=request.form['cuenta']
        bene=request.form['beneficiario']
        cate=request.form['categoria']
        desc=request.form['descripcion']
        oper=request.form['operacion']
        mont=request.form['monto']
        mone=request.form['moneda']
        if mone=='2':
            print(mont)
            mont=float(mont)*3.71
            print(mont)
        else:
            mont=mont
        pago=request.form['pago']
        frec=request.form['frecuencia']
        noti=request.form['notificacion']
        fech=request.form['fecha']
        sql=mysql.connection.cursor()
        sql.execute("call sp_ingreso_recordatorio({0},{1},{2},{3},{4},{5},{6},{7},'{8}',{9},'{10}');".format(cuen,oper,cate,mont,mone,pago,bene,frec,fech,noti,desc))
        mysql.connection.commit()
        flash('Recordatorio insertado exitosamente.')
        print(cuen,bene,cate,desc,oper,mone,pago,mont,frec,noti,fech,)
        return redirect(url_for('recordatorios'))

@app.route('/delete_recordatorio/<int:id>')
def delete_recordatorio(id):
    sql=mysql.connection.cursor()
    sql.execute("call sp_delete_recordatorio({0});".format(id))
    mysql.connection.commit()
    return redirect(url_for('recordatorios'))

@app.route('/cuentas')
def cuentas():
    if 'mail' in session:
        email = session['mail']
        sql=mysql.connection.cursor()
        sql.execute("call sp_mostrar_cuentas('{0}');".format(email))
        data=sql.fetchall()
        print(data)
        print(email)
        sql=mysql.connection.cursor()
        sql.execute("call sp_call_user('{0}');".format(email))
        data2=sql.fetchone()
        print(data2)
        print(email)
        return render_template('cuentas.html',data=data,data2=data2,email=email)
    return redirect(url_for('client'))    

@app.route('/insert_cuenta',methods=['GET','POST'])
def insert_cuenta():
    if request.method == 'POST':
        user=request.form['user']
        prop=request.form['propietario']
        tar=request.form['tarjeta']
        mes=request.form['mes']
        año=request.form['año']
        cvv=request.form['cvv']
        ban=request.form['banco']
        mont=request.form['monto']
        sql=mysql.connection.cursor()
        sql.execute("call sp_duplicar_cuenta('{0}');".format(tar))
        data=sql.fetchone()
        if data:
            flash('Cuenta con numero de tarjeta existente.','danger')
            return redirect(url_for('cuentas'))
        else: 
            sql=mysql.connection.cursor()
            sql.execute("call sp_ingreso_cuenta({0},'{1}',{2},'{3}','{4}','{5}','{6}',{7});".format(user,prop,ban,tar,mes,año,cvv,mont)) 
            mysql.connection.commit()
            flash("Su cuenta a sido afiliada exitosamente.",'success')
            return redirect(url_for('cuentas'))
    
@app.route('/delete_cuenta/<int:id>')
def delete_cuenta(id):
    sql=mysql.connection.cursor()
    sql.execute("call sp_delete_cuenta({0});".format(id))
    mysql.connection.commit()
    return redirect(url_for('cuentas'))

@app.route('/ajustes')
def ajustes():
    if 'mail' in session:
        email = session['mail']
        sql=mysql.connection.cursor()
        sql.execute("call sp_call_user('{0}');".format(email))
        data=sql.fetchone()
        return render_template('ajustes.html',email=email,data=data)
    return redirect(url_for('client'))

@app.route('/update_user',methods=['GET','POST'])
def update_user():
    if request.method == 'POST':
        id=request.form['id']
        name=request.form['name']
        apat=request.form['apepat']
        amat=request.form['apemat']
        phone=request.form['phone']
        mail=request.form['mail']
        pswd=request.form['pswd']
        sql=mysql.connection.cursor()
        sql.execute("call sp_update_user({0},'{1}','{2}','{3}','{4}','{5}','{6}');".format(id,name,apat,amat,phone,mail,pswd))
        mysql.connection.commit()
        flash("Su cuenta de usuario a sido actualizada de manera exitosa.")
        return redirect(url_for('ajustes'))

if __name__=='__main__':
    app.run(port=3000,debug=True)    
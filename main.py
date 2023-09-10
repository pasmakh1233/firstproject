# app.py
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, Response
from db import get_db_connection, release_db_connection
import pandas as pd
import io
import csv
app = Flask(__name__)
app.secret_key = '123'


@app.route('/')
def landing_page():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()

        cursor = conn.cursor()

        query = "SELECT user_id FROM public.utilisateur WHERE user_name = %s AND user_password = %s"
        cursor.execute(query, (username, password))
        user_id = cursor.fetchone()

        if cursor:
            cursor.close()
        release_db_connection(conn)

        if user_id:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('landing_page'))
    return render_template('dashboard.html')


@app.route('/chart_data1')
def chart_data1():

    conn = get_db_connection()

    cursor = conn.cursor()
    cursor.execute("""select c.descp_profession,d.desc_cat,sum(a.prix_cat)
from collecte as a, client as b , socio_profession as c, public.categorie as d
where b."ID_profession" = c."ID_profession"
and a.identifiant_client = b.identifiant_client
and a."ID_categorie" = d."ID_categorie"
group by c.descp_profession,d.desc_cat""")

    data = cursor.fetchall()
    if cursor:
        cursor.close()
    release_db_connection(conn)
    category_colors = {
        'multimedia': 'rgba(128, 0, 32, 0.2)',
        'alimentaire': 'rgba(0, 35, 102, 0.2)',
        'electronique': 'rgba(0, 102, 71, 0.2)'
    }

    # Extract unique labels for the first and second categories
    labels1 = list(set(item[0] for item in data))
    labels2 = list(set(item[1] for item in data))

    # Initialize an empty dataset dictionary for each unique label in the second category
    datasets = {}
    for label2 in labels2:
        datasets[label2] = {
            'label': label2,
            'data': [],
            # Default color
            'backgroundColor': category_colors.get(label2, 'rgba(75, 192, 192, 0.2)'),
            # Default color
            'borderColor': category_colors.get(label2, 'rgba(75, 192, 192, 1)'),
            'borderWidth': 1
        }

    # Populate the data arrays for each dataset
    for label2 in labels2:
        for label1 in labels1:
            # Find the data item for the current label combination
            item = next(
                (item for item in data if item[0] == label1 and item[1] == label2), None)

            # If the item exists, add its value to the corresponding dataset
            if item:
                datasets[label2]['data'].append(item[2])
            else:
                # If the item doesn't exist for this combination, set a default value (e.g., 0)
                datasets[label2]['data'].append(0)

    chart_data = {
        'labels': labels1,
        'datasets': list(datasets.values())
    }

    return jsonify(chart_data)


@app.route('/chart_data2')
def chart_data2():

    conn = get_db_connection()

    cursor = conn.cursor()
    cursor.execute("""select c.descp_profession,
        avg(prix_panier_total)
    from collecte as a,
        client as b,
        socio_profession as c
    where b."ID_profession" = c."ID_profession"
        and a.identifiant_client = b.identifiant_client
    group by c.descp_profession""")

    data = cursor.fetchall()
    if cursor:
        cursor.close()
    release_db_connection(conn)

    prof = []
    avg = []
    for i, j in data:
        prof.append(i)
        avg.append(j)

    # Replace this with code that retrieves your chart data
    chart_data = {
        "labels": prof,
        "datasets": [
            {
                "label": 'Average cart price',
                "data": avg,
                "backgroundColor": [
                    'rgba(128, 0, 32, 0.2)',
                    'rgba(0, 35, 102, 0.2)',
                    'rgba(0, 102, 71, 0.2)',
                    'rgba(75, 192, 192, 0.2)'
                ],
                "borderColor": [
                    'rgba(128, 0, 32, 0)',
                    'rgba(0, 35, 102, 0.5)',
                    'rgba(0, 102, 71, 0.5)',
                    'rgba(75, 192, 192, 0.5)'
                ],
                "borderWidth": 1
            }
        ]
    }

    return jsonify(chart_data)


@app.route('/generate_excel', methods=['POST'])
def generate_excel():
    try:
        # Get the number from the form
        number = request.form.get('cart_count')

        if number.isdigit():
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM collecte LIMIT {number};")
            data = cursor.fetchall()
            print(data)
            if cursor:
                cursor.close()
            release_db_connection(conn)
            df = pd.DataFrame(data, columns=['identifiant_collecte', 'ID_categorie',
                              'identifiant_client', 'identifiant_panier', 'prix_cat', 'prix_panier_total'])

            csv_data = df.to_csv(index=False)

            # Create a response with CSV data
            response = Response(csv_data, content_type='text/csv')
            response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
            return response

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(df)

        # Set response headers for CSV download
        response = Response(output.getvalue(), content_type='text/csv')
        response.headers["Content-Disposition"] = "attachment; filename=generated_data.csv"
        return response
    except Exception as e:
        return str(e)


@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('landing_page'))


if __name__ == '__main__':
    app.run()

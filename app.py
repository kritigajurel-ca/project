from flask import Flask, render_template, request
from pymysql import connections
import os
import logging
import shutil

app = Flask(__name__)

# =============================
# READ ENVIRONMENT VARIABLES
# =============================
DBHOST = os.environ.get("DBHOST", "localhost")
DBUSER = os.environ.get("DBUSER", "root")
DBPWD = os.environ.get("DBPWD", "password")
DATABASE = os.environ.get("DATABASE", "employees")
DBPORT = int(os.environ.get("DBPORT", 3306))

# GROUP NAME
APP_HEADER = os.environ.get("APP_HEADER", "Group10")

# =============================
# BACKGROUND IMAGE
# =============================
# Path inside the repo (source)
SOURCE_IMAGE_PATH = "static/images/blue-oil-paint-textured-background.jpeg"

# Path inside container (Flask serves /static)
CONTAINER_IMAGE_PATH = "static/images/blue-oil-paint-textured-background.jpeg"

# Make sure the /app/static/images folder exists
os.makedirs("static/images", exist_ok=True)

# Copy the image if it doesn't already exist
if not os.path.exists(CONTAINER_IMAGE_PATH):
    try:
        shutil.copy(SOURCE_IMAGE_PATH, CONTAINER_IMAGE_PATH)
        logging.info(f"Background image copied to {CONTAINER_IMAGE_PATH}")
    except Exception as e:
        logging.error(f"Could not copy background image: {e}")

# Path used in templates
BACKGROUND_IMAGE = "images/blue-oil-paint-textured-background.jpeg"

logging.basicConfig(level=logging.INFO)

# =============================
# DATABASE CONNECTION
# =============================
db_conn = None
try:
    db_conn = connections.Connection(
        host=DBHOST,
        port=DBPORT,
        user=DBUSER,
        password=DBPWD,
        db=DATABASE
    )
    logging.info("Database connected successfully.")
except Exception as e:
    logging.error(f"Database connection failed: {e}")

# =============================
# ROUTES
# =============================
@app.route("/", methods=['GET'])
def home():
    return render_template(
        'addemp.html',
        header=APP_HEADER,
        bg_image_path=BACKGROUND_IMAGE
    )

@app.route("/about", methods=['GET'])
def about():
    return render_template(
        'about.html',
        header=APP_HEADER,
        bg_image_path=BACKGROUND_IMAGE
    )

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form.get('emp_id')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    primary_skill = request.form.get('primary_skill')
    location = request.form.get('location')

    emp_name = f"{first_name} {last_name}"

    if db_conn:
        try:
            insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
            cursor = db_conn.cursor()
            cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
            db_conn.commit()
        except Exception as e:
            logging.error(f"Error inserting employee: {e}")
        finally:
            cursor.close()

    return render_template(
        'addempoutput.html',
        name=emp_name,
        header=APP_HEADER,
        bg_image_path=BACKGROUND_IMAGE
    )

@app.route("/getemp", methods=['GET'])
def GetEmp():
    return render_template(
        "getemp.html",
        header=APP_HEADER,
        bg_image_path=BACKGROUND_IMAGE
    )

@app.route("/fetchdata", methods=['POST'])
def FetchData():
    emp_id = request.form.get('emp_id')
    output = {}

    if db_conn:
        try:
            select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
            cursor = db_conn.cursor()
            cursor.execute(select_sql, (emp_id,))
            result = cursor.fetchone()
            if result:
                output = {
                    "emp_id": result[0],
                    "first_name": result[1],
                    "last_name": result[2],
                    "primary_skills": result[3],
                    "location": result[4]
                }
        except Exception as e:
            logging.error(f"Error fetching employee: {e}")
        finally:
            cursor.close()

    return render_template(
        "getempoutput.html",
        id=output.get("emp_id"),
        fname=output.get("first_name"),
        lname=output.get("last_name"),
        interest=output.get("primary_skills"),
        location=output.get("location"),
        header=APP_HEADER,
        bg_image_path=BACKGROUND_IMAGE
    )

# =============================
# RUN APP
# =============================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)